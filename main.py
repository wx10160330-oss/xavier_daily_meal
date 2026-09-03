"""
兔吃了么 · 每日饮食底稿注入插件

给你的兔子每天生成一份不重样的饮食底稿，被问到吃喝时静默注入 system_prompt。
- 两层生成：LLM（可自选 provider）-> 本地权重池
- 一份统一食物库 foods.json（love / cat / time / weird 四种标签）
- 60% 走"正经搭配"（主食+配菜±汤±甜点），可通过 lazy_ratio 调整
- 剩余走"摆烂"：一顿就一样，制造真实生活感
- 会话隔离 + 可选关键词过滤（默认全场景注入）
- 附带 aiohttp 小网页：查看/重摇/管理食物库
"""

from __future__ import annotations

import asyncio
import json
import random
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, StarTools

try:
    from aiohttp import web
except ImportError:  # pragma: no cover
    web = None  # type: ignore[assignment]

from .foods_default import DEFAULT_FOODS
from .web_assets import ICON_SVG, INDEX_HTML, LOGIN_HTML, MANIFEST_JSON


# ============ 常量 ============

SLOTS = ("breakfast", "lunch", "dinner", "snack")
SLOT_CN = {
    "breakfast": "早",
    "lunch": "午",
    "dinner": "晚",
    "snack": "加",
}
SLOT_TIME_TAG = {
    "breakfast": "早",
    "lunch": "午",
    "dinner": "晚",
    "snack": "加",
}
CATS = ("主食", "配菜", "汤", "甜点", "饮品")

HISTORY_FILE = "history.json"
FOODS_FILE = "foods.json"

DEFAULT_SNIPPET_TEMPLATE = (
    "[今日吃食] {menu}"
    "（被问到时自然带出，别主动罗列、别复读；"
    "请结合当前时间判断该聊哪一顿：还没吃就说打算吃，吃过了就说吃过了）"
)

LOVE_WEIGHT = {2: 5.0, 1: 2.0, 0: 0.5}
TIME_MATCH_MULT = 1.8
TIME_MISS_MULT = 0.35

LLM_MENU_PROMPT_TEMPLATE = (
    "给他排一份今天的饮食（早/午/晚/加餐）。要求：\n"
    "1. 早/午/晚各 1 项，加餐 1 项（不需要就给空字符串）。\n"
    "2. 追求真实生活感，街边小吃 / 家常菜 / 精致小食都可以，"
    "避免连锁快餐凑数。\n"
    "3. 他是重度肉食+嗜甜口味，喜辣，也偶尔会来点清奇怪味。\n"
    "4. 今天是 {today}，节气/时令：{season_hint}，可以适当贴合。\n"
    "5. 避开最近吃过的：{recent}\n"
    "6. 只返回一个严格 JSON 对象，键为 breakfast/lunch/dinner/snack，"
    "值为菜名字符串（可以是一顿的多样搭配，用 + 连接），"
    "不要任何多余文字、不要 markdown 代码块围栏。\n"
    '示例：{{"breakfast":"煎饼果子+豆浆","lunch":"红烧肉+白粥+冬瓜排骨汤",'
    '"dinner":"麻辣香锅","snack":"焦糖蛋挞"}}'
)


