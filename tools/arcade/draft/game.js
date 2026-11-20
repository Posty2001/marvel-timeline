/* ================= UI Draft 2.0 (il motore sopra resta quello di int3) ================= */
function hash(s){let h=2166136261;for(const ch of s){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
const SHY={Nightcrawler:'Night\u00adcrawler'};
function parts(n){const m=n.match(/^(.*?)\s*\((.*)\)\s*$/);const p=m?{main:m[1],sub:m[2]}:{main:n,sub:''};p.main=p.main.replace(/\b[A-Za-z]+\b/g,w=>SHY[w]||w);return p}
function lenCls(s){const L=Math.max(...s.split(/[\s\-\u00ad]+/).map(w=>w.length));return L>=12?'l12':L>=10?'l10':''}
function bestRole(c){let bi=0;STATS.forEach((k,i)=>{if(c.stats[k]>c.stats[STATS[bi]])bi=i});return ROLES[bi]}
let TIERS=[0,0],tierSc='';function calcTiers(){if(tierSc===scenario)return;tierSc=scenario;const v=D.roster.map(val).sort((a,b)=>a-b);TIERS=[v[Math.floor(v.length/3)],v[Math.floor(v.length*2/3)]]}
const tier=c=>{calcTiers();const v=val(c);return v>=TIERS[1]?'t-gold':v>=TIERS[0]?'t-silver':'t-bronze'};
const ICON={avanguardia:'<path d="M5 19 19 5M14 5h5v5M5 14l5 5"/>',stratega:'<circle cx="12" cy="12" r="8"/><path d="m15 9-2 5-5 1 2-5z"/>',ricognitore:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',difensore:'<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/>',specialista:'<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>'};
const roleSvg=r=>{const s=document.createElementNS('http://www.w3.org/2000/svg','svg');s.setAttribute('viewBox','0 0 24 24');s.setAttribute('aria-hidden','true');s.innerHTML=ICON[r];return s};
/* --- ritratti: SOLO voci approvate e complete del catalogo (assets/draft_portraits/manifest.json); altrimenti segnaposto originale --- */
const PORT={};
const okf=e=>e&&typeof e.file==='string'&&/^[\w\-]+\.(webp|png|jpe?g)$/.test(e.file);const usable=e=>okf(e)&&((e.status==='approved'&&e.license&&e.source_url&&e.author&&e.verified_on&&e.rights_confirmed===true)||(e.status==='test_stylized'&&e.license&&e.sha256&&e.rights_confirmed!==true));
fetch('../assets/draft_portraits/manifest.json').then(r=>r.ok?r.json():null).then(j=>{if(!j||j.schema!==1||!j.portraits)return;let n=0;for(const [id,e] of Object.entries(j.portraits))if(byId[id]&&usable(e)){PORT[id]='../assets/draft_portraits/'+e.file;n++}if(n&&phase!=='idle')render()}).catch(()=>{});
let UID=0;
function artSvg(c){const uid=++UID,h=hash(c.id),GC={'Avengers e alleati':[212,38],'X-Men e mutanti':[42,48],'Spider-Verse e simbionti':[350,46],'Cosmici e altri':[268,44]},g=GC[c.group]||[200,40],hue=(g[0]+(h%34)-17+360)%360,sat=g[1]+20;
 const v=h>>3,rays=9+(v%7),head=v%5,emb=(v>>3)%5,flip=(v>>6)&1;
 const c1=`hsl(${hue} ${sat+10}% 46%)`,c2=`hsl(${(hue+28)%360} ${sat}% 18%)`,c3=`hsl(${(hue+180)%360} 70% 62%)`,dk=`hsl(${hue} 45% 9%)`;
 let ray='';for(let i=0;i<rays;i++){const a1=i*2*Math.PI/rays,a2=a1+Math.PI/rays;ray+=`<path d="M50 62 L${(50+160*Math.cos(a1)).toFixed(1)} ${(62+160*Math.sin(a1)).toFixed(1)} L${(50+160*Math.cos(a2)).toFixed(1)} ${(62+160*Math.sin(a2)).toFixed(1)}Z"/>`}
 const E=[`<polygon points="50,6 58,26 80,26 62,38 69,58 50,46 31,58 38,38 20,26 42,26"/>`,`<path d="M50 8 82 22v26c0 20-14 32-32 40C32 80 18 68 18 48V22z"/>`,`<polygon points="50,8 84,28 84,66 50,86 16,66 16,28"/>`,`<path d="M58 6 28 52h20l-8 40 34-50H52z"/>`,`<circle cx="50" cy="48" r="34"/><circle cx="50" cy="48" r="18" fill="none" stroke="#000" stroke-width="4"/>`][emb];
 const H=[`<circle cx="50" cy="66" r="15"/>`,`<path d="M50 48c-17 0-22 14-22 24h44c0-10-5-24-22-24z"/><circle cx="50" cy="68" r="10"/>`,`<rect x="35" y="50" width="30" height="34" rx="14"/>`,`<circle cx="50" cy="66" r="15"/><path d="M32 60 28 40 42 52M68 60l4-20-14 12"/>`,`<ellipse cx="50" cy="66" rx="13" ry="17"/><path d="M34 54h32l-4-12H38z"/>`][head];
 const fl=flip?'translate(100 0) scale(-1 1)':'';
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 140" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><defs><linearGradient id="g${uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient><pattern id="p${uid}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="2.5" cy="2.5" r="1.1" fill="#000" fill-opacity=".22"/></pattern><radialGradient id="v${uid}" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient></defs><rect width="100" height="140" fill="url(#g${uid})"/><g fill="#fff" fill-opacity=".09" transform="${fl}">${ray}</g><g transform="translate(0 6) ${fl}" fill="${c3}" fill-opacity=".55" stroke="#fff" stroke-opacity=".55" stroke-width="1.2"><g transform="translate(14 4) scale(.72)">${E}</g></g><g transform="${fl}"><path d="M8 140c0-30 16-46 42-46s42 16 42 46z" fill="${dk}"/><path d="M8 140c0-30 16-46 42-46s42 16 42 46" fill="none" stroke="${c3}" stroke-width="1.6" stroke-opacity=".9"/><g fill="${dk}" stroke="${c3}" stroke-width="1.4" stroke-opacity=".9" transform="translate(0 6)">${H}</g></g><rect width="100" height="140" fill="url(#p${uid})"/><rect width="100" height="140" fill="url(#v${uid})"/></svg>`}
function artEl(c){const d=el('div','','art');if(PORT[c.id]){const i=document.createElement('img');i.src=PORT[c.id];i.alt='';i.decoding='async';i.onerror=()=>{d.innerHTML=artSvg(c)};d.append(i)}else d.innerHTML=artSvg(c);return d}
function nameBlock(c,withSub){const p=parts(c.name),nb=el('div','','nameb cmic '+lenCls(p.main));nb.append(el('h3',p.main));if(withSub&&p.sub)nb.append(el('small',p.sub));return nb}
function kard(c,o){o=o||{};const k=el('div','','kard '+tier(c));k.append(artEl(c));const co=el('div',val(c).toFixed(0),'coin');co.setAttribute('aria-label','Valore nello scenario '+val(c).toFixed(1));k.append(co);const rc=el('div','','rolechip');if(o.role){rc.title=RN[o.role];rc.append(roleSvg(o.role))}else if(o.role===null){rc.textContent='?';rc.title='Ruolo da assegnare'}else{const r=bestRole(c);rc.title=RN[r];rc.append(roleSvg(r))}k.append(rc,nameBlock(c,o.sub));return k}
function statBars(c){const w=el('div','','stats');STATS.forEach((k,i)=>{const r=el('div','','r'),bar=el('div','','bar'),f=el('i');f.style.width=c.stats[k]+'%';f.style.animationDelay=i*40+'ms';bar.append(f);r.append(el('span',SN[i].slice(0,3).toUpperCase()),bar,el('b',String(c.stats[k])));const fv=D.scenarios[scenario][i]>=FAVTH;if(fv)r.classList.add('fav');r.setAttribute('aria-label',SN[i]+' '+c.stats[k]+(fv?', favorita dallo scenario':''));w.append(r)});return w}
/* ================= schermata di scelta ================= */
let sel=null,rsel=null,fresh='';
function thumb(c){const p=parts(c.name),b=el('button');b.type='button';b.className='card th '+tier(c);b.dataset.id=c.id;const nm=el('span','','nm '+lenCls(p.main));nm.append(document.createTextNode(p.main));if(p.sub)nm.append(el('small',p.sub.split(' ')[0]));const rr=el('span','','rl2');rr.title=RN[bestRole(c)];rr.append(roleSvg(bestRole(c)));b.append(artEl(c),el('span',val(c).toFixed(0),'v'),rr,nm);const dd=r1(dlt(c));if(scenario!=='battleworld'&&Math.abs(dd)>=.5)b.append(el('span',sg(dd)+Math.round(Math.abs(dd)),'dl '+(dd>0?'up':'dn')));b.setAttribute('aria-label',c.name+', ruolo ideale '+RN[bestRole(c)]+', valore '+val(c).toFixed(1)+(scenario!=='battleworld'?', '+(dd>=0?'+':'−')+Math.abs(dd).toFixed(1)+' rispetto a Battleworld':''));b.setAttribute('aria-pressed','false');b.onclick=()=>choose(c);return b}
function choose(c){sel=c;for(const t of $('pool').children)t.setAttribute('aria-pressed',t.dataset.id===c.id?'true':'false');renderHero();upRecruit()}
function renderTray(box,team,cls,mark){box.replaceChildren();for(let i=0;i<5;i++){const s=el('div','','slot '+cls);if(team[i]){s.classList.add('on');s.append(artEl(team[i]));s.title=team[i].name;if(mark&&i===team.length-1)s.classList.add('new')}box.append(s)}}
function renderHero(){const h=$('hero');h.replaceChildren();if(!sel)return;const box=el('div','','herobox');const r=bestRole(sel);const rl=el('div','','role');rl.append(roleSvg(r),el('span','Ruolo ideale: '+RN[r]));const same=A.filter(x=>x.group===sel.group).length;const sy=el('div','','syn');sy.append(document.createTextNode('Sinergia con la tua squadra: '),el('b',same?'+'+same+'%':'nessuna'));box.append(el('div',sel.group,'grp'),rl,el('div','▲ '+RN[Core.BEATS[r]]+'  ▼ '+RN[ROLES.find(k=>Core.BEATS[k]===r)],'ctrl'),valRow(sel),whyBox(sel),statBars(sel),sy);h.append(kard(sel,{sub:true}),box)}
function whyBox(c){const r=bestRole(c),beat=Core.BEATS[r],w=el('div','','why'),add=(t,tone)=>w.append(el('span',t,'wy '+tone));const same=A.filter(x=>x.group===c.group).length;
 if(same)add('Sinergia +'+same+'%','up');if(!A.some(x=>bestRole(x)===r))add('Copre '+RN[r],'up');
 const O=B[A.length];if(O){const cc=Core.counter(r,bestRole(O));add('Sfida '+parts(O.name).main.split(' ')[0]+(cc>0?' ▲':cc<0?' ▼':''),cc>0?'up':cc<0?'dn':'')}else if(B.some(o=>bestRole(o)===beat))add('Batte '+RN[beat]+' CPU','up');
 let bi=0;STATS.forEach((k,i)=>{if(c.stats[k]*W()[i]>c.stats[STATS[bi]]*W()[bi])bi=i});if(W()[bi]>=.25)add('Forte in '+SN[bi],'up');
 if(!w.children.length)add('Profilo '+RN[r],'');while(w.children.length>3)w.lastChild.remove();w.setAttribute('aria-label','Perché sceglierlo: '+[...w.children].map(x=>x.textContent).join(', '));return w}
function valRow(c){const v=val(c),n=valN(c),d=r1(v-n),w=el('div','','valrow');if(scenario==='battleworld'){w.append(el('span',v.toFixed(0),'vb'),el('span','Scenario di riferimento','dl ref'));w.setAttribute('aria-label','Valore '+v.toFixed(1)+', scenario di riferimento');return w}
 const t=el('span',(d>0?'▲ ':d<0?'▼ ':'= ')+sg(d)+Math.abs(d).toFixed(1),'dl '+(d>0.05?'up':d<-0.05?'dn':'eq'));w.append(el('span',v.toFixed(0),'vb'),t,el('small','Battleworld '+n.toFixed(0),'ref'));w.setAttribute('aria-label','Valore '+SCN[scenario]+' '+v.toFixed(1)+', '+(d>=0?'+':'−')+Math.abs(d).toFixed(1)+' rispetto a Battleworld ('+n.toFixed(1)+')');return w}
function upRecruit(){const mine=phase==='draft'&&ORDER[turn]==='A';$('recruit').disabled=!(mine&&sel);$('rtxt').textContent=mine&&sel?'Recluta '+parts(sel.name).main:'Recluta'}
function renderDraft(){$('scnbn').replaceChildren(banner(scenario));$('order').replaceChildren(...[...ORDER].map((o,i)=>{const b=el('i','',o+(i<turn?'':' todo')+(i===turn?' cur':''));b.setAttribute('aria-label','Turno '+(i+1)+': '+(o==='A'?'tu':'CPU'));return b}));
 renderTray($('trme'),A,'me',fresh==='A');renderTray($('trcpu'),B,'cpu',fresh==='B');fresh='';
 const gr=$('pool');gr.replaceChildren();const sorted=[...offers];if(!sel||!offers.includes(sel))sel=sorted[0]||null;
 for(const c of sorted){const t=thumb(c);if(c===sel)t.setAttribute('aria-pressed','true');gr.append(t)}renderHero();upRecruit()}
/* ================= ruoli ================= */
function teamRow(box,team,m,me,opp,om){box.replaceChildren();const sc=total(team,m),hd=el('div','','hd');hd.append(el('h3',me?'La tua squadra':'Squadra CPU '+cpuLvl,'cmic'));const sm=el('div','','synm'),bar=el('div','','bar'),f=el('i');f.style.width=(sc.syn/.15*100)+'%';bar.append(f);sm.append(el('span','Sinergia '+(sc.syn*100).toFixed(0)+'%'),bar);hd.append(sm);box.append(hd);
 const row=el('div','','row5');for(const c of team){const rl=m[c.id]||null;const w=el(me?'button':'div','','rc');if(me){w.type='button';w.dataset.id=c.id;w.setAttribute('aria-pressed',rsel===c.id?'true':'false');w.setAttribute('aria-label',c.name+', '+(rl?'ruolo '+RN[rl]:'ruolo da assegnare')+(rsel===c.id?', selezionata':''));w.onclick=()=>{rsel=c.id;renderRoles()}}
  const ix=team.indexOf(c),oc=opp&&opp[ix],orl=me&&oc?bestRole(oc):null,cc=rl&&orl?Core.counter(rl,orl):0;const kd=kard(c,{role:me?(rl||null):null});kd.append(el('span',String(ix+1),'cn'));if(cc>0){kd.append(el('span','▲ +5%','cm'));w.classList.add('ctr')}else if(cc<0)kd.append(el('span','▼','cm bad'));w.append(kd,el('div',me?(rl?RN[rl]:'Da assegnare'):'Ruolo nascosto','rlab'));if(w.setAttribute&&me)w.setAttribute('aria-label',w.getAttribute('aria-label')+', scontro '+(ix+1)+(cc>0?', contromossa a tuo favore':cc<0?', contromossa a favore della CPU':''));row.append(w)}box.append(row)}
function assignRole(cid,r){const prev=assign[cid],other=Object.keys(assign).find(k=>assign[k]===r&&k!==cid);if(other){if(prev)assign[other]=prev;else delete assign[other]}assign[cid]=r;const nxt=A.find(c=>!assign[c.id]);if(nxt)rsel=nxt.id;persist();render()}
const RSH={avanguardia:'Avang.',stratega:'Strateg.',ricognitore:'Ricogn.',difensore:'Difens.',specialista:'Special.'};
function renderRoles(){if(!rsel||!A.some(c=>c.id===rsel))rsel=(A.find(c=>!assign[c.id])||A[0]).id;const cm=cpuAssign();teamRow($('tcpu2'),B,cm,false,A,assign);teamRow($('tme2'),A,assign,true,B,cm);
 const rb=$('roles');rb.replaceChildren();const cur=byId[rsel];rb.setAttribute('aria-label','Ruolo per '+cur.name);for(const r of ROLES){const b=el('button');b.type='button';b.className='rb';b.dataset.role=r;b.setAttribute('aria-pressed',assign[rsel]===r?'true':'false');b.append(roleSvg(r),el('span',RSH[r]));b.title=RN[r];const own=A.find(c=>c.id!==rsel&&assign[c.id]===r);if(own){b.append(el('span','↔ '+parts(own.name).main.split(/[\s-]/)[0],'used'));b.setAttribute('aria-label',RN[r]+' (in uso da '+own.name+': verranno scambiati)')}else b.setAttribute('aria-label',RN[r]);b.onclick=()=>assignRole(rsel,r);rb.append(b)}
 const full=Object.keys(assign).length===5&&new Set(Object.values(assign)).size===5;$('go').disabled=!full;
 const du=$('duel');du.replaceChildren(el('h4','Duello delle statistiche','cmic'));STATS.forEach((k,i)=>{const x=A.reduce((s,c)=>s+c.stats[k],0),y=B.reduce((s,c)=>s+c.stats[k],0),w=el('div','','');w.style.display='contents';const r=el('div','','r'),bar=el('div','','bar'),a=el('i'),b=el('i');a.style.width=x/(x+y)*100+'%';b.style.width=y/(x+y)*100+'%';bar.append(a,b);r.append(el('span',String(x)),bar,el('span',String(y)));w.append(el('div',SN[i],'lb'),r);du.append(w)})}
/* ================= battaglia ================= */
const reduce=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
const FXC={avanguardia:'<svg viewBox="0 0 100 100"><line x1="10" y1="85" x2="90" y2="15"/><line x1="25" y1="95" x2="95" y2="30"/><line x1="0" y1="70" x2="75" y2="5"/><circle cx="50" cy="50" r="30"/></svg>',
 stratega:'<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="30"/><polygon points="50,10 85,30 85,70 50,90 15,70 15,30"/><polygon points="50,10 85,30 85,70 50,90 15,70 15,30"/><polygon points="50,10 85,30 85,70 50,90 15,70 15,30"/></svg>',
 ricognitore:'<svg viewBox="0 0 100 100"><line x1="5" y1="20" x2="70" y2="20"/><line x1="0" y1="38" x2="85" y2="38"/><line x1="10" y1="55" x2="95" y2="55"/><line x1="0" y1="72" x2="75" y2="72"/><line x1="15" y1="88" x2="80" y2="88"/></svg>',
 difensore:'<svg viewBox="0 0 100 100"><path d="M50 8 14 22v26c0 22 15 36 36 44 21-8 36-22 36-44V22z"/><circle cx="50" cy="50" r="30"/></svg>',
 specialista:(()=>{let s='<svg viewBox="0 0 100 100">';for(let i=0;i<7;i++){const a=i*2*Math.PI/7,x=Math.round(Math.cos(a)*38),y=Math.round(Math.sin(a)*38);s+=`<path style="--sx:${x}px;--sy:${y}px" d="m50 40 3 7 8 1-6 5 2 8-7-4-7 4 2-8-6-5 8-1z"/>`}return s+'</svg>'})()};
const FXCLS={avanguardia:'lunge',stratega:'',ricognitore:'dash',difensore:'brace',specialista:''};
function playFx(wrap,role,side){const f=el('div','','fx fx-'+role);f.innerHTML=FXC[role];wrap.append(f);wrap.classList.add('fx'+side);if(FXCLS[role])wrap.classList.add(FXCLS[role])}
function cpuAssign(){return G.cpuAssign(cpuLvl,B,A,W(),Core.mulberry32(Core.hash32(seed+'|roles')))}
function compute(){const cm=cpuAssign(),r=G.clashes(A,assign,B,cm,W());return{x:r.x,y:r.y,xs:r.xs,ys:r.ys,cm,r}}
function strip(box,team){box.replaceChildren();team.forEach(c=>{const m=el('div','','m');m.append(artEl(c));box.append(m)})}
function runBattle(){clearTimer();buildArena();const cm=cpuAssign(),cl=G.clashes(A,assign,B,cm,W()),pa=cl.pa,pb=cl.pb,X=result.x,Y=result.y;
 strip($('bme'),A);strip($('bcpu'),B);const ma=[...$('bme').children],mb=[...$('bcpu').children];
 $('stage').querySelectorAll('.fcw').forEach(n=>n.remove());$('sa').textContent='0';$('sb').textContent='0';$('tugA').style.width='50%';$('cap').textContent='Le squadre entrano nell’arena';$('cap2').textContent=' ';$('vsb').style.opacity='1';
 const caps=['Primo scontro!','Contrattacco!','La strategia cambia!','Scontro decisivo!','Ultimo colpo!'],rd=reduce(),T=rd?700:BEAT_MS;let ra=0,rb=0,timers=[];const later=(f,ms)=>{const t=setTimeout(f,ms);timers.push(t);return t};
 const stop=()=>{timers.forEach(clearTimeout);timers=[]};
 function finish(){stop();phase='done';persist();render()}
 function beat(i){$('stage').querySelectorAll('.fcw').forEach(n=>n.remove());ma.forEach((m,j)=>m.classList.toggle('cur',j===i));mb.forEach((m,j)=>m.classList.toggle('cur',j===i));
  $('cap').textContent=caps[i];$('cap2').textContent=RN[assign[A[i].id]]+' contro '+RN[cm[B[i].id]];$('vsb').style.opacity='1';
  const L=el('div','','fcw l'),R=el('div','','fcw r');L.append(kard(A[i],{role:assign[A[i].id]}));R.append(kard(B[i],{role:cm[B[i].id]}));if(cl.ca[i]>0)L.append(el('div','▲ Contromossa','ctrb'));if(cl.cb[i]>0)R.append(el('div','▲ Contromossa','ctrb'));$('stage').insertBefore(L,$('stage').firstChild);$('stage').append(R);fitNames();
  later(()=>{ra+=pa[i];rb+=pb[i];const w=pa[i]>=pb[i];
   if(!rd){playFx(L,assign[A[i].id],'l');playFx(R,cm[B[i].id],'r');$('flash').classList.remove('on');void $('flash').offsetWidth;$('flash').classList.add('on');$('arena').classList.remove('shake');void $('arena').offsetWidth;$('arena').classList.add('shake')}
   L.classList.add(w?'win':'lose');R.classList.add(w?'lose':'win');$('vsb').style.opacity='0';impactFx(w);
   L.append(el('div',(w?'+':'')+pa[i].toFixed(0),'pts cmic'));R.append(el('div',(w?'':'+')+pb[i].toFixed(0),'pts cmic'));
   ma[i].classList.add(w?'won':'lost');mb[i].classList.add(w?'lost':'won');$('sa').textContent=ra.toFixed(0);$('sb').textContent=rb.toFixed(0);$('tugA').style.width=Math.max(8,Math.min(92,ra/(ra+rb)*100))+'%'},rd?60:620);
  later(()=>{if(i<BEATS-1)beat(i+1);else finish()},T)}
 $('skip').onclick=finish;timer=0;later(()=>beat(0),rd?60:600);
 clearTimer=(old=>function(){stop();old()})(clearTimerBase)}
const clearTimerBase=()=>{if(timer){clearInterval(timer);timer=null}};
/* ================= esito ================= */
function showResult(){const r=result,box=$('result');box.replaceChildren();const tie=Math.abs(r.x-r.y)<1e-9,win=r.x>r.y,wteam=win||tie?A:B,wm=win||tie?assign:cpuAssign();
 box.className='resv'+(win||tie?'':' lose');box.append(el('div','','rays'));
 if(!reduce()&&win){const cf=el('div','','conf');cf.setAttribute('aria-hidden','true');const cols=['#ffd28a','#33d1bd','#ff6f8d','#fff','#8fb4ff'];for(let i=0;i<18;i++){const p=el('i');p.style.cssText=`--x:${(i*5.7+3)%100}%;--c:${cols[i%5]};--d:${3.2+(i%4)*.7}s;--dl:${(i%6)*.35}s;--r:${(i*47)%360}deg`;cf.append(p)}box.append(cf)}
 box.append(el('div',tie?'Equilibrio perfetto':win?'Hai guidato i tuoi combattenti':'La CPU ha prevalso','kick'),el('h2',tie?'PAREGGIO':win?'VITTORIA!':'SCONFITTA','big cmic'));
 const fan=el('div','','fan');fan.setAttribute('role','img');fan.setAttribute('aria-label','Squadra vincitrice: '+wteam.map(c=>c.name).join(', '));wteam.forEach((c,i)=>{const k=kard(c,{role:wm[c.id]});k.style.setProperty('--dl',(i*.12)+'s');fan.append(k)});box.append(fan);
 const nm=el('p','','wnames');nm.append(el('b',tie?'La tua squadra: ':win?'La tua squadra: ':'Squadra CPU: '),document.createTextNode(wteam.map(c=>c.name).join(' · ')));box.append(nm);
 const sc=el('div','','sc cmic'),a=el('div','','a'),b=el('div','','b');a.append(document.createTextNode(r.x.toFixed(2)),el('small','TU'));b.append(document.createTextNode(r.y.toFixed(2)),el('small','CPU'));sc.append(a,el('span','–'),b);box.append(sc,el('p','Sinergie '+(r.xs*100).toFixed(0)+'% / '+(r.ys*100).toFixed(0)+'% · scenario '+SCN[scenario]+' · CPU '+cpuLvl,'note'));
 const dt=document.createElement('details'),sm=el('summary','Dettaglio del tuo punteggio'),t=el('table'),hd=el('tr');['Personaggio','Ruolo','Valore'].forEach(h=>hd.append(el('th',h)));t.append(hd);for(const c of A){const tr=el('tr'),rl=assign[c.id],i=ROLES.indexOf(rl),v=val(c)+c.stats[STATS[i]]*.08*W()[i];const ci=A.indexOf(c),cx=r.cb?G.counter(rl,cpuAssign()[B[ci].id]):0;tr.append(el('td',c.name),el('td',RN[rl]+(cx>0?' ▲':cx<0?' ▼':'')),el('td',(cx>0?v*(1+Core.CB):v).toFixed(1)));t.append(tr)}dt.append(sm,t);box.append(dt);
 const ac=el('div','','acts'),again=el('button','','btn gold');again.type='button';again.append(el('span','Nuova partita'));again.onclick=()=>{store.del(SAVE);newGame()};ac.append(again);box.append(ac)}
/* ================= render principale ================= */
function syncBar(){let h=0;for(const b of document.querySelectorAll('.actbar'))h=Math.max(h,Math.ceil(b.getBoundingClientRect().height));document.documentElement.style.setProperty('--barh',h+'px')}
addEventListener('resize',syncBar);addEventListener('orientationchange',syncBar);
function render(){const active=phase!=='idle';document.body.classList.toggle('playing',active);$('game').hidden=!active;$('scenario').disabled=$('cpu').disabled=phase==='draft'||phase==='roles'||phase==='cinematic';
 const sk0=phase==='idle'?$('scenario').value:scenario;document.body.dataset.s=sk0;if(phase==='idle')$('scnprev').replaceChildren(banner(sk0));else $('scnprev').replaceChildren();
 if(!active)return;
 const T1={draft:turn<10?'Turno ':'Draft',roles:'Assegna i ruoli',cinematic:'Battaglia',done:'Esito'}[phase];$('t1').replaceChildren(document.createTextNode(T1),...(phase==='draft'?[el('em',(turn+1)+'/10')]:[]));
 const used=Object.values(assign),dup=used.length!==new Set(used).size;
 $('status').textContent=phase==='draft'?(ORDER[turn]==='A'?'Tocca a te: scegli un combattente':'Turno CPU…'):phase==='roles'?(dup?'Ruolo duplicato: ogni ruolo va usato una sola volta':'Ruoli assegnati '+Object.keys(assign).length+'/5'):phase==='cinematic'?'Battaglia in corso':'Battaglia conclusa';
 $('scn').textContent=SCN[scenario];
 $('poolp').hidden=phase!=='draft';$('rolesp').hidden=phase!=='roles';$('battle').hidden=phase!=='cinematic';$('result').hidden=phase!=='done';
 if(phase==='draft')renderDraft();if(phase==='roles')renderRoles();if(phase==='done'&&result)showResult();window.scrollTo(0,0);fitNames()}
try{if(window.ResizeObserver){const ro=new ResizeObserver(syncBar);document.querySelectorAll('.actbar').forEach(b=>ro.observe(b))}}catch(x){}
function fitNames(){try{document.querySelectorAll('.nameb h3,.th .nm').forEach(function(e){e.style.fontSize='';var fs=parseFloat(getComputedStyle(e).fontSize),n=0;while(e.scrollWidth>e.clientWidth+1&&fs>6&&n++<12){fs-=.5;e.style.fontSize=fs+'px'}})}catch(x){}}
function battle(){if(phase!=='roles')return;const r=compute();result={x:r.x,y:r.y,xs:r.xs,ys:r.ys,cb:1};phase='cinematic';persist();render();runBattle()}

/* ================= Arene degli scenari (solo grafica: nessun effetto sul motore) ================= */
const SCNFX={asgard:{c1:'#f3c46a',c2:'#6b3fb5',n:14},wakanda:{c1:'#b58cff',c2:'#ffd36b',n:0},quantum:{c1:'#38e8e0',c2:'#ff4fd8',n:14},battleworld:{c1:'#ff8a2a',c2:'#c4342c',n:14}};
const srnd=i=>{const x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const poly=a=>a.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
function persp(y,f,vy){const w=(y-vy)*1.95+30;return 180+(f-.5)*w}
function sceneSvg(k,vb){const u='s'+(++UID),H=330;let o='',d='';
 if(k==='asgard'){
  d=`<linearGradient id="${u}a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060b24"/><stop offset=".3" stop-color="#241a58"/><stop offset=".47" stop-color="#8a4a7c"/><stop offset=".52" stop-color="#f6bd55"/><stop offset=".53" stop-color="#2a1d4d"/><stop offset="1" stop-color="#120c26"/></linearGradient><radialGradient id="${u}g" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".95"/><stop offset=".5" stop-color="#f6bd55" stop-opacity=".35"/><stop offset="1" stop-color="#f6bd55" stop-opacity="0"/></radialGradient><linearGradient id="${u}l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6c8" stop-opacity=".85"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></linearGradient><linearGradient id="${u}u" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3fe0b0" stop-opacity="0"/><stop offset=".5" stop-color="#7a8cff" stop-opacity=".5"/><stop offset="1" stop-color="#ff7be5" stop-opacity="0"/></linearGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/>`;
  for(let i=0;i<22;i++)o+=`<circle cx="${(srnd(i)*360).toFixed(0)}" cy="${(srnd(i+40)*210).toFixed(0)}" r="${(.5+srnd(i+7)*1.1).toFixed(1)}" fill="#fff" opacity="${(.4+srnd(i+3)*.5).toFixed(2)}"/>`;
  o+=`<path d="M-20 120 Q90 60 200 110 T380 70 L380 150 Q250 120 120 160 T-20 150Z" fill="url(#${u}u)" opacity=".55"/>`;
  o+=`<ellipse cx="180" cy="300" rx="190" ry="90" fill="url(#${u}g)"/>`;
  o+=`<path d="M0 ${H} L0 296 L40 280 L70 296 L110 270 L140 290 L220 290 L250 268 L290 292 L320 278 L360 296 L360 ${H}Z" fill="#35275f"/>`;
  o+=`<g fill="#2a1d4d"><rect x="132" y="240" width="96" height="90"/><rect x="146" y="206" width="68" height="40"/><path d="M146 206 L180 120 L214 206Z"/><path d="M104 330 L104 250 L118 214 L132 250 L132 330Z"/><path d="M228 330 L228 250 L242 214 L256 250 L256 330Z"/><path d="M60 330 L60 280 L70 258 L80 280 L80 330Z"/><path d="M280 330 L280 280 L290 258 L300 280 L300 330Z"/><circle cx="180" cy="208" r="22"/></g>`;
  o+=`<g stroke="#ffd36b" stroke-width="1.2" fill="none" opacity=".9"><path d="M180 120 L180 78"/><circle cx="180" cy="74" r="4" fill="#ffd36b"/><path d="M146 206 L214 206 M132 240 L228 240"/></g><g fill="#ffd36b"><rect x="168" y="256" width="5" height="9"/><rect x="187" y="256" width="5" height="9"/><rect x="150" y="256" width="5" height="9"/><rect x="205" y="256" width="5" height="9"/><rect x="176" y="190" width="8" height="8" rx="4"/></g>`;
  const cols=['#ff5d73','#ffb347','#f5e663','#5de0a0','#4aa8ff','#a77bff'];
  for(let s=0;s<6;s++){const f0=s/6,f1=(s+1)/6;o+=`<polygon points="${poly([[172+f0*16,H],[172+f1*16,H],[-70+f1*500,640],[-70+f0*500,640]])}" fill="${cols[s]}" opacity=".9"/>`}
  o+=`<path d="M170 ${H} L-72 640 M190 ${H} L432 640" stroke="#ffd36b" stroke-width="3" fill="none"/>`;
  for(let i=0;i<5;i++){const y=H+Math.pow(i/4,1.7)*300+14,x=persp(y,-.02,H)-4,x2=persp(y,1.02,H),s=3+i*2.2;o+=`<rect x="${(x-s).toFixed(1)}" y="${(y-s*4).toFixed(1)}" width="${(s*1.6).toFixed(1)}" height="${(s*4).toFixed(1)}" fill="#ffd36b"/><rect x="${x2.toFixed(1)}" y="${(y-s*4).toFixed(1)}" width="${(s*1.6).toFixed(1)}" height="${(s*4).toFixed(1)}" fill="#ffd36b"/>`}
  o+=`<rect x="120" y="0" width="120" height="${H+40}" fill="url(#${u}l)" class="beam"/>`;
  o+=`<ellipse cx="180" cy="${H+4}" rx="170" ry="9" fill="#fff" opacity=".18"/>`;
 }else if(k==='wakanda'){
  d=`<linearGradient id="${u}a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07061c"/><stop offset=".35" stop-color="#25104f"/><stop offset=".52" stop-color="#6b2fc0"/><stop offset=".53" stop-color="#150a30"/><stop offset="1" stop-color="#07041a"/></linearGradient><pattern id="${u}h" width="30" height="26" patternUnits="userSpaceOnUse"><path d="M15 0 L30 7.5 L30 18.5 L15 26 L0 18.5 L0 7.5Z" fill="none" stroke="#b58cff" stroke-width=".7" opacity=".4"/></pattern><radialGradient id="${u}o" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f1e2ff"/><stop offset=".35" stop-color="#a45cff" stop-opacity=".75"/><stop offset="1" stop-color="#a45cff" stop-opacity="0"/></radialGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/><rect width="360" height="${H}" fill="url(#${u}h)"/>`;
  o+=`<circle cx="180" cy="230" r="120" fill="url(#${u}o)" class="orb"/>`;
  o+=`<path d="M0 ${H} L0 262 L50 236 L96 262 L150 214 L206 258 L262 226 L318 258 L360 240 L360 ${H}Z" fill="#190d3a"/><path d="M0 262 L50 236 L96 262 L150 214 L206 258 L262 226 L318 258 L360 240" stroke="#a45cff" stroke-width="1.2" fill="none" opacity=".8"/>`;
  const tw=[[14,70],[38,110],[64,84],[96,128],[122,76],[238,92],[262,136],[292,86],[318,118],[340,74]];
  tw.forEach(([x,h],i)=>{o+=`<rect x="${x}" y="${H-h}" width="${18+(i%3)*5}" height="${h}" fill="#10082a"/><rect x="${x}" y="${H-h}" width="${18+(i%3)*5}" height="2" fill="#d9b8ff" opacity=".8"/>`;for(let j=0;j<h/14-1;j++)if(srnd(i*9+j)>.35)o+=`<rect x="${x+4+(j%2)*7}" y="${H-h+8+j*14}" width="3" height="3" fill="#c9a6ff" opacity=".85"/>`});
  o+=`<path d="M150 ${H} L150 190 M210 ${H} L210 176" stroke="#2b1660" stroke-width="10"/><circle cx="150" cy="186" r="8" fill="none" stroke="#ffd36b" stroke-width="2"/><circle cx="210" cy="172" r="8" fill="none" stroke="#ffd36b" stroke-width="2"/>`;
  o+=`<path d="M0 90 Q180 60 360 100 M0 120 Q180 90 360 130" stroke="#d9b8ff" stroke-width=".8" fill="none" opacity=".5"/><rect x="60" y="86" width="14" height="3" rx="1.5" fill="#fff" opacity=".9"/><rect x="250" y="100" width="14" height="3" rx="1.5" fill="#fff" opacity=".9"/>`;
  for(let i=-6;i<=6;i++)o+=`<path d="M${(180+i*4).toFixed(0)} ${H} L${(180+i*84).toFixed(0)} 640" stroke="#a45cff" stroke-width="1" opacity=".42"/>`;
  [0,.08,.18,.32,.5,.74,1].forEach(t=>{const y=H+8+t*300;o+=`<path d="M0 ${y.toFixed(0)} L360 ${y.toFixed(0)}" stroke="#a45cff" stroke-width="1" opacity="${(.2+t*.3).toFixed(2)}"/>`});
  o+=`<ellipse cx="180" cy="470" rx="170" ry="38" fill="none" stroke="#c89bff" stroke-width="2.4" opacity=".8"/><ellipse cx="180" cy="470" rx="112" ry="24" fill="none" stroke="#ffd36b" stroke-width="1.6" opacity=".75"/>`;
  for(let i=0;i<6;i++){const a=i*Math.PI/3;o+=`<path d="M${(180+Math.cos(a)*112).toFixed(0)} ${(470+Math.sin(a)*24).toFixed(0)} L${(180+Math.cos(a)*170).toFixed(0)} ${(470+Math.sin(a)*38).toFixed(0)}" stroke="#ffd36b" stroke-width="1.4" opacity=".7"/>`}
 }else if(k==='quantum'){
  d=`<radialGradient id="${u}a" cx=".5" cy=".47" r=".7"><stop offset="0" stop-color="#27408a"/><stop offset=".45" stop-color="#0b1038"/><stop offset="1" stop-color="#02020c"/></radialGradient><linearGradient id="${u}f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14386a" stop-opacity=".85"/><stop offset="1" stop-color="#03040f"/></linearGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/>`;
  for(let i=0;i<26;i++){const a=i/26*Math.PI*2;o+=`<path d="M180 270 L${(180+Math.cos(a)*400).toFixed(0)} ${(270+Math.sin(a)*400).toFixed(0)}" stroke="${i%2?'#38e8e0':'#ff4fd8'}" stroke-width=".7" opacity=".14"/>`}
  [[34,'#38e8e0',.95,'r1'],[62,'#ff4fd8',.7,'r2'],[96,'#38e8e0',.5,'r3'],[134,'#8a7bff',.4,'r1'],[178,'#ff4fd8',.28,'r2'],[230,'#38e8e0',.2,'r3']].forEach(([r,c,op,cl])=>{o+=`<circle cx="180" cy="270" r="${r}" fill="none" stroke="${c}" stroke-width="1.6" opacity="${op}" class="ring ${cl}" stroke-dasharray="${r>100?'8 10':'none'}"/>`});
  o+=`<g class="ring r3" opacity=".7"><path d="M180 270 m0 -26 a26 26 0 1 1 -26 26 a52 52 0 0 1 52 -52 a78 78 0 0 1 -78 78 a104 104 0 0 1 104 -104" fill="none" stroke="#fff" stroke-width="1"/></g>`;
  o+=`<circle cx="180" cy="270" r="9" fill="#fff"/><circle cx="180" cy="270" r="22" fill="#38e8e0" opacity=".25"/>`;
  o+=`<rect x="0" y="206" width="360" height="3" fill="#38e8e0" opacity=".25"/><rect x="24" y="214" width="330" height="2" fill="#ff4fd8" opacity=".25"/><rect x="0" y="330" width="300" height="2" fill="#38e8e0" opacity=".22"/>`;
  o+=`<rect x="0" y="360" width="360" height="280" fill="url(#${u}f)"/>`;
  for(let i=-8;i<=8;i++)o+=`<path d="M${(180+i*5).toFixed(0)} 360 L${(180+i*70).toFixed(0)} 640" stroke="#38e8e0" stroke-width=".9" opacity=".32"/>`;
  [0,.07,.16,.3,.5,.76,1].forEach(t=>{const y=364+t*276;o+=`<path d="M0 ${y.toFixed(0)} L360 ${y.toFixed(0)}" stroke="#38e8e0" stroke-width=".9" opacity="${(.15+t*.3).toFixed(2)}"/>`});
  [[34,'#38e8e0'],[62,'#ff4fd8'],[96,'#38e8e0']].forEach(([r,c],i)=>{o+=`<ellipse cx="180" cy="${470+i*8}" rx="${r*2.1}" ry="${r*.42}" fill="none" stroke="${c}" stroke-width="1.4" opacity="${(.5-i*.12).toFixed(2)}"/>`});
  for(let i=0;i<9;i++){const x=30+srnd(i)*300,y=60+srnd(i+9)*440,s=5+srnd(i+3)*10,c=i%2?'#38e8e0':'#ff4fd8';o+=`<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="${s.toFixed(0)}" height="${s.toFixed(0)}" fill="none" stroke="${c}" stroke-width="1.2" opacity=".7" transform="rotate(${(srnd(i+5)*70).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})" class="deb d${1+i%3}"/>`}
 }else{
  d=`<linearGradient id="${u}a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#190407"/><stop offset=".3" stop-color="#6f1814"/><stop offset=".5" stop-color="#ff7a24"/><stop offset=".51" stop-color="#2a0d08"/><stop offset="1" stop-color="#0f0504"/></linearGradient><radialGradient id="${u}s" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffe0a8"/><stop offset=".6" stop-color="#ff9a3a"/><stop offset="1" stop-color="#b02a14"/></radialGradient><linearGradient id="${u}r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a6050"/><stop offset="1" stop-color="#271a14"/></linearGradient><linearGradient id="${u}m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffa030"/><stop offset="1" stop-color="#8a1a0a"/></linearGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/>`;
  o+=`<circle cx="238" cy="200" r="78" fill="url(#${u}s)"/><circle cx="238" cy="200" r="110" fill="#ff9a3a" opacity=".18"/>`;
  o+=`<path d="M200 130 L226 176 L206 210 L240 250 M262 140 L248 190 L282 226" stroke="#3a0d08" stroke-width="3.5" fill="none"/><path d="M168 204 L214 214 L196 246Z M270 250 L300 226 L296 262Z" fill="#3a0d08"/>`;
  o+=`<g fill="url(#${u}r)" stroke="#ffb060" stroke-width=".8"><path d="M18 110 L74 92 L98 128 L62 156 L24 146Z" class="deb d1"/><path d="M290 70 L334 60 L348 92 L312 108Z" class="deb d2"/><path d="M110 40 L146 34 L156 62 L122 72Z" class="deb d3"/><path d="M30 214 L64 204 L76 236 L42 246Z" class="deb d2"/><path d="M286 300 L330 284 L348 314 L308 330Z" class="deb d1"/><path d="M96 262 L120 256 L128 276 L104 284Z" class="deb d3"/></g>`;
  o+=`<path d="M0 ${H} L0 296 L30 284 L58 304 L100 290 L150 308 L204 292 L252 310 L306 290 L340 302 L360 292 L360 ${H}Z" fill="#2a0d08"/>`;
  o+=`<rect x="0" y="${H}" width="360" height="310" fill="url(#${u}m)"/>`;
  const rows=[[340,376,7],[376,430,6],[430,520,5],[520,650,4]];
  rows.forEach(([y0,y1,n],ri)=>{for(let j=0;j<n;j++){const f0=j/n,f1=(j+1)/n,g=.012+ri*.004,j0=(srnd(ri*20+j)-.5)*.02;const p=[[persp(y0,f0+g+j0,H),y0+2],[persp(y0,f1-g+j0,H),y0+2],[persp(y1,f1-g-.012,H),y1-3],[persp(y1,f0+g-.012,H),y1-3]];o+=`<polygon points="${poly(p)}" fill="url(#${u}r)" stroke="#ffb060" stroke-width="${(.6+ri*.5).toFixed(1)}"/>`}});
  o+=`<path d="M178 ${H} L170 360 L184 398 L168 452 L190 520 L174 640" stroke="#fff2c0" stroke-width="1.4" fill="none" opacity=".8"/>`;
  for(let i=0;i<4;i++)o+=`<ellipse cx="${60+i*80}" cy="${H-2}" rx="60" ry="14" fill="#1a0806" opacity=".45"/>`;
 }
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb||'0 0 360 640'}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><defs>${d}</defs>${o}</svg>`}
const r1=x=>(x<0?-1:1)*Math.floor(Math.abs(x)*10+.5+1e-6)/10,FAVTH=.25,WN=()=>D.scenarios.battleworld;
const valN=c=>STATS.reduce((s,k,i)=>s+c.stats[k]*WN()[i],0),dlt=c=>val(c)-valN(c);
const favs=k=>D.scenarios[k].map((w,i)=>w>=FAVTH?i:-1).filter(i=>i>=0);
const sg=d=>d>0?'+':d<0?'−':'±';
function banner(k){const w=D.scenarios[k],f=favs(k),b=el('div','','scnban');b.dataset.s=k;const bg=el('div','','bg');bg.innerHTML=sceneSvg(k,'0 215 360 160');b.append(bg);
 const row=el('div','','r1'),nm=el('div','','nm cmic');nm.append(el('small','Scenario'),el('b',SCN[k]));row.append(nm);const ch=el('div','','chips');
 if(f.length)f.forEach(i=>{const c=el('span','','chip');c.append(document.createTextNode(SN[i]+' '),el('b',Math.round(w[i]*100)+'%'));ch.append(c)});else{const c=el('span','','chip eq');c.append(document.createTextNode('Tutte '),el('b','20%'));ch.append(c)}
 row.append(ch);
 const tx=f.length?'Pesano di più '+f.map(i=>SN[i]).join(', ').replace(/, ([^,]*)$/,' e $1')+': il valore carta è la somma delle statistiche per il loro peso.':'Ogni statistica pesa uguale: conta la media. Riferimento per i confronti \u25b2\u25bc.';
 b.append(row,el('p',tx,'ex'));if(f.length)b.append(el('p','▲▼ sulle carte: differenza di valore rispetto a Battleworld.','lg'));
 b.setAttribute('role','note');b.setAttribute('aria-label','Scenario '+SCN[k]+'. '+tx);return b}
function buildArena(){const k=scenario,ar=$('arena');ar.dataset.s=k;$('scene').innerHTML=sceneSvg(k);const fx=$('fxl');fx.replaceChildren();if(!reduce())for(let i=0;i<SCNFX[k].n;i++){const u=el('u');u.style.cssText=`--i:${i};--x:${(i*37+srnd(i)*20)%100}%;--d:${3+(i%5)*.9}s;--s:${2+(i%3)}px`;fx.append(u)}
 $('spot').className='spot';$('amb').className='amb'}
function impactFx(winL){const sp=$('spot');sp.className='spot on '+(winL?'l':'r');if(reduce())return;const a=$('amb');a.classList.remove('go');void a.offsetWidth;a.classList.add('go')}

/* ================= animazione di reclutamento (breve, saltata con riduzione movimento) ================= */
let recruiting=false;
function recruit(){if(recruiting||phase!=='draft'||!sel||ORDER[turn]!=='A')return;const c=sel;
 const fin=()=>{recruiting=false;sel=null;fresh='A';pick(c)};
 const hero=document.querySelector('#hero .kard'),slot=$('trme').children[A.length];
 if(reduce()||!hero||!slot||!hero.animate){fin();return}
 recruiting=true;$('recruit').disabled=true;const a=hero.getBoundingClientRect(),b=slot.getBoundingClientRect();
 const f=hero.cloneNode(true);f.classList.add('fly');f.setAttribute('aria-hidden','true');f.style.cssText=`left:${a.left}px;top:${a.top}px;width:${a.width}px;height:${a.height}px`;document.body.append(f);
 const dx=b.left+b.width/2-(a.left+a.width/2),dy=b.top+b.height/2-(a.top+a.height/2),s=b.width/a.width;
 const an=f.animate([{transform:'translate(0,0) scale(1) rotate(0)',offset:0},{transform:`translate(${dx*.25}px,${dy*.25-36}px) scale(1.14) rotate(-5deg)`,filter:'brightness(1.55) saturate(1.3)',offset:.3},{transform:`translate(${dx}px,${dy}px) scale(${s}) rotate(0)`,filter:'brightness(1)',offset:1}],{duration:560,easing:'cubic-bezier(.35,.75,.3,1)',fill:'forwards'});
 let done=false;const end=()=>{if(done)return;done=true;f.remove();const x=el('div','','burst');x.setAttribute('aria-hidden','true');x.style.cssText=`left:${b.left+b.width/2}px;top:${b.top+b.height/2}px`;for(let i=0;i<8;i++){const p=el('i');p.style.setProperty('--a',i*45+'deg');x.append(p)}document.body.append(x);setTimeout(()=>x.remove(),650);fin()};
 an.onfinish=end;btimers.push(setTimeout(end,900))}
