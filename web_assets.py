"""内联的 HTML 页面和图标资产。放这里免得 main.py 太长。"""

from __future__ import annotations


# 趴在饭碗上的小兔子 SVG 图标，适配桌面大图和小尺寸 favicon
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fff5f7"/>
      <stop offset="100%" stop-color="#ffe1ea"/>
    </linearGradient>
    <linearGradient id="earGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffb3c6"/>
      <stop offset="100%" stop-color="#ff8da9"/>
    </linearGradient>
    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#fff0f4"/>
    </linearGradient>
    <linearGradient id="bowlGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ff9eb9"/>
      <stop offset="100%" stop-color="#ff7aa2"/>
    </linearGradient>
  </defs>

  <!-- 柔和圆角背景底板（手机加桌面时好看） -->
  <rect width="512" height="512" rx="115" fill="url(#bgGrad)"/>

  <!-- 饭碗上方的热气小爱心 -->
  <g opacity="0.65">
    <path d="M170 120 C170 108 178 100 188 100 C194 100 199 104 202 109 C205 104 210 100 216 100 C226 100 234 108 234 120 C234 136 202 152 202 152 C202 152 170 136 170 120 Z" fill="#ff9eb9" transform="scale(0.85) translate(30, 20)"/>
    <path d="M320 95 C320 85 327 78 335 78 C340 78 344 81 347 85 C350 81 354 78 359 78 C367 78 374 85 374 95 C374 108 347 122 347 122 C347 122 320 108 320 95 Z" fill="#ffb3c6"/>
  </g>

  <!-- 左耳外侧 -->
  <ellipse cx="190" cy="165" rx="36" ry="105" transform="rotate(-16 190 165)" fill="url(#bodyGrad)"/>
  <!-- 左耳内侧 -->
  <ellipse cx="190" cy="165" rx="20" ry="80" transform="rotate(-16 190 165)" fill="url(#earGrad)"/>

  <!-- 右耳外侧 -->
  <ellipse cx="322" cy="165" rx="36" ry="105" transform="rotate(16 322 165)" fill="url(#bodyGrad)"/>
  <!-- 右耳内侧 -->
  <ellipse cx="322" cy="165" rx="20" ry="80" transform="rotate(16 322 165)" fill="url(#earGrad)"/>

  <!-- 兔头大轮廓 -->
  <ellipse cx="256" cy="270" rx="130" ry="115" fill="url(#bodyGrad)"/>

  <!-- 呆毛 -->
  <path d="M256 170 Q264 145 258 135 Q250 155 250 168 Z" fill="#ffffff"/>

  <!-- 腮红 -->
  <ellipse cx="172" cy="285" rx="22" ry="13" fill="#ff91aa" opacity="0.6"/>
  <ellipse cx="340" cy="285" rx="22" ry="13" fill="#ff91aa" opacity="0.6"/>

  <!-- 眼睛（亮晶晶的大眼睛） -->
  <ellipse cx="195" cy="245" rx="13" ry="16" fill="#372830"/>
  <circle cx="191" cy="239" r="5.5" fill="#ffffff"/>
  <circle cx="199" cy="249" r="2.5" fill="#ffffff"/>

  <ellipse cx="317" cy="245" rx="13" ry="16" fill="#372830"/>
  <circle cx="313" cy="239" r="5.5" fill="#ffffff"/>
  <circle cx="321" cy="249" r="2.5" fill="#ffffff"/>

  <!-- 鼻子 -->
  <path d="M251 265 L261 265 L256 271 Z" fill="#ff7aa2"/>

  <!-- 嘴巴（小兔三瓣嘴） -->
  <path d="M256 271 Q247 279 240 276 M256 271 Q265 279 272 276" stroke="#4b3b46" stroke-width="3.5" stroke-linecap="round" fill="none"/>

  <!-- 碗口冒出的白米饭弧度 -->
  <ellipse cx="256" cy="305" rx="155" ry="30" fill="#fffaf5"/>

  <!-- 饭碗主体 -->
  <path d="M92 305 Q120 440 256 440 Q392 440 420 305 Z" fill="url(#bowlGrad)"/>
  <!-- 碗底圈足 -->
  <rect x="200" y="435" width="112" height="18" rx="8" fill="#ff6b95"/>

  <!-- 碗口立体边沿 -->
  <ellipse cx="256" cy="305" rx="168" ry="18" fill="#fff5f8" opacity="0.9"/>
  <ellipse cx="256" cy="305" rx="160" ry="13" fill="#ffb3c6" opacity="0.4"/>

  <!-- 碗身中央的小星星 -->
  <polygon points="256,360 263,376 280,378 267,390 271,407 256,398 241,407 245,390 232,378 249,376" fill="#ffffff" opacity="0.9"/>

  <!-- 两只趴在碗沿上的小爪子 -->
  <ellipse cx="165" cy="305" rx="20" ry="16" fill="#ffffff" stroke="#ffd0dc" stroke-width="2"/>
  <path d="M160 308 L160 316 M170 308 L170 316" stroke="#ffb3c6" stroke-width="2" stroke-linecap="round"/>

  <ellipse cx="347" cy="305" rx="20" ry="16" fill="#ffffff" stroke="#ffd0dc" stroke-width="2"/>
  <path d="M342 308 L342 316 M352 308 L352 316" stroke="#ffb3c6" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