class XavierDailyMeal(Star):
    def __init__(self, context: Context, config: dict | None = None) -> None:
        super().__init__(context)
        self.config: dict = config or {}
        self.name = "xavier_daily_meal"

        self._data_dir: Path | None = None
        self._history_lock = asyncio.Lock()
        self._foods_lock = asyncio.Lock()

        self._web_runner: Any = None
        self._web_site: Any = None

    # ---------- 生命周期 ----------

    async def initialize(self) -> None:
        try:
            self._data_dir = StarTools.get_data_dir("xavier_daily_meal")
        except Exception:
            logger.exception("[兔吃了么] 获取数据目录失败")
            self._data_dir = None

        await self._ensure_default_foods()

        if self.config.get("web_enable", True):
            await self._start_web()

        logger.info("[兔吃了么] 插件已启动")

    async def terminate(self) -> None:
        await self._stop_web()
        logger.info("[兔吃了么] 已关闭")

    # ---------- 会话隔离 ----------

    async def _check_enabled_async(self, event: AstrMessageEvent) -> bool:
        try:
            from astrbot.core.star.session_plugin_manager import (
                SessionPluginManager,
            )
            return await SessionPluginManager.is_plugin_enabled_for_session(
                session_id=event.unified_msg_origin,
                plugin_name=self.name,
            )
        except Exception:
            logger.exception("[兔吃了么] 会话状态检查失败，默认放行")
            return True

    # ---------- LLM Hook ----------

    @filter.on_llm_request()
    async def on_llm_request(
        self, event: AstrMessageEvent, req: ProviderRequest,
    ) -> None:
        try:
            if not self.config.get("enable_inject", True):
                return
            if not await self._check_enabled_async(event):
                return

            user_msg = (event.message_str or req.prompt or "").strip()
            keywords = self.config.get("trigger_keywords") or []
            if keywords and not self._hit_keyword(user_msg, keywords):
                return

            menu = await self._get_today_menu(event)
            if not menu:
                return
            snippet = self._compose_snippet(menu)
            if not snippet:
                return
            req.system_prompt = (req.system_prompt or "") + "\n" + snippet
        except Exception:
            logger.exception("[兔吃了么] 注入失败，安全回退")

    @staticmethod
    def _hit_keyword(text: str, keywords: list[str]) -> bool:
        if not text or not keywords:
            return False
        return any(kw and kw in text for kw in keywords)

    # ---------- 菜单获取 ----------

    async def _get_today_menu(
        self, event: AstrMessageEvent | None,
    ) -> dict[str, str] | None:
        today = date.today().isoformat()
        history = await self._load_history()
        cached = history.get(today)
        if cached and any(cached.get(s) for s in SLOTS):
            return cached

        menu = None
        # 兼容配置：如果关了 use_llm_gen 视作 0 概率，否则读 llm_ratio (0.0~1.0，默认 1.0)
        use_llm = bool(self.config.get("use_llm_gen", True))
        try:
            llm_ratio = float(self.config.get("llm_ratio", 1.0) if use_llm else 0.0)
        except (ValueError, TypeError):
            llm_ratio = 1.0 if use_llm else 0.0

        if llm_ratio > 0 and event is not None:
            # 每天根据日期种子掷骰子，确保同一天内重试判断一致
            dice = (self._daily_seed() % 10000) / 10000.0
            if dice < llm_ratio:
                try:
                    menu = await self._llm_generate(event, history)
                except Exception:
                    logger.exception("[兔吃了么] LLM 生成失败，回退本地池")

        if not menu:
            menu = await self._local_generate(history)

        if not menu:
            return None

        history[today] = menu
        history = self._trim_history(history)
        await self._save_history(history)
        return menu

    # ---------- LLM 生成 ----------

    def _pick_provider(self, event: AstrMessageEvent):
        """按配置选 provider：指定了 id 就用指定的，否则用会话默认。"""
        pid = str(self.config.get("llm_provider_id") or "").strip()
        try:
            if pid:
                p = self.context.get_provider_by_id(pid)
                if p is None:
                    logger.warning(
                        "[兔吃了么] 找不到 provider_id=%s，回退默认", pid,
                    )
                else:
                    return p
            return self.context.get_using_provider(
                umo=event.unified_msg_origin,
            )
        except Exception:
            logger.exception("[兔吃了么] 获取 provider 失败")
            return None

    async def _llm_generate(
        self,
        event: AstrMessageEvent,
        history: dict[str, dict[str, str]],
    ) -> dict[str, str] | None:
        provider = self._pick_provider(event)
        if provider is None:
            return None

        today = date.today().isoformat()
        recent = self._collect_recent_dishes(history, days=7)
        season_hint = self._season_hint()

        tpl = str(self.config.get("gen_prompt_template") or "").strip()
        if not tpl:
            tpl = LLM_MENU_PROMPT_TEMPLATE
        try:
            prompt = tpl.format(
                today=today,
                season_hint=season_hint,
                recent=("、".join(recent) if recent else "无"),
            )
        except Exception:
            logger.exception("[兔吃了么] 生成 prompt 渲染失败，回退默认")
            prompt = LLM_MENU_PROMPT_TEMPLATE.format(
                today=today,
                season_hint=season_hint,
                recent=("、".join(recent) if recent else "无"),
            )

        sys_prompt = str(self.config.get("gen_system_prompt") or "").strip()
        if not sys_prompt:
            sys_prompt = (
                "你是一个菜单助手。只返回严格 JSON，"
                "不要解释、不要 markdown 代码块。"
            )

        try:
            resp = await asyncio.wait_for(
                provider.text_chat(
                    prompt=prompt,
                    contexts=[],
                    system_prompt=sys_prompt,
                ),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            logger.warning("[兔吃了么] LLM 生成超时")
            return None

        text = (resp.completion_text or "").strip()
        if not text:
            return None
        menu = self._parse_json_menu(text)
        if not menu:
            logger.warning("[兔吃了么] LLM 返回无法解析: %s", text[:200])
        return menu

    @staticmethod
    def _parse_json_menu(text: str) -> dict[str, str] | None:
        text = text.strip()
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            if not isinstance(obj, dict):
                return None
            out: dict[str, str] = {}
            for k in SLOTS:
                v = obj.get(k, "")
                out[k] = str(v).strip() if v is not None else ""
            return out
        except Exception:
            return None

    @staticmethod
    def _season_hint() -> str:
        m = date.today().month
        if m in (12, 1, 2):
            return "冬季，天冷，适合热汤/暖胃"
        if m in (3, 4, 5):
            return "春季，回暖，清爽为主"
        if m in (6, 7, 8):
            return "夏季，炎热，可以清淡/凉面/凉皮/酸梅汤"
        return "秋季，处暑立秋前后，微凉，可温润"

    # ---------- 本地权重池生成 ----------

    async def _local_generate(
        self,
        history: dict[str, dict[str, str]],
    ) -> dict[str, str]:
        foods = await self._load_foods()
        if not foods:
            return {s: "" for s in SLOTS}

        recent = set(self._collect_recent_dishes(history, days=7))
        rng = random.Random(self._daily_seed())

        lazy_ratio = float(self.config.get("lazy_ratio", 0.4) or 0.0)
        weird_ratio = float(self.config.get("weird_ratio", 0.1) or 0.0)
        include_snack = bool(self.config.get("include_snack", True))

        menu: dict[str, str] = {}
        used: set[str] = set(recent)

        for slot in SLOTS:
            if slot == "snack":
                if not include_snack or rng.random() > 0.55:
                    menu[slot] = ""
                    continue
                # 加餐：只出一样，主要来自甜点/饮品/加餐主食
                dish = self._pick_snack(foods, slot, used, weird_ratio, rng)
                menu[slot] = dish
                if dish:
                    used.add(dish)
                continue

            # 正餐：决定摆烂还是搭配
            if rng.random() < lazy_ratio:
                # 摆烂：一样菜
                dish = self._pick_one_lazy(foods, slot, used, weird_ratio, rng)
                menu[slot] = dish
                if dish:
                    used.add(dish)
            else:
                # 正经搭配：主食 + 配菜 (+ 30% 汤/甜点)
                combo = self._pick_combo(foods, slot, used, weird_ratio, rng)
                menu[slot] = combo
                for part in combo.split("+"):
                    part = part.strip()
                    if part:
                        used.add(part)
        return menu

    def _daily_seed(self) -> int:
        import hashlib
        raw = date.today().isoformat().encode("utf-8")
        return int(hashlib.md5(raw).hexdigest()[:8], 16)

    def _weight(self, food: dict, slot_tag: str, weird_ratio: float) -> float:
        base = LOVE_WEIGHT.get(int(food.get("love", 1)), 1.0)
        tags = food.get("time") or []
        if tags:
            base = base * (TIME_MATCH_MULT if slot_tag in tags else TIME_MISS_MULT)
        if food.get("weird"):
            # 怪味按 weird_ratio 参与，不参与时权重≈0
            base = base * max(weird_ratio, 0.0)
        return base

    def _weighted_pick(
        self,
        candidates: list[dict],
        slot_tag: str,
        used: set[str],
        weird_ratio: float,
        rng: random.Random,
    ) -> str:
        pool = [f for f in candidates if f.get("name") and f["name"] not in used]
        if not pool:
            pool = candidates  # 全用过了就允许重复
        weights = [max(self._weight(f, slot_tag, weird_ratio), 0.0001) for f in pool]
        try:
            picked = rng.choices(pool, weights=weights, k=1)[0]
            return str(picked.get("name") or "")
        except Exception:
            return ""

    def _pick_one_lazy(
        self,
        foods: list[dict],
        slot: str,
        used: set[str],
        weird_ratio: float,
        rng: random.Random,
    ) -> str:
        """摆烂模式：早餐偏主食，午晚可以主食/配菜/汤单挑一样。"""
        slot_tag = SLOT_TIME_TAG[slot]
        if slot == "breakfast":
            cats = ["主食"]
        else:
            cats = ["主食", "配菜"]
        cand = [f for f in foods if f.get("cat") in cats]
        return self._weighted_pick(cand, slot_tag, used, weird_ratio, rng)

    def _pick_snack(
        self,
        foods: list[dict],
        slot: str,
        used: set[str],
        weird_ratio: float,
        rng: random.Random,
    ) -> str:
        slot_tag = SLOT_TIME_TAG[slot]
        cand = [f for f in foods if f.get("cat") in ("甜点", "饮品", "主食")]
        return self._weighted_pick(cand, slot_tag, used, weird_ratio, rng)

    def _pick_combo(
        self,
        foods: list[dict],
        slot: str,
        used: set[str],
        weird_ratio: float,
        rng: random.Random,
    ) -> str:
        """正经搭配：主食 + 配菜（+ 30% 汤 / 20% 甜点）"""
        slot_tag = SLOT_TIME_TAG[slot]
        parts: list[str] = []
        local_used = set(used)

        # 主食
        staple = [f for f in foods if f.get("cat") == "主食"]
        s = self._weighted_pick(staple, slot_tag, local_used, weird_ratio, rng)
        if s:
            parts.append(s)
            local_used.add(s)

        # 配菜 1~2 样
        n_side = rng.choices([1, 2], weights=[0.55, 0.45], k=1)[0]
        side = [f for f in foods if f.get("cat") == "配菜"]
        for _ in range(n_side):
            d = self._weighted_pick(side, slot_tag, local_used, weird_ratio, rng)
            if d:
                parts.append(d)
                local_used.add(d)

        # 30% 汤
        if slot in ("lunch", "dinner") and rng.random() < 0.3:
            soup = [f for f in foods if f.get("cat") == "汤"]
            d = self._weighted_pick(soup, slot_tag, local_used, weird_ratio, rng)
            if d:
                parts.append(d)
                local_used.add(d)

        # 早餐 40% 概率带饮品
        if slot == "breakfast" and rng.random() < 0.4:
            drink = [f for f in foods if f.get("cat") == "饮品"]
            d = self._weighted_pick(drink, slot_tag, local_used, weird_ratio, rng)
            if d:
                parts.append(d)
                local_used.add(d)

        return "+".join(p for p in parts if p)

    # ---------- 注入片段 ----------

    def _compose_snippet(self, menu: dict[str, str]) -> str:
        b = menu.get("breakfast") or ""
        l = menu.get("lunch") or ""
        d = menu.get("dinner") or ""
        s = menu.get("snack") or ""

        parts: list[str] = []
        if b: parts.append(f"早 {b}")
        if l: parts.append(f"午 {l}")
        if d: parts.append(f"晚 {d}")
        if s: parts.append(f"想吃 {s}")

        if not parts:
            return ""
        joined = " ｜ ".join(parts)

        tpl = str(self.config.get("snippet_template") or "").strip()
        if not tpl:
            tpl = DEFAULT_SNIPPET_TEMPLATE

        try:
            return tpl.format(
                menu=joined,
                breakfast=b or "（无）",
                lunch=l or "（无）",
                dinner=d or "（无）",
                snack=s or "（无）",
            )
        except Exception:
            logger.exception("[兔吃了么] 模板渲染失败，回退默认")
            return DEFAULT_SNIPPET_TEMPLATE.format(
                menu=joined,
                breakfast=b or "（无）",
                lunch=l or "（无）",
                dinner=d or "（无）",
                snack=s or "（无）",
            )

    # ---------- 历史读写 ----------

    def _history_path(self) -> Path | None:
        if self._data_dir is None:
            return None
        return self._data_dir / HISTORY_FILE

    async def _load_history(self) -> dict[str, dict[str, str]]:
        async with self._history_lock:
            return await asyncio.to_thread(self._load_history_sync)

    def _load_history_sync(self) -> dict[str, dict[str, str]]:
        p = self._history_path()
        if not p or not p.exists():
            return {}
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            logger.exception("[兔吃了么] 读取 history.json 失败")
        return {}

    async def _save_history(self, data: dict[str, dict[str, str]]) -> None:
        async with self._history_lock:
            await asyncio.to_thread(self._save_history_sync, data)

    def _save_history_sync(self, data: dict[str, dict[str, str]]) -> None:
        p = self._history_path()
        if not p:
            return
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("[兔吃了么] 写入 history.json 失败")

    def _trim_history(
        self, data: dict[str, dict[str, str]],
    ) -> dict[str, dict[str, str]]:
        keep = max(int(self.config.get("dedup_days", 7) or 7) * 2, 14)
        try:
            items = sorted(data.items(), key=lambda kv: kv[0], reverse=True)
            return dict(items[:keep])
        except Exception:
            return data

    def _collect_recent_dishes(
        self, history: dict[str, dict[str, str]], days: int,
    ) -> list[str]:
        try:
            items = sorted(history.items(), key=lambda kv: kv[0], reverse=True)
            recent: list[str] = []
            for _, menu in items[:days]:
                for k in SLOTS:
                    v = (menu or {}).get(k) or ""
                    if not v:
                        continue
                    for part in v.split("+"):
                        part = part.strip()
                        if part:
                            recent.append(part)
            return recent
        except Exception:
            return []

    # ---------- 食物库读写 ----------

    def _foods_path(self) -> Path | None:
        if self._data_dir is None:
            return None
        return self._data_dir / FOODS_FILE

    async def _ensure_default_foods(self) -> None:
        p = self._foods_path()
        if not p:
            return
        if p.exists():
            return
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w", encoding="utf-8") as f:
                json.dump(DEFAULT_FOODS, f, ensure_ascii=False, indent=2)
            logger.info("[兔吃了么] 已写入默认食物库: %s", p)
        except Exception:
            logger.exception("[兔吃了么] 写入默认食物库失败")

    async def _load_foods(self) -> list[dict]:
        async with self._foods_lock:
            return await asyncio.to_thread(self._load_foods_sync)

    def _load_foods_sync(self) -> list[dict]:
        p = self._foods_path()
        if not p or not p.exists():
            return list(DEFAULT_FOODS)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [self._normalize_food(x) for x in data if isinstance(x, dict)]
        except Exception:
            logger.exception("[兔吃了么] 读取 foods.json 失败")
        return list(DEFAULT_FOODS)

    @staticmethod
    def _normalize_food(f: dict) -> dict:
        return {
            "name": str(f.get("name", "")).strip(),
            "love": int(f.get("love", 1)) if str(f.get("love", "")).strip() != "" else 1,
            "cat": str(f.get("cat", "配菜")).strip() or "配菜",
            "time": [str(t) for t in (f.get("time") or []) if str(t).strip()],
            "weird": bool(f.get("weird", False)),
        }

    async def _save_foods(self, data: list[dict]) -> None:
        async with self._foods_lock:
            await asyncio.to_thread(self._save_foods_sync, data)

    def _save_foods_sync(self, data: list[dict]) -> None:
        p = self._foods_path()
        if not p:
            return
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("[兔吃了么] 写入 foods.json 失败")

    # ============ 小网页 (aiohttp) ============

    async def _start_web(self) -> None:
        if web is None:
            logger.warning("[兔吃了么] 未安装 aiohttp，跳过 web 启动")
            return

        host = str(self.config.get("web_host", "127.0.0.1") or "127.0.0.1")
        port = int(self.config.get("web_port", 17334) or 17334)
        token = str(self.config.get("web_token", "") or "").strip()

        if host not in ("127.0.0.1", "localhost") and not token:
            logger.warning(
                "[兔吃了么] 监听 %s 但未设置 web_token，任何人可访问，"
                "强烈建议在配置里填一个复杂 token", host,
            )

        app = web.Application(middlewares=[self._auth_middleware(token)])
        app.router.add_get("/", self._h_index)
        app.router.add_get("/favicon.svg", self._h_favicon)
        app.router.add_get("/favicon.ico", self._h_favicon)
        app.router.add_get("/manifest.webmanifest", self._h_manifest)
        app.router.add_get("/login", self._h_login_page)
        app.router.add_post("/login", self._h_login_submit)
        app.router.add_get("/logout", self._h_logout)
        app.router.add_get("/api/today", self._h_today)
        app.router.add_get("/api/history", self._h_history)
        app.router.add_post("/api/reroll", self._h_reroll)
        app.router.add_get("/api/foods", self._h_foods_list)
        app.router.add_post("/api/foods", self._h_foods_save)

        try:
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=host, port=port)
            await site.start()
            self._web_runner = runner
            self._web_site = site
            logger.info(
                "[兔吃了么] 小网页: http://%s:%s%s",
                host, port, (" (需 token)" if token else ""),
            )
        except Exception:
            logger.exception("[兔吃了么] 启动小网页失败")
            self._web_runner = None
            self._web_site = None

    def _auth_middleware(self, token: str):
        PUBLIC_PATHS = {"/login", "/favicon.svg", "/favicon.ico", "/manifest.webmanifest"}
        COOKIE_NAME = "tuchile_token"

        @web.middleware
        async def _mw(request, handler):
            if not token:
                return await handler(request)
            if request.path in PUBLIC_PATHS:
                return await handler(request)
            supplied = (
                request.cookies.get(COOKIE_NAME)
                or request.query.get("token")
                or request.headers.get("X-Token") or ""
            )
            if supplied != token:
                if request.method == "GET" and not request.path.startswith("/api/"):
                    return web.HTTPFound("/login")
                return web.json_response(
                    {"ok": False, "err": "unauthorized"}, status=401,
                )
            return await handler(request)
        return _mw

    async def _h_favicon(self, request: Any) -> Any:
        return web.Response(text=ICON_SVG, content_type="image/svg+xml")

    async def _h_manifest(self, request: Any) -> Any:
        return web.Response(text=MANIFEST_JSON, content_type="application/manifest+json")

    async def _h_login_page(self, request: Any) -> Any:
        err = request.query.get("err")
        err_block = '<div class="err">密码不对哦</div>' if err == "1" else ""
        html = LOGIN_HTML.replace("{err_html}", err_block)
        return web.Response(text=html, content_type="text/html")

    async def _h_login_submit(self, request: Any) -> Any:
        token = str(self.config.get("web_token", "") or "").strip()
        try:
            data = await request.post()
            pw = str(data.get("token") or data.get("password") or "").strip()
        except Exception:
            pw = ""
        if not token or pw != token:
            return web.HTTPFound("/login?err=1")
        resp = web.HTTPFound("/")
        resp.set_cookie(
            "tuchile_token", token,
            max_age=30 * 86400,
            httponly=True,
            samesite="Lax",
            path="/",
        )
        return resp

    async def _h_logout(self, request: Any) -> Any:
        resp = web.HTTPFound("/login")
        resp.del_cookie("tuchile_token")
        return resp

    async def _stop_web(self) -> None:
        try:
            if self._web_site is not None:
                await self._web_site.stop()
        except Exception:
            logger.exception("[兔吃了么] 关闭 site 失败")
        try:
            if self._web_runner is not None:
                await self._web_runner.cleanup()
        except Exception:
            logger.exception("[兔吃了么] 清理 runner 失败")
        self._web_site = None
        self._web_runner = None

    async def _h_index(self, request: Any) -> Any:
        return web.Response(
            text=INDEX_HTML,
            content_type="text/html",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )

    async def _h_today(self, request: Any) -> Any:
        today = date.today().isoformat()
        history = await self._load_history()
        menu = history.get(today) or {}
        return web.json_response({
            "date": today, "menu": menu,
            "snippet": self._compose_snippet(menu),
        })

    async def _h_history(self, request: Any) -> Any:
        history = await self._load_history()
        try:
            days = int(request.query.get("days", "7"))
        except ValueError:
            days = 7
        items = sorted(history.items(), key=lambda kv: kv[0], reverse=True)
        return web.json_response({"history": items[:days]})

    async def _h_reroll(self, request: Any) -> Any:
        try:
            body = await request.json()
        except Exception:
            body = {}
        slot = body.get("slot") if isinstance(body, dict) else None

        history = await self._load_history()
        today = date.today().isoformat()
        current = dict(history.get(today) or {})

        # 用本地生成器重出，避开当前已用
        foods = await self._load_foods()
        rng = random.Random()
        recent = set(self._collect_recent_dishes(history, days=7))
        for v in current.values():
            for part in (v or "").split("+"):
                part = part.strip()
                if part:
                    recent.add(part)
        weird_ratio = float(self.config.get("weird_ratio", 0.1) or 0.0)
        lazy_ratio = float(self.config.get("lazy_ratio", 0.4) or 0.0)

        def gen_slot(s: str) -> str:
            if s == "snack":
                if not self.config.get("include_snack", True):
                    return ""
                return self._pick_snack(foods, s, recent, weird_ratio, rng)
            if rng.random() < lazy_ratio:
                return self._pick_one_lazy(foods, s, recent, weird_ratio, rng)
            return self._pick_combo(foods, s, recent, weird_ratio, rng)

        if slot in SLOTS:
            current[slot] = gen_slot(slot)
        else:
            for s in SLOTS:
                current[s] = gen_slot(s)

        history[today] = current
        history = self._trim_history(history)
        await self._save_history(history)
        return web.json_response({"ok": True, "menu": current})

    async def _h_foods_list(self, request: Any) -> Any:
        foods = await self._load_foods()
        return web.json_response({"foods": foods})

    async def _h_foods_save(self, request: Any) -> Any:
        try:
            body = await request.json()
        except Exception:
            body = None
        if not isinstance(body, dict) or not isinstance(body.get("foods"), list):
            return web.json_response(
                {"ok": False, "err": "invalid body"}, status=400,
            )
        cleaned: list[dict] = []
        seen: set[str] = set()
        for item in body["foods"]:
            if not isinstance(item, dict):
                continue
            f = self._normalize_food(item)
            if not f["name"] or f["name"] in seen:
                continue
            if f["cat"] not in CATS:
                f["cat"] = "配菜"
            if f["love"] not in (0, 1, 2):
                f["love"] = 1
            seen.add(f["name"])
            cleaned.append(f)
        await self._save_foods(cleaned)
        return web.json_response({"ok": True, "count": len(cleaned)})
