FALCONQUERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FalconQuery — Team Falcon</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#06101e;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:system-ui,-apple-system,sans-serif}
.app{display:flex;height:620px;width:920px;background:#0a1628;border-radius:16px;overflow:hidden}
.sidebar{width:240px;background:#0d1f3c;border-right:0.5px solid rgba(100,160,255,0.15);display:flex;flex-direction:column;flex-shrink:0}
.logo{padding:18px 14px 14px;display:flex;align-items:center;gap:9px;border-bottom:0.5px solid rgba(100,160,255,0.1)}
.logo-icon{width:30px;height:30px;background:#1e6eff;border-radius:7px;display:flex;align-items:center;justify-content:center}
.logo-icon svg{width:16px;height:16px;stroke:white;fill:none;stroke-width:2}
.logo-name{font-size:15px;font-weight:500;color:#e8f0ff}
.logo-tag{font-size:9px;color:#2a5a9a;text-transform:uppercase;letter-spacing:1px;margin-top:1px}
.new-btn{margin:10px;padding:8px 12px;background:rgba(30,110,255,0.12);border:0.5px solid rgba(30,110,255,0.3);border-radius:7px;color:#6aa8ff;font-size:12.5px;cursor:pointer;display:flex;align-items:center;gap:7px}
.new-btn svg{width:13px;height:13px;stroke:#6aa8ff;fill:none;stroke-width:2.5}
.chat-list{flex:1;overflow-y:auto;padding:2px 6px}
.grp-label{font-size:10px;color:#2a4a7a;text-transform:uppercase;letter-spacing:0.7px;padding:8px 8px 3px}
.chat-item{padding:7px 9px;border-radius:6px;cursor:pointer;margin-bottom:1px}
.chat-item:hover{background:rgba(30,110,255,0.09)}
.chat-item.active{background:rgba(30,110,255,0.16);border:0.5px solid rgba(30,110,255,0.18)}
.ci-title{font-size:12px;color:#a8c0e8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ci-input{font-size:12px;color:#a8c0e8;background:rgba(30,110,255,0.15);border:0.5px solid rgba(30,110,255,0.4);border-radius:4px;outline:none;width:100%;padding:1px 4px;font-family:inherit}
.ci-meta{font-size:10px;color:#2a4a7a;margin-top:1px}
.sb-foot{padding:10px;border-top:0.5px solid rgba(100,160,255,0.1)}
.status-row{display:flex;align-items:center;gap:5px;padding:4px 8px 8px}
.sdot{width:6px;height:6px;border-radius:50%;background:#3aaa6a}
.stxt{font-size:10px;color:#2a7a4a}
.user-row{display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:7px}
.ava{width:26px;height:26px;border-radius:50%;background:#1e3a7a;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:500;color:#6aa8ff;border:0.5px solid rgba(30,110,255,0.3)}
.u-name{font-size:12px;color:#a8c0e8}
.u-role{font-size:10px;color:#2a4a7a}
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{padding:12px 18px;border-bottom:0.5px solid rgba(100,160,255,0.1);display:flex;align-items:center;justify-content:space-between;gap:12px}
.tb-title{font-size:13.5px;color:#a8c0e8;font-weight:500;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ds-select{font-size:11.5px;padding:4px 10px;background:rgba(30,110,255,0.1);border:0.5px solid rgba(30,110,255,0.22);border-radius:20px;color:#6aa8ff;cursor:pointer;outline:none}
.ds-select option{background:#0d1f3c;color:#a8c0e8}
.msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:14px}
.msg{display:flex;gap:9px;max-width:90%}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg-ava{width:26px;height:26px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:500;margin-top:2px}
.msg-ava.bot{background:#1e6eff;color:white}
.msg-ava.user{background:#1e3a7a;color:#6aa8ff;border:0.5px solid rgba(30,110,255,0.3)}
.bubble{padding:9px 13px;font-size:13px;line-height:1.6}
.bot .bubble{background:rgba(255,255,255,0.04);border:0.5px solid rgba(100,160,255,0.1);color:#b8d0f0;border-radius:3px 10px 10px 10px}
.user .bubble{background:rgba(30,110,255,0.18);border:0.5px solid rgba(30,110,255,0.28);color:#c8dcff;border-radius:10px 3px 10px 10px}
.msg-time{font-size:10px;color:#1e3a6a;margin-top:3px}
.conf{display:inline-block;font-size:10px;padding:2px 7px;background:rgba(30,110,255,0.1);border:0.5px solid rgba(30,110,255,0.2);border-radius:10px;color:#3a6aaa;margin-top:5px}
.dots{display:flex;gap:4px;align-items:center;padding:4px 0}
.dot{width:5px;height:5px;border-radius:50%;background:#3a6aaa;animation:bl 1.2s ease-in-out infinite}
.dot:nth-child(2){animation-delay:.2s}
.dot:nth-child(3){animation-delay:.4s}
@keyframes bl{0%,80%,100%{opacity:.3;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}
.input-wrap{padding:12px 14px;border-top:0.5px solid rgba(100,160,255,0.1)}
.input-box{display:flex;gap:7px;align-items:flex-end;background:rgba(255,255,255,0.035);border:0.5px solid rgba(100,160,255,0.18);border-radius:10px;padding:7px 9px}
.input-box:focus-within{border-color:rgba(30,110,255,0.45)}
.input-box textarea{flex:1;background:transparent;border:none;outline:none;color:#b8d0f0;font-size:13px;font-family:inherit;resize:none;line-height:1.5;min-height:20px;max-height:96px}
.input-box textarea::placeholder{color:#1e3a6a}
.send-btn{width:30px;height:30px;border-radius:7px;background:#1e6eff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.send-btn:hover{background:#2d7aff}
.send-btn svg{width:13px;height:13px;fill:white}
.chips{display:flex;gap:5px;margin-top:7px;flex-wrap:wrap}
.chip{font-size:11px;padding:3px 9px;background:rgba(30,110,255,0.07);border:0.5px solid rgba(30,110,255,0.15);border-radius:20px;color:#3a6aaa;cursor:pointer;white-space:nowrap}
.chip:hover{background:rgba(30,110,255,0.15);color:#6aa8ff}
.err{color:#d08080}
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
    <div class="chat-list" id="chatList"><div class="grp-label" style="text-align:center;padding-top:20px;color:#1a3a6a">No conversations yet</div></div>
    <div class="sb-foot">
      <div class="status-row"><div class="sdot"></div><div class="stxt">Oracle Forge online</div></div>
      <div class="user-row">
        <div class="ava">FQ</div>
        <div><div class="u-name">FalconQuery</div><div class="u-role">Team Falcon · TRP1 FDE</div></div>
      </div>
    </div>
  </div>
  <div class="main">
    <div class="topbar">
      <div class="tb-title" id="chatTitle">New conversation</div>
      <select class="ds-select" id="ds" onchange="renderChips()">
        <option value="yelp">Yelp</option>
        <option value="bookreview">Bookreview</option>
        <option value="agnews">AGNews</option>
        <option value="GITHUB_REPOS">GitHub Repos</option>
        <option value="stockmarket">Stockmarket</option>
        <option value="stockindex">Stockindex</option>
        <option value="music_brainz_20k">Music Brainz</option>
        <option value="crmarenapro">CRM Arena Pro</option>
        <option value="DEPS_DEV_V1">Deps Dev V1</option>
        <option value="PANCANCER_ATLAS">Pancancer Atlas</option>
        <option value="googlelocal">Google Local</option>
        <option value="PATENTS">Patents</option>
      </select>
    </div>
    <div class="msgs" id="msgs"></div>
    <div class="input-wrap">
      <div class="input-box">
        <textarea id="inp" placeholder="Ask anything about your data..." rows="1" onkeydown="onKey(event)" oninput="resize(this)"></textarea>
        <button class="send-btn" onclick="send()">
          <svg viewBox="0 0 24 24"><path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/></svg>
        </button>
      </div>
      <div class="chips" id="chips"></div>
    </div>
  </div>
</div>
<script>
var API = 'https://charleston-lounge-tank-bachelor.trycloudflare.com';
var CHIPS = {
  yelp:['Average rating in Indianapolis?','State with most reviews?','Businesses with WiFi in PA?','Top rated category?'],
  bookreview:['Best rated decade?','Literature Fiction with 5.0 rating?','Children books rated above 4.5?'],
  agnews:['Top news categories?'],
  GITHUB_REPOS:['Top 5 repos by commits not Python?','Shell repos with Apache-2.0?'],
  stockmarket:['Max adjusted close for RealReal 2020?','Top NYSE stocks up days 2017?'],
  stockindex:['Best performing index 2020?'],
  music_brainz_20k:['Top selling tracks?'],
  crmarenapro:['Top sales accounts?'],
  DEPS_DEV_V1:['Most depended packages?'],
  PANCANCER_ATLAS:['Most common cancer types?'],
  googlelocal:['Top rated restaurants?'],
  PATENTS:['Most cited patents?']
};
var sessions = [], current = null, busy = false;

function t(){return new Date().toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',hour12:true});}
function resize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,96)+'px';}
function onKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');}

function renderChips(){
  var ds=document.getElementById('ds').value;
  var arr=CHIPS[ds]||[];
  document.getElementById('chips').innerHTML=arr.map(function(c){
    return '<div class="chip" onclick="useChip(this)">'+c+'</div>';
  }).join('');
}

function useChip(el){document.getElementById('inp').value=el.textContent;send();}

function addMsg(role,text,conf,isErr){
  var msgs=document.getElementById('msgs');
  var w=document.createElement('div');
  w.className='msg '+role;
  var al=role==='bot'?'FQ':'YD';
  var cls=role==='bot'?'bot':'user';
  var inner='<div class="msg-ava '+cls+'">'+al+'</div><div>';
  if(isErr){inner+='<div class="bubble err">'+text+'</div>';}
  else if(role==='bot'&&conf!==undefined){inner+='<div class="bubble">'+text+'<div class="conf">confidence: '+Math.round(conf*100)+'%</div></div>';}
  else{inner+='<div class="bubble">'+text+'</div>';}
  inner+='<div class="msg-time">'+t()+'</div></div>';
  w.innerHTML=inner;
  msgs.appendChild(w);
  msgs.scrollTop=msgs.scrollHeight;
  if(current)current.msgs.push({role:role,text:text,conf:conf,isErr:isErr});
}

function showTyping(){
  var msgs=document.getElementById('msgs');
  var el=document.createElement('div');
  el.className='msg bot';el.id='typing';
  el.innerHTML='<div class="msg-ava bot">FQ</div><div><div class="bubble"><div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div></div>';
  msgs.appendChild(el);msgs.scrollTop=msgs.scrollHeight;
}
function hideTyping(){var el=document.getElementById('typing');if(el)el.remove();}

function renderChatList(){
  var l=document.getElementById('chatList');
  if(!sessions.length){l.innerHTML='<div class="grp-label" style="text-align:center;padding-top:20px;color:#1a3a6a">No conversations yet</div>';return;}
  var h='<div class="grp-label">Recent</div>';
  var rev=sessions.slice().reverse();
  for(var ri=0;ri<rev.length;ri++){
    var s=rev[ri];
    var i=sessions.length-1-ri;
    var a=s===current?' active':'';
    h+='<div class="chat-item'+a+'" onclick="loadSession('+i+')" ondblclick="startRename(event,'+i+')">'
      +'<div class="ci-title" id="cit'+i+'">'+esc(s.title)+'</div>'
      +'<div class="ci-meta">'+s.ds+' · '+s.msgs.length+' msgs</div>'
      +'</div>';
  }
  l.innerHTML=h;
}

function startRename(e,i){
  e.stopPropagation();
  var el=document.getElementById('cit'+i);if(!el)return;
  var inp=document.createElement('input');
  inp.className='ci-input';inp.value=sessions[i].title;
  inp.onclick=function(ev){ev.stopPropagation();};
  inp.onkeydown=function(ev){if(ev.key==='Enter'){finishRename(i,inp.value);}if(ev.key==='Escape'){renderChatList();}};
  inp.onblur=function(){finishRename(i,inp.value);};
  el.replaceWith(inp);inp.focus();inp.select();
}
function finishRename(i,val){
  var name=val.trim()||sessions[i].title;
  sessions[i].title=name;
  if(sessions[i]===current)document.getElementById('chatTitle').textContent=name;
  renderChatList();
}

function loadSession(i){
  current=sessions[i];
  document.getElementById('chatTitle').textContent=current.title;
  document.getElementById('ds').value=current.ds;
  var msgs=document.getElementById('msgs');msgs.innerHTML='';
  for(var j=0;j<current.msgs.length;j++){
    var m=current.msgs[j];
    addMsg(m.role,m.text,m.conf,m.isErr);
  }
  renderChips();renderChatList();
}

function newChat(){
  current=null;
  document.getElementById('chatTitle').textContent='New conversation';
  document.getElementById('msgs').innerHTML='<div class="msg bot"><div class="msg-ava bot">FQ</div><div><div class="bubble">Hello! I am <strong>FalconQuery</strong>. Ask me anything about your data.</div><div class="msg-time">'+t()+'</div></div></div>';
  renderChatList();
  document.getElementById('inp').focus();
}

function send(){
  if(busy)return;
  var inp=document.getElementById('inp');
  var text=inp.value.trim();
  if(!text)return;
  var ds=document.getElementById('ds').value;
  if(!current){
    current={title:text.slice(0,40),ds:ds,msgs:[],sid:null};
    sessions.push(current);
    document.getElementById('chatTitle').textContent=current.title;
  }
  inp.value='';inp.style.height='auto';
  busy=true;
  addMsg('user',esc(text));
  showTyping();
  renderChatList();
  var body={question:text,dataset:ds};
  if(current.sid)body.session_id=current.sid;
  fetch(API+'/query',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  }).then(function(r){
    hideTyping();
    if(!r.ok){r.text().then(function(e){addMsg('bot','Error '+r.status+': '+esc(e.slice(0,100)),undefined,true);busy=false;renderChatList();});}
    else{r.json().then(function(d){if(d.session_id)current.sid=d.session_id;addMsg('bot',esc(d.answer),d.confidence);busy=false;renderChatList();});}
  }).catch(function(e){
    hideTyping();
    addMsg('bot','Connection error: '+esc(e.message),undefined,true);
    busy=false;renderChatList();
  });
}

newChat();
renderChips();
</script>
</body>
</html>"""
