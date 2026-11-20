const ORDER=Core.ORDER,STATS=Core.STATS,SN=['Potenza','Intelligenza','Velocità','Resistenza','Versatilità'],ROLES=Core.ROLES,RN={avanguardia:'Avanguardia',stratega:'Stratega',ricognitore:'Ricognitore',difensore:'Difensore',specialista:'Specialista'},SAVE='tva-draft-save-v2',SAVE1='tva-draft-save-v1',BEATS=5,BEAT_MS=2900;
const SCN={asgard:'Asgard',wakanda:'Wakanda',quantum:'Regno Quantico',battleworld:'Battleworld'};
function warm(urls){try{if(navigator.connection&&navigator.connection.saveData)return;urls=urls.filter(Boolean);const go=()=>{for(const u of urls){fetch(u).catch(()=>{})}};setTimeout(go,1500)}catch{}}
const G=Core.make(D),byId=G.byId;
let offers=[],oh=[],seed='',A=[],B=[],turn=0,assign={},phase='idle',scenario='asgard',cpuLvl='stratega',result=null,timer=null;
const store={get(k){try{return localStorage.getItem(k)}catch{return null}},set(k,v){try{localStorage.setItem(k,v);return true}catch{return false}},del(k){try{localStorage.removeItem(k)}catch{}}};
const W=()=>D.scenarios[scenario];
const val=c=>G.val(c,W()),synergy=t=>G.synergy(t),total=(t,m)=>G.total(t,m,W()),bestAssign=t=>G.bestAssign(t,W());
const drafted=()=>new Set([...A,...B].map(c=>c.id));
const rngFor=(tag,t)=>Core.mulberry32(Core.hash32(seed+'|'+tag+'|'+t));
const makeOffer=t=>{const s=ORDER[t];return G.offers(drafted(),W(),seed,t,s==='A'?A:B,s==='A'?B:A)};
function ask(msg,ok,no){const d=$('tva-dlg');$('tva-dlg-t').textContent=msg;d.classList.add('on');const y=$('tva-dlg-yes'),n=$('tva-dlg-no');const close=()=>{d.classList.remove('on');y.onclick=n.onclick=null;document.removeEventListener('keydown',esc)};const esc=e=>{if(e.key==='Escape'){close();no&&no()}};document.addEventListener('keydown',esc);y.onclick=()=>{close();ok()};n.onclick=()=>{close();no&&no()};n.focus()}
function persist(){if(phase==='idle')return;const ok=store.set(SAVE,JSON.stringify({v:2,seed,scenario,cpu:cpuLvl,a:A.map(c=>c.id),b:B.map(c=>c.id),turn,offers:phase==='draft'&&ORDER[turn]==='A'?offers.map(c=>c.id):[],oh,assign,phase:phase==='cinematic'?'roles':phase,result}));if(ok)store.del(SAVE1)}
/* Ripristino: salvataggio v2 oppure migrazione automatica del v1 (pool da 16) senza perdere progressi. */
function checkAssign(r,asgn){const asg={};if(asgn&&typeof asgn==='object')for(const [k,v] of Object.entries(asgn)){if(!r.a.includes(k)||!ROLES.includes(v))throw 0;asg[k]=v}if(new Set(Object.values(asg)).size!==Object.keys(asg).length)throw 0;return asg}
function restore(){
 const raw=store.get(SAVE);
 if(raw){try{const r=JSON.parse(raw);
  const ok=r&&r.v===2&&SCN[r.scenario]&&['recluta','stratega','maestro'].includes(r.cpu)&&typeof r.seed==='string'&&r.seed&&Array.isArray(r.a)&&Array.isArray(r.b)&&Number.isInteger(r.turn)&&r.turn>=0&&r.turn<=10&&['draft','roles','done'].includes(r.phase);if(!ok)throw 0;
  const ids=[...r.a,...r.b];if(new Set(ids).size!==ids.length||ids.some(i=>!byId[i]))throw 0;if(r.a.length+r.b.length!==r.turn||r.a.length!==[...ORDER.slice(0,r.turn)].filter(x=>x==='A').length)throw 0;if(r.phase!=='draft'&&r.turn!==10)throw 0;
  const asg=checkAssign(r,r.assign);if(r.phase==='done'&&(Object.keys(asg).length!==5||!r.result||typeof r.result.x!=='number'||typeof r.result.y!=='number'))throw 0;
  scenario=r.scenario;cpuLvl=r.cpu;seed=r.seed;A=r.a.map(i=>byId[i]);B=r.b.map(i=>byId[i]);turn=r.turn;assign=asg;phase=r.phase;result=r.phase==='done'?r.result:null;oh=Array.isArray(r.oh)?r.oh.filter(h=>h&&Array.isArray(h.o)).slice(0,10):[];
  offers=[];if(phase==='draft'&&ORDER[turn]==='A'){const dr=drafted(),sv=(Array.isArray(r.offers)?r.offers:[]).map(i=>byId[i]);offers=sv.length===5&&new Set(sv.map(c=>c&&c.id)).size===5&&sv.every(c=>c&&!dr.has(c.id))?sv:makeOffer(turn).list}
  $('scenario').value=scenario;$('cpu').value=cpuLvl;return true}catch{store.del(SAVE)}}
 const raw1=store.get(SAVE1);if(!raw1)return false;
 try{const r=JSON.parse(raw1);const ok=r&&r.v===1&&SCN[r.scenario]&&['recluta','stratega','maestro'].includes(r.cpu)&&Array.isArray(r.pool)&&Array.isArray(r.a)&&Array.isArray(r.b)&&Number.isInteger(r.turn)&&r.turn>=0&&r.turn<=10&&['draft','roles','done'].includes(r.phase);if(!ok)throw 0;
  const ids=[...r.pool,...r.a,...r.b];if(ids.length!==16||new Set(ids).size!==16||ids.some(i=>!byId[i]))throw 0;if(r.a.length+r.b.length!==r.turn||r.a.length!==[...ORDER.slice(0,r.turn)].filter(x=>x==='A').length)throw 0;if(r.phase!=='draft'&&r.turn!==10)throw 0;
  const asg=checkAssign(r,r.assign);if(r.phase==='done'&&(Object.keys(asg).length!==5||!r.result||typeof r.result.x!=='number'||typeof r.result.y!=='number'))throw 0;
  scenario=r.scenario;cpuLvl=r.cpu;seed='mig'+Core.hash32(raw1).toString(36);A=r.a.map(i=>byId[i]);B=r.b.map(i=>byId[i]);turn=r.turn;assign=asg;phase=r.phase;result=r.phase==='done'?r.result:null;oh=[];offers=[];
  if(phase==='draft'&&ORDER[turn]==='A')offers=makeOffer(turn).list;
  $('scenario').value=scenario;$('cpu').value=cpuLvl;persist();return true}catch{store.del(SAVE1);return false}}
