FALCONQUERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FalconQuery — Team Falcon</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#06101e;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:system-ui,-apple-system,sans-serif}
.app{display:flex;height:620px;width:900px;background:#0a1628;border-radius:16px;overflow:hidden}
.sidebar{width:232px;background:#0d1f3c;border-right:0.5px solid rgba(100,160,255,0.15);display:flex;flex-direction:column;flex-shrink:0}
.logo{padding:18px 14px 14px;display:flex;align-items:center;gap:9px;border-bottom:0.5px solid rgba(100,160,255,0.1)}
.logo-icon{width:30px;height:30px;background:#1e6eff;border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.logo-icon svg{width:16px;height:16px;stroke:white;fill:none;stroke-width:2}
.logo-name{font-size:15px;font-weight:500;color:#e8f0ff}
.logo-tag{font-size:9.5px;color:#2a5a9a;text-transform:uppercase;letter-spacing:1px;margin-top:1px}
.new-btn{margin:10px;padding:8px 12px;background:rgba(30,110,255,0.12);border:0.5px solid rgba(30,110,255,0.3);border-radius:7px;color:#6aa8ff;font-size:12.5px;cursor:pointer;display:flex;align-items:center;gap:7px;transition:background 0.15s}
.new-btn:hover{background:rgba(30,110,255,0.22)}
.new-btn svg{width:13px;height:13px;stroke:#6aa8ff;fill:none;stroke-width:2.5}
.chat-list{flex:1;overflow-y:auto;padding:2px 6px}
.chat-list::-webkit-scrollbar{width:3px}
.chat-list::-webkit-scrollbar-thumb{background:rgba(100,160,255,0.15);border-radius:2px}
.grp-label{font-size:10px;color:#2a4a7a;text-transform:uppercase;letter-spacing:0.7px;padding:8px 8px 3px}
.chat-item{padding:7px 9px;border-radius:6px;cursor:pointer;margin-bottom:1px}
.chat-item:hover{background:rgba(30,110,255,0.09)}
.chat-item.active{background:rgba(30,110,255,0.16);border:0.5px solid rgba(30,110,255,0.18)}
.ci-title{font-size:12px;color:#a8c0e8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ci-meta{font-size:10px;color:#2a4a7a;margin-top:1px}
.sb-foot{padding:10px;border-top:0.5px solid rgba(100,160,255,0.1)}
.user-row{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:7px;cursor:pointer}
.user-row:hover{background:rgba(30,110,255,0.09)}
.ava{width:26px;height:26px;border-radius:50%;background:#1e3a7a;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:500;color:#6aa8ff;flex-shrink:0;border:0.5px solid rgba(30,110,255,0.3)}
.u-name{font-size:12px;color:#a8c0e8}
.u-role{font-size:10px;color:#2a4a7a}
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{padding:12px 18px;border-bottom:0.5px solid rgba(100,160,255,0.1);display:flex;align-items:center;justify-content:space-between}
.tb-title{font-size:13.5px;color:#a8c0e8;font-weight:500}
.ds-select{font-size:11.5px;padding:4px 10px;background:rgba(30,110,255,0.1);border:0.5px solid rgba(30,110,255,0.22);border-radius:20px;color:#6aa8ff;cursor:pointer;outline:none}
.ds-select option{background:#0d1f3c;color:#a8c0e8}
.msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:14px}
.msgs::-webkit-scrollbar{width:3px}
.msgs::-webkit-scrollbar-thumb{background:rgba(100,160,255,0.12);border-radius:2px}
.msg{display:flex;gap:9px;max-width:90%}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg-ava{width:26px;height:26px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:500;margin-top:2px}
.msg-ava.bot{background:#1e6eff;color:white}
.msg-ava.user{background:#1e3a7a;color:#6aa8ff;border:0.5px solid rgba(30,110,255,0.3)}
.bubble{padding:9px 13px;font-size:13px;line-height:1.6}
.msg.bot .bubble{background:rgba(255,255,255,0.04);border:0.5px solid rgba(100,160,255,0.1);color:#b8d0f0;border-radius:3px 10px 10px 10px}
.msg.user .bubble{background:rgba(30,110,255,0.18);border:0.5px solid rgba(30,110,255,0.28);color:#c8dcff;border-radius:10px 3px 10px 10px}
.msg-time{font-size:10px;color:#1e3a6a;margin-top:3px;padding:0 2px}
.conf-badge{display:inline-block;font-size:10px;padding:2px 7px;background:rgba(30,110,255,0.1);border:0.5px solid rgba(30,110,255,0.2);border-radius:10px;color:#3a6aaa;margin-top:5px}
.typing-dots{display:flex;gap:4px;align-items:center;padding:4px 0}
.dot{width:5px;height:5px;border-radius:50%;background:#3a6aaa;animation:blink 1.2s ease-in-out infinite}
.dot:nth-child(2){animation-delay:0.2s}
.dot:nth-child(3){animation-delay:0.4s}
@keyframes blink{0%,80%,100%{opacity:0.3;transform:scale(0.8)}40%{opacity:1;transform:scale(1)}}
.input-wrap{padding:12px 14px;border-top:0.5px solid rgba(100,160,255,0.1)}
.input-box{display:flex;gap:7px;align-items:flex-end;background:rgba(255,255,255,0.035);border:0.5px solid rgba(100,160,255,0.18);border-radius:10px;padding:7px 9px;transition:border-color 0.15s}
.input-box:focus-within{border-color:rgba(30,110,255,0.45)}
.input-box textarea{flex:1;background:transparent;border:none;outline:none;color:#b8d0f0;font-size:13px;font-family:inherit;resize:none;line-height:1.5;min-height:20px;max-height:96px}
.input-box textarea::placeholder{color:#1e3a6a}
.send-btn{width:30px;height:30px;border-radius:7px;background:#1e6eff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background 0.15s,transform 0.1s,opacity 0.15s}
.send-btn:hover{background:#2d7aff}
.send-btn:active{transform:scale(0.93)}
.send-btn:disabled{opacity:0.4;cursor:not-allowed}
.send-btn svg{width:13px;height:13px;fill:white}
.chips{display:flex;gap:5px;margin-top:7px;flex-wrap:wrap}
.chip{font-size:11px;padding:3px 9px;background:rgba(30,110,255,0.07);border:0.5px solid rgba(30,110,255,0.15);border-radius:20px;color:#3a6aaa;cursor:pointer;transition:all 0.12s;white-space:nowrap}
.chip:hover{background:rgba(30,110,255,0.15);color:#6aa8ff;border-color:rgba(30,110,255,0.3)}
.api-status{display:flex;align-items:center;gap:5px;font-size:10px}
.status-dot{width:6px;height:6px;border-radius:50%}
.status-dot.online{background:#3aaa6a}
.status-dot.offline{background:#aa3a3a}
.status-dot.checking{background:#aa8a2a;animation:blink 1s ease-in-out infinite}
.status-text{color:#2a4a7a}
.error-bubble{color:#d08080}
</style>
</head>
<body>
<div class="app">
  <div class="sidebar">
    <div class="logo">
      <div class="logo-icon"><svg viewBox="0 0 24 24"><path d="M12 2L3 7l9 5 9-5-9-5zM3 17l9 5 9-5M3 12l9 5 9-5"/></svg></div>
      <div><div class="logo-name">FalconQuery</div><div class="logo-tag">Team Falcon · TRP1</div></div>
    </div>
    <button class="new-btn" onclick="newChat()">
      <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      New conversation
    </button>
    <div class="chat-list" id="chatList"></div>
    <div class="sb-foot">
      <div class="api-status" style="padding:4px 8px 8px">
        <div class="status-dot checking" id="statusDot"></div>
        <div class="status-text" id="statusText">Connecting...</div>
      </div>
      <div class="user-row">
        <div class="ava">FQ</div>
        <div><div class="u-name">FalconQuery</div><div class="u-role">Team Falcon · TRP1 FDE</div></div>
      </div>
    </div>
  </div>
  <div class="main">
    <div class="topbar">
      <div class="tb-title" id="chatTitle">New conversation</div>
      <select class="ds-select" id="datasetSelect" onchange="renderChips()">
        <option value="yelp">Yelp</option>
        <option value="bookreview">Bookreview</option>
        <option value="agnews">AGNews</option>
        <option value="GITHUB_REPOS">GitHub Repos</option>
        <option value="stockmarket">Stockmarket</option>
      </select>
    </div>
    <div class="msgs" id="msgs">
      <div class="msg bot">
        <div class="msg-ava bot">FQ</div>
        <div>
          <div class="bubble">Hello! I am <strong>FalconQuery</strong> — your AI data analytics assistant powered by Oracle Forge. Ask me anything about Yelp businesses, GitHub repos, stock market data, book reviews, and more.</div>
          <div class="msg-time" id="welcomeTime"></div>
        </div>
      </div>
    </div>
    <div class="input-wrap">
      <div class="input-box">
        <textarea id="input" placeholder="Ask anything about your data..." rows="1" onkeydown="handleKey(event)" oninput="resize(this)"></textarea>
        <button class="send-btn" id="sendBtn" onclick="send()">
          <svg viewBox="0 0 24 24"><path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/></svg>
        </button>
      </div>
      <div class="chips" id="chips"></div>
    </div>
  </div>
</div>
<script>
const API='';
const CHIPS={yelp:['Average rating in Indianapolis?','State with most reviews?','Businesses with WiFi in PA?','Top rated category?'],bookreview:['Best rated books in 2020s?','Literature Fiction with 5.0 rating?'],agnews:['Top news categories?'],GITHUB_REPOS:['Top 5 repos by commits not Python?','Shell repos with Apache-2.0?'],stockmarket:['Max adjusted close for RealReal 2020?','Top NYSE stocks with more up days in 2017?']};
let sessions=[],current=null,loading=false;
function time(){return new Date().toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',hour12:true})}
function resize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,96)+'px'}
function handleKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}}
function renderChips(){const ds=document.getElementById('datasetSelect').value;document.getElementById('chips').innerHTML=(CHIPS[ds]||[]).map(c=>`<div class="chip" onclick="useChip(this)">${c}</div>`).join('')}
function useChip(el){document.getElementById('input').value=el.textContent;send()}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>')}
function renderChatList(){const l=document.getElementById('chatList');if(!sessions.length){l.innerHTML='<div class="grp-label" style="text-align:center;padding-top:20px;color:#1a3a6a">No conversations yet</div>';return}let h='<div class="grp-label">Recent</div>';sessions.slice().reverse().forEach((s,ri)=>{const i=sessions.length-1-ri;const a=s===current?' active':'';h+=`<div class="chat-item${a}" onclick="loadSession(${i})"><div class="ci-title">${esc(s.title)}</div><div class="ci-meta">${s.dataset} · ${s.msgs.length} msgs</div></div>`});l.innerHTML=h}
function loadSession(i){current=sessions[i];document.getElementById('chatTitle').textContent=current.title;document.getElementById('datasetSelect').value=current.dataset;renderMessages();renderChips();renderChatList()}
function renderMessages(){const c=document.getElementById('msgs');c.innerHTML='';if(!current)return;current.msgs.forEach(m=>c.appendChild(buildMsg(m)));c.scrollTop=c.scrollHeight}
function buildMsg(m){const w=document.createElement('div');w.className='msg '+m.role;const ac=m.role==='bot'?'bot':'user';const al=m.role==='bot'?'FQ':'YD';let html=`<div class="msg-ava ${ac}">${al}</div><div>`;if(m.error){html+=`<div class="bubble error-bubble">${m.text}</div>`}else if(m.role==='bot'&&m.conf!==undefined){html+=`<div class="bubble">${m.text}<div class="conf-badge">confidence: ${Math.round(m.conf*100)}%</div></div>`}else{html+=`<div class="bubble">${m.text}</div>`}html+=`<div class="msg-time">${m.time}</div></div>`;w.innerHTML=html;return w}
function addMsg(m){if(current)current.msgs.push(m);const c=document.getElementById('msgs');c.appendChild(buildMsg(m));c.scrollTop=c.scrollHeight}
function showTyping(){const c=document.getElementById('msgs');const el=document.createElement('div');el.className='msg bot';el.id='typing';el.innerHTML='<div class="msg-ava bot">FQ</div><div><div class="bubble"><div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div></div>';c.appendChild(el);c.scrollTop=c.scrollHeight}
function hideTyping(){const el=document.getElementById('typing');if(el)el.remove()}
async function send(){if(loading)return;const inp=document.getElementById('input');const text=inp.value.trim();if(!text)return;const ds=document.getElementById('datasetSelect').value;if(!current){current={title:text.slice(0,38)+(text.length>38?'...':''),dataset:ds,msgs:[],sid:null};sessions.push(current);document.getElementById('chatTitle').textContent=current.title}inp.value='';inp.style.height='auto';loading=true;document.getElementById('sendBtn').disabled=true;addMsg({role:'user',text:esc(text),time:time()});showTyping();renderChatList();try{const body={question:text,dataset:ds};if(current.sid)body.session_id=current.sid;const res=await fetch(`${API}/query`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});hideTyping();if(!res.ok){const e=await res.text();addMsg({role:'bot',text:`Error ${res.status}: ${esc(e.slice(0,120))}`,time:time(),error:true})}else{const d=await res.json();if(d.session_id)current.sid=d.session_id;addMsg({role:'bot',text:esc(d.answer),time:time(),conf:d.confidence})}}catch(e){hideTyping();addMsg({role:'bot',text:`Connection error: ${esc(e.message)}`,time:time(),error:true})}loading=false;document.getElementById('sendBtn').disabled=false;renderChatList()}
function newChat(){current=null;document.getElementById('chatTitle').textContent='New conversation';document.getElementById('msgs').innerHTML=`<div class="msg bot"><div class="msg-ava bot">FQ</div><div><div class="bubble">Hello! I am <strong>FalconQuery</strong>. Ask me anything about your data.</div><div class="msg-time">${time()}</div></div></div>`;renderChatList();document.getElementById('input').focus()}
async function checkStatus(){const dot=document.getElementById('statusDot');const txt=document.getElementById('statusText');try{const r=await fetch(`${API}/health`,{signal:AbortSignal.timeout(4000)});if(r.ok){dot.className='status-dot online';txt.textContent='API connected'}else{dot.className='status-dot offline';txt.textContent='API error'}}catch{dot.className='status-dot offline';txt.textContent='API offline'}}
document.getElementById('welcomeTime').textContent=time();renderChips();renderChatList();checkStatus();setInterval(checkStatus,30000);
</script>
</body>
</html>"""