MANIFEST_JSON = """{
  "name": "兔吃了么",
  "short_name": "兔吃了么",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#fff5f7",
  "theme_color": "#ff7aa2",
  "icons": [
    {
      "src": "/favicon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
"""


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"/>
<title>兔吃了么</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
<link rel="apple-touch-icon" href="/favicon.svg"/>
<link rel="manifest" href="/manifest.webmanifest"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="default"/>
<meta name="apple-mobile-web-app-title" content="兔吃了么"/>
<meta name="theme-color" content="#ff7aa2"/>
<style>
  :root {
    --bg:#fff5f7; --card:#fff; --pink:#ffb3c6; --pink-deep:#ff7aa2;
    --text:#4b3b46; --muted:#a08b95; --line:#ffe3ea;
  }
  *{box-sizing:border-box;}
  body{margin:0;padding:20px;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;}
  header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px;}
  .brand{display:flex;align-items:center;gap:10px;}
  .brand-icon{width:36px;height:36px;border-radius:10px;box-shadow:0 2px 6px rgba(255,122,162,.2);flex-shrink:0;}
  h1{font-size:20px;margin:0;} .sub{color:var(--muted);font-size:12px;margin-top:2px;}
  .tabs{display:flex;gap:6px;margin-bottom:16px;}
  .tab{padding:6px 14px;border:1px solid var(--line);border-radius:20px;background:#fff;cursor:pointer;font-size:13px;color:var(--muted);transition:all .15s ease;}
  .tab.active{background:var(--pink-deep);color:#fff;border-color:var(--pink-deep);}
  .page{display:none;} .page.active{display:block;}
  .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin-bottom:16px;}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:0 2px 8px rgba(255,122,162,.06);position:relative;}
  .card h3{margin:0 0 6px 0;font-size:13px;color:var(--pink-deep);}
  .card .items{font-size:15px;font-weight:500;min-height:36px;display:flex;align-items:center;}
  .card .empty{color:var(--muted);font-weight:normal;font-size:13px;}
  .card button.reroll{position:absolute;top:10px;right:10px;background:none;border:none;cursor:pointer;font-size:15px;padding:4px;border-radius:6px;transition:transform .2s;}
  .card button.reroll:hover{transform:rotate(45deg);background:var(--bg);}
  .actions{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;}
  .btn{background:var(--pink-deep);color:#fff;border:none;border-radius:10px;padding:8px 16px;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:opacity .15s;}
  .btn:hover{opacity:0.9;}
  .btn-outline{background:#fff;color:var(--pink-deep);border:1px solid var(--pink-deep);}
  .preview-box{background:var(--card);border:1px dashed var(--line);border-radius:12px;padding:12px;font-size:12px;color:var(--muted);white-space:pre-wrap;font-family:ui-monospace,Menlo,monospace;}
  .history-item{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:10px;}
  .history-date{font-weight:bold;color:var(--pink-deep);margin-bottom:4px;font-size:13px;}
  .history-content{font-size:13px;color:var(--text);}
  .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:8px 16px;border-radius:20px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none;z-index:999;}
  .toast.show{opacity:0.9;}

  /* 食物库表格与控件 */
  .toolbar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center;}
  .search-input{padding:6px 12px;border:1px solid var(--line);border-radius:8px;font-size:13px;outline:none;background:#fff;color:var(--text);}
  .filter-select{padding:6px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:#fff;color:var(--text);}
  .table-wrapper{background:#fff;border:1px solid var(--line);border-radius:12px;overflow-x:auto;overflow-y:auto;max-height:600px;-webkit-overflow-scrolling:touch;}
  table{width:100%;min-width:600px;border-collapse:collapse;font-size:13px;}
  th,td{padding:10px 8px;text-align:left;border-bottom:1px solid var(--line);vertical-align:middle;}
  th{background:#fff8fa;color:var(--pink-deep);position:sticky;top:0;z-index:2;font-weight:600;}
  tr:hover{background:#fffbfd;}
  .in-name{width:100%;min-width:130px;padding:6px 8px;border:1px solid var(--line);border-radius:6px;font-size:14px;color:#2c2027;background:#fff;font-weight:500;}
  .in-name:focus{outline:none;border-color:var(--pink-deep);box-shadow:0 0 0 2px rgba(255,122,162,0.2);}
  .in-select{padding:6px 6px;border:1px solid var(--line);border-radius:6px;font-size:13px;background:#fff;color:var(--text);}
  .time-chips{display:flex;gap:4px;flex-wrap:nowrap;}
  .time-chip{padding:3px 7px;border-radius:4px;font-size:11px;cursor:pointer;user-select:none;border:1px solid var(--line);background:#fff;color:var(--muted);transition:all .15s;}
  .time-chip.active{background:var(--pink-deep);color:#fff;border-color:var(--pink-deep);font-weight:bold;}
  .del-btn{background:none;border:none;cursor:pointer;color:#d88;font-size:15px;padding:4px 8px;border-radius:4px;}
  .del-btn:hover{background:#ffe3ea;color:#b33;}
  .save-bar{margin-top:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
  .badge-count{color:var(--muted);font-size:12px;}

  @media (max-width: 600px) {
    body{padding:12px;}
    .table-wrapper{border-radius:8px;}
    table{font-size:12px;}
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <img class="brand-icon" src="/favicon.svg" alt="🐰"/>
    <div>
      <h1>🐰 兔吃了么</h1>
      <div class="sub">每日饮食底稿注入 · 控制台</div>
    </div>
  </div>
  <div class="tabs">
    <div class="tab active" onclick="switchTab('today')">今日</div>
    <div class="tab" onclick="switchTab('history')">近几天</div>
    <div class="tab" onclick="switchTab('foods')">食物库</div>
  </div>
</header>

<!-- 今日 -->
<div id="page-today" class="page active">
  <div class="grid">
    <div class="card">
      <h3>🌅 早餐</h3>
      <button class="reroll" onclick="rerollSlot('breakfast')" title="重摇早餐">🎲</button>
      <div class="items" id="slot-breakfast">-</div>
    </div>
    <div class="card">
      <h3>☀️ 午餐</h3>
      <button class="reroll" onclick="rerollSlot('lunch')" title="重摇午餐">🎲</button>
      <div class="items" id="slot-lunch">-</div>
    </div>
    <div class="card">
      <h3>🌙 晚餐</h3>
      <button class="reroll" onclick="rerollSlot('dinner')" title="重摇晚餐">🎲</button>
      <div class="items" id="slot-dinner">-</div>
    </div>
    <div class="card">
      <h3>🍰 加餐 / 甜点</h3>
      <button class="reroll" onclick="rerollSlot('snack')" title="重摇加餐">🎲</button>
      <div class="items" id="slot-snack"><span class="empty">无</span></div>
    </div>
  </div>

  <div class="actions">
    <button class="btn" onclick="rerollAll()">🎲 全部重摇</button>
    <button class="btn btn-outline" onclick="loadToday()">🔄 刷新</button>
  </div>

  <div style="font-size:12px;color:var(--muted);margin-bottom:6px;">静默注入 Prompt 预览（AI 会看到的提示）：</div>
  <div class="preview-box" id="snippet-preview">加载中...</div>
</div>

<!-- 历史 -->
<div id="page-history" class="page">
  <div class="actions">
    <button class="btn btn-outline" onclick="loadHistory()">🔄 刷新历史</button>
  </div>
  <div id="history-list"></div>
</div>

<!-- 食物库 -->
<div id="page-foods" class="page">
  <div class="toolbar">
    <input class="search-input" id="food-search" placeholder="🔍 搜菜名..." oninput="renderFoodsTable()"/>
    <select class="filter-select" id="food-filter-cat" onchange="renderFoodsTable()">
      <option value="">全部分类</option>
      <option value="主食">主食</option>
      <option value="配菜">配菜</option>
      <option value="汤">汤</option>
      <option value="甜点">甜点</option>
      <option value="饮品">饮品</option>
    </select>
    <select class="filter-select" id="food-filter-love" onchange="renderFoodsTable()">
      <option value="">全部喜好</option>
      <option value="2">⭐⭐ 特别喜欢</option>
      <option value="1">⭐ 喜欢</option>
      <option value="0">一般</option>
    </select>
    <select class="filter-select" id="food-filter-time" onchange="renderFoodsTable()">
      <option value="">全部时段</option>
      <option value="早">🍞 早餐</option>
      <option value="午">🍚 午餐</option>
      <option value="晚">🍜 晚餐</option>
      <option value="加">🍰 加餐</option>
      <option value="__none__">未标时段</option>
    </select>
    <button class="btn" onclick="addFoodRow()">➕ 加一道菜</button>
    <span class="badge-count" id="food-count">0 道菜</span>
  </div>

  <div class="table-wrapper">
    <table>
      <thead><tr>
        <th style="min-width:140px">菜名</th>
        <th style="min-width:110px">喜好度</th>
        <th style="min-width:90px">分类</th>
        <th style="min-width:140px">偏好时段</th>
        <th style="min-width:55px;text-align:center;">怪味</th>
        <th style="width:45px"></th>
      </tr></thead>
      <tbody id="foods-tbody"></tbody>
    </table>
  </div>

  <div class="save-bar">
    <button class="btn" onclick="saveFoods()">💾 保存所有改动</button>
    <button class="btn btn-outline" onclick="loadFoods()">↩️ 放弃并重新载入</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let FOODS = [];

function toast(msg){
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 1800);
}

function switchTab(name){
  document.querySelectorAll('.tab').forEach((el,i)=>{
    el.classList.toggle('active', ['today','history','foods'][i] === name);
  });
  document.querySelectorAll('.page').forEach(el=>el.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if(name === 'today') loadToday();
  if(name === 'history') loadHistory();
  if(name === 'foods') loadFoods();
}

async function loadToday(){
  try{
    const r = await fetch('/api/today');
    const data = await r.json();
    const m = data.menu || data.meal || {};
    ['breakfast','lunch','dinner','snack'].forEach(slot => {
      const raw = m[slot] || '';
      const items = Array.isArray(raw) ? raw : (typeof raw === 'string' && raw.trim() ? raw.split('+') : []);
      const el = document.getElementById('slot-' + slot);
      if(items.length){
        el.innerHTML = items.join(' + ');
      } else {
        el.innerHTML = '<span class="empty">无</span>';
      }
    });
    document.getElementById('snippet-preview').textContent = data.snippet || '（今日无底稿）';
  }catch(e){ toast('加载失败: ' + e.message); }
}

async function rerollSlot(slot){
  try{
    const r = await fetch('/api/reroll', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({slot})
    });
    const data = await r.json();
    if(data.ok){
      loadToday();
      toast('已重摇 ' + {breakfast:'早餐', lunch:'午餐', dinner:'晚餐', snack:'加餐'}[slot]);
    }
  }catch(e){ toast('重摇失败: ' + e.message); }
}

async function rerollAll(){
  try{
    const r = await fetch('/api/reroll', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({})
    });
    const data = await r.json();
    if(data.ok){
      loadToday();
      toast('已全部重摇');
    }
  }catch(e){ toast('重摇失败: ' + e.message); }
}

async function loadHistory(){
  try{
    const r = await fetch('/api/history');
    const data = await r.json();
    const box = document.getElementById('history-list');
    box.innerHTML = '';
    const list = Array.isArray(data.history) ? data.history : [];
    if(!list.length){ box.innerHTML = '<div class="empty" style="padding:12px;color:var(--muted);">暂无历史记录</div>'; return; }
    list.forEach(([d, m]) => {
      m = m || {};
      const parts = [];
      if(m.breakfast) parts.push('早: ' + m.breakfast);
      if(m.lunch) parts.push('午: ' + m.lunch);
      if(m.dinner) parts.push('晚: ' + m.dinner);
      if(m.snack) parts.push('加餐: ' + m.snack);
      const div = document.createElement('div');
      div.className = 'history-item';
      div.innerHTML = `<div class="history-date">${d}</div><div class="history-content">${parts.join(' ｜ ') || '无记录'}</div>`;
      box.appendChild(div);
    });
  }catch(e){ toast('加载历史失败: ' + e.message); }
}

async function loadFoods(){
  try{
    const r = await fetch('/api/foods');
    const data = await r.json();
    FOODS = Array.isArray(data) ? data : (data.foods || []);
    renderFoodsTable();
  }catch(e){ toast('加载食物库失败: ' + e.message); }
}

function renderFoodsTable(){
  const tbody = document.getElementById('foods-tbody');
  const kw = (document.getElementById('food-search').value || '').trim().toLowerCase();
  const fCat = document.getElementById('food-filter-cat').value;
  const fLove = document.getElementById('food-filter-love').value;
  const fTime = document.getElementById('food-filter-time').value;

  tbody.innerHTML = '';
  let count = 0;

  FOODS.forEach((item, idx) => {
    if(kw && !item.name.toLowerCase().includes(kw)) return;
    if(fCat && item.cat !== fCat) return;
    if(fLove !== '' && String(item.love) !== fLove) return;
    if(fTime){
      const times = item.time || [];
      if(fTime === '__none__'){
        if(times.length > 0) return;
      } else {
        if(!times.includes(fTime)) return;
      }
    }
    count++;

    const tr = document.createElement('tr');

    const loveOpts = [
      {v:0, t:'一般'},
      {v:1, t:'⭐ 喜欢'},
      {v:2, t:'⭐⭐ 特别喜欢'}
    ].map(o => `<option value="${o.v}" ${item.love===o.v?'selected':''}>${o.t}</option>`).join('');

    const catOpts = ['主食','配菜','汤','甜点','饮品']
      .map(c => `<option value="${c}" ${item.cat===c?'selected':''}>${c}</option>`).join('');

    const times = item.time || [];
    const timeChips = ['早','午','晚','加'].map(t => {
      const active = times.includes(t);
      return `<span class="time-chip ${active?'active':''}" onclick="toggleTime(${idx}, '${t}')">${t}</span>`;
    }).join('');

    tr.innerHTML = `
      <td><input class="in-name" type="text" placeholder="菜名" value="${item.name ? item.name.replace(/"/g,'&quot;') : ''}" oninput="FOODS[${idx}].name=this.value.trim()"/></td>
      <td><select class="in-select" onchange="FOODS[${idx}].love=Number(this.value)">${loveOpts}</select></td>
      <td><select class="in-select" onchange="FOODS[${idx}].cat=this.value">${catOpts}</select></td>
      <td><div class="time-chips">${timeChips}</div></td>
      <td style="text-align:center;"><input type="checkbox" ${item.weird?'checked':''} onchange="FOODS[${idx}].weird=this.checked"/></td>
      <td><button class="del-btn" onclick="delFood(${idx})" title="删除">🗑️</button></td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('food-count').textContent = `${count} / ${FOODS.length} 道菜`;
}

function toggleTime(idx, slot){
  const item = FOODS[idx];
  if(!item.time) item.time = [];
  const i = item.time.indexOf(slot);
  if(i >= 0) item.time.splice(i, 1);
  else item.time.push(slot);
  renderFoodsTable();
}

function addFoodRow(){
  FOODS.unshift({
    name: '新菜品',
    love: 1,
    cat: '主食',
    time: [],
    weird: false
  });
  renderFoodsTable();
  toast('已在顶部添加新菜品，修改后记得保存');
}

function delFood(idx){
  const name = FOODS[idx].name;
  FOODS.splice(idx, 1);
  renderFoodsTable();
  toast(`已移除「${name}」`);
}

async function saveFoods(){
  const valid = FOODS.filter(f => f.name && f.name.trim());
  try{
    const r = await fetch('/api/foods', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({foods: valid})
    });
    const data = await r.json();
    if(data.ok){
      FOODS = valid;
      renderFoodsTable();
      toast(`保存成功，共 ${valid.length} 道菜`);
    } else {
      toast('保存失败: ' + (data.msg || '未知错误'));
    }
  }catch(e){ toast('保存异常: ' + e.message); }
}

loadToday();
</script>
</body></html>
"""


LOGIN_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"/>
<title>兔吃了么 · 登录</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
<link rel="apple-touch-icon" href="/favicon.svg"/>
<link rel="manifest" href="/manifest.webmanifest"/>
<meta name="theme-color" content="#ff7aa2"/>
<style>
  body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#fff5f7;color:#4b3b46;display:flex;align-items:center;justify-content:center;height:100vh;-webkit-font-smoothing:antialiased;}
  .box{background:#fff;border:1px solid #ffe3ea;border-radius:16px;padding:26px 28px;box-shadow:0 4px 16px rgba(255,122,162,.1);min-width:290px;text-align:center;}
  .logo{width:56px;height:56px;margin-bottom:8px;border-radius:14px;}
  h2{margin:0 0 6px;font-size:18px;color:#ff7aa2;}
  .sub{color:#a08b95;font-size:12px;margin-bottom:18px;}
  input{width:100%;padding:10px 12px;border:1px solid #ffe3ea;border-radius:8px;font-size:14px;box-sizing:border-box;outline:none;}
  input:focus{border-color:#ff7aa2;}
  button{margin-top:12px;width:100%;padding:10px;background:#ff7aa2;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;transition:opacity .15s;}
  button:hover{opacity:0.9;}
  .err{color:#d66;font-size:12px;margin-top:8px;}
</style>
</head>
<body>
<div class="box">
  <img class="logo" src="/favicon.svg" alt="🐰"/>
  <h2>🐰 兔吃了么</h2>
  <div class="sub">请输入访问 Token</div>
  <form method="post" action="/login">
    <input type="password" name="token" placeholder="访问密码" autofocus/>
    <button type="submit">进入控制台</button>
  </form>
  {err_html}
</div>
</body>
</html>
"""