function newGame(){clearTimer();scenario=$('scenario').value;cpuLvl=$('cpu').value;seed=Date.now().toString(36)+Math.random().toString(36).slice(2,9);A=[];B=[];oh=[];offers=[];turn=0;assign={};result=null;phase='draft';advance()}
/* Turni snake: a ogni turno (anche consecutivi della CPU) si genera una nuova offerta dal seed; la CPU vede solo la propria offerta del turno. */
function advance(){offers=[];while(turn<10){const side=ORDER[turn],off=makeOffer(turn);if(side==='B'){const ch=G.cpuChoose(cpuLvl,off.list,B,A,W(),rngFor('c',turn));oh.push({t:turn,s:'B',o:off.list.map(c=>c.id),p:ch.id});B.push(ch);turn++}else{offers=off.list;break}}
 if(turn===10&&phase==='draft')phase='roles';persist();render()}
function pick(c){if(phase!=='draft'||ORDER[turn]!=='A'||!offers.includes(c))return;oh.push({t:turn,s:'A',o:offers.map(x=>x.id),p:c.id});A.push(c);turn++;advance()}
let btimers=[];function clearTimer(){btimers.forEach(clearTimeout);btimers=[];if(timer){clearInterval(timer);timer=null}}
function el(t,txt,cls){const e=document.createElement(t);if(txt!==undefined)e.textContent=txt;if(cls)e.className=cls;return e}
