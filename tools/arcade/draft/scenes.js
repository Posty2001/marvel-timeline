/* ================= Arene degli scenari (solo grafica: nessun effetto sul motore) ================= */
const SCNFX={asgard:{c1:'#f3c46a',c2:'#6b3fb5',n:14},wakanda:{c1:'#b58cff',c2:'#ffd36b',n:0},quantum:{c1:'#38e8e0',c2:'#ff4fd8',n:14},battleworld:{c1:'#ff8a2a',c2:'#c4342c',n:14}};
const rnd=i=>{const x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const poly=a=>a.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
function persp(y,f,vy){const w=(y-vy)*1.95+30;return 180+(f-.5)*w}
function sceneSvg(k,vb){const u='s'+(++UID),H=330;let o='',d='';
 if(k==='asgard'){
  d=`<linearGradient id="${u}a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060b24"/><stop offset=".3" stop-color="#241a58"/><stop offset=".47" stop-color="#8a4a7c"/><stop offset=".52" stop-color="#f6bd55"/><stop offset=".53" stop-color="#2a1d4d"/><stop offset="1" stop-color="#120c26"/></linearGradient><radialGradient id="${u}g" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".95"/><stop offset=".5" stop-color="#f6bd55" stop-opacity=".35"/><stop offset="1" stop-color="#f6bd55" stop-opacity="0"/></radialGradient><linearGradient id="${u}l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6c8" stop-opacity=".85"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></linearGradient><linearGradient id="${u}u" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3fe0b0" stop-opacity="0"/><stop offset=".5" stop-color="#7a8cff" stop-opacity=".5"/><stop offset="1" stop-color="#ff7be5" stop-opacity="0"/></linearGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/>`;
  for(let i=0;i<22;i++)o+=`<circle cx="${(rnd(i)*360).toFixed(0)}" cy="${(rnd(i+40)*210).toFixed(0)}" r="${(.5+rnd(i+7)*1.1).toFixed(1)}" fill="#fff" opacity="${(.4+rnd(i+3)*.5).toFixed(2)}"/>`;
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
  tw.forEach(([x,h],i)=>{o+=`<rect x="${x}" y="${H-h}" width="${18+(i%3)*5}" height="${h}" fill="#10082a"/><rect x="${x}" y="${H-h}" width="${18+(i%3)*5}" height="2" fill="#d9b8ff" opacity=".8"/>`;for(let j=0;j<h/14-1;j++)if(rnd(i*9+j)>.35)o+=`<rect x="${x+4+(j%2)*7}" y="${H-h+8+j*14}" width="3" height="3" fill="#c9a6ff" opacity=".85"/>`});
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
  for(let i=0;i<9;i++){const x=30+rnd(i)*300,y=60+rnd(i+9)*440,s=5+rnd(i+3)*10,c=i%2?'#38e8e0':'#ff4fd8';o+=`<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="${s.toFixed(0)}" height="${s.toFixed(0)}" fill="none" stroke="${c}" stroke-width="1.2" opacity=".7" transform="rotate(${(rnd(i+5)*70).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})" class="deb d${1+i%3}"/>`}
 }else{
  d=`<linearGradient id="${u}a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#190407"/><stop offset=".3" stop-color="#6f1814"/><stop offset=".5" stop-color="#ff7a24"/><stop offset=".51" stop-color="#2a0d08"/><stop offset="1" stop-color="#0f0504"/></linearGradient><radialGradient id="${u}s" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffe0a8"/><stop offset=".6" stop-color="#ff9a3a"/><stop offset="1" stop-color="#b02a14"/></radialGradient><linearGradient id="${u}r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a6050"/><stop offset="1" stop-color="#271a14"/></linearGradient><linearGradient id="${u}m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffa030"/><stop offset="1" stop-color="#8a1a0a"/></linearGradient>`;
  o+=`<rect width="360" height="640" fill="url(#${u}a)"/>`;
  o+=`<circle cx="238" cy="200" r="78" fill="url(#${u}s)"/><circle cx="238" cy="200" r="110" fill="#ff9a3a" opacity=".18"/>`;
  o+=`<path d="M200 130 L226 176 L206 210 L240 250 M262 140 L248 190 L282 226" stroke="#3a0d08" stroke-width="3.5" fill="none"/><path d="M168 204 L214 214 L196 246Z M270 250 L300 226 L296 262Z" fill="#3a0d08"/>`;
  o+=`<g fill="url(#${u}r)" stroke="#ffb060" stroke-width=".8"><path d="M18 110 L74 92 L98 128 L62 156 L24 146Z" class="deb d1"/><path d="M290 70 L334 60 L348 92 L312 108Z" class="deb d2"/><path d="M110 40 L146 34 L156 62 L122 72Z" class="deb d3"/><path d="M30 214 L64 204 L76 236 L42 246Z" class="deb d2"/><path d="M286 300 L330 284 L348 314 L308 330Z" class="deb d1"/><path d="M96 262 L120 256 L128 276 L104 284Z" class="deb d3"/></g>`;
  o+=`<path d="M0 ${H} L0 296 L30 284 L58 304 L100 290 L150 308 L204 292 L252 310 L306 290 L340 302 L360 292 L360 ${H}Z" fill="#2a0d08"/>`;
  o+=`<rect x="0" y="${H}" width="360" height="310" fill="url(#${u}m)"/>`;
  const rows=[[340,376,7],[376,430,6],[430,520,5],[520,650,4]];
  rows.forEach(([y0,y1,n],ri)=>{for(let j=0;j<n;j++){const f0=j/n,f1=(j+1)/n,g=.012+ri*.004,j0=(rnd(ri*20+j)-.5)*.02;const p=[[persp(y0,f0+g+j0,H),y0+2],[persp(y0,f1-g+j0,H),y0+2],[persp(y1,f1-g-.012,H),y1-3],[persp(y1,f0+g-.012,H),y1-3]];o+=`<polygon points="${poly(p)}" fill="url(#${u}r)" stroke="#ffb060" stroke-width="${(.6+ri*.5).toFixed(1)}"/>`}});
  o+=`<path d="M178 ${H} L170 360 L184 398 L168 452 L190 520 L174 640" stroke="#fff2c0" stroke-width="1.4" fill="none" opacity=".8"/>`;
  for(let i=0;i<4;i++)o+=`<ellipse cx="${60+i*80}" cy="${H-2}" rx="60" ry="14" fill="#1a0806" opacity=".45"/>`;
 }
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb||'0 0 360 640'}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><defs>${d}</defs>${o}</svg>`}
const FAVTH=.25,WN=()=>D.scenarios.battleworld;
const valN=c=>STATS.reduce((s,k,i)=>s+c.stats[k]*WN()[i],0),dlt=c=>val(c)-valN(c);
const favs=k=>D.scenarios[k].map((w,i)=>w>=FAVTH?i:-1).filter(i=>i>=0);
const sg=d=>d>0?'+':d<0?'−':'±';
function banner(k){const w=D.scenarios[k],f=favs(k),b=el('div','','scnban');b.dataset.s=k;const bg=el('div','','bg');bg.innerHTML=sceneSvg(k,'0 215 360 160');b.append(bg);
 const row=el('div','','r1'),nm=el('div','','nm cmic');nm.append(el('small','Scenario'),el('b',SCN[k]));row.append(nm);const ch=el('div','','chips');
 if(f.length)f.forEach(i=>{const c=el('span','','chip');c.append(document.createTextNode(SN[i]+' '),el('b',Math.round(w[i]*100)+'%'));ch.append(c)});else{const c=el('span','','chip eq');c.append(document.createTextNode('Tutte '),el('b','20%'));ch.append(c)}
 row.append(ch);
 const tx=f.length?'Pesano di più '+f.map(i=>SN[i]).join(', ').replace(/, ([^,]*)$/,' e $1')+': il valore carta è la somma delle statistiche per il loro peso.':'Ogni statistica pesa uguale: conta la media. È il riferimento per i ▲▼.';
 b.append(row,el('p',tx,'ex'));if(f.length)b.append(el('p','▲▼ sulle carte: differenza di valore rispetto a Battleworld.','lg'));
 b.setAttribute('role','note');b.setAttribute('aria-label','Scenario '+SCN[k]+'. '+tx);return b}
function buildArena(){const k=scenario,ar=$('arena');ar.dataset.s=k;$('scene').innerHTML=sceneSvg(k);const fx=$('fxl');fx.replaceChildren();if(!reduce())for(let i=0;i<SCNFX[k].n;i++){const u=el('u');u.style.cssText=`--i:${i};--x:${(i*37+rnd(i)*20)%100}%;--d:${3+(i%5)*.9}s;--s:${2+(i%3)}px`;fx.append(u)}
 $('spot').className='spot';$('amb').className='amb'}
function impactFx(winL){const sp=$('spot');sp.className='spot on '+(winL?'l':'r');if(reduce())return;const a=$('amb');a.classList.remove('go');void a.offsetWidth;a.classList.add('go')}
