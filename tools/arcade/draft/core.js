/* Secret Wars Draft 3.0 — nucleo di gioco puro (nessun DOM). Usato identico dal gioco e dalle simulazioni Node. */
(function(root){
'use strict';
const ORDER='ABBAABBAAB',STATS=['power','intelligence','speed','durability','versatility'],ROLES=['avanguardia','stratega','ricognitore','difensore','specialista'];
/* Contromosse: ogni ruolo ne batte esattamente uno e cede a uno (pentagono). Bonus limitato, solo a chi ha il vantaggio. */
const BEATS={difensore:'avanguardia',avanguardia:'specialista',specialista:'stratega',stratega:'ricognitore',ricognitore:'difensore'};
const CB=0.05,BAND=5,MINC=7,MAXW=14;
function hash32(s){let h=2166136261>>>0;s=String(s);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}h^=h>>>13;h=Math.imul(h,0x5bd1e995);h^=h>>>15;return h>>>0}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const counter=(a,b)=>BEATS[a]===b?1:BEATS[b]===a?-1:0;
function perms(n,k){const out=[];(function rec(cur,used){if(cur.length===k){out.push(cur.slice());return}for(let i=0;i<n;i++)if(!used.has(i)){used.add(i);cur.push(i);rec(cur,used);cur.pop();used.delete(i)}})([],new Set());return out}
const PERM={};
function make(D){
 const byId=Object.fromEntries(D.roster.map(c=>[c.id,c]));
 const val=(c,w)=>STATS.reduce((s,k,i)=>s+c.stats[k]*w[i],0);
 const ideal=c=>{let bi=0;STATS.forEach((k,i)=>{if(c.stats[k]>c.stats[STATS[bi]])bi=i});return ROLES[bi]};
 function synergy(t){let p=0;for(let i=0;i<t.length;i++)for(let j=i+1;j<t.length;j++)if(t[i].group===t[j].group)p++;return Math.min(.15,p*.01)}
 const roleBonus=(c,role,w)=>{const i=ROLES.indexOf(role);return i<0?0:c.stats[STATS[i]]*.08*w[i]};
 function total(t,m,w){const base=t.reduce((s,c)=>s+val(c,w),0),bonus=t.reduce((s,c)=>s+roleBonus(c,m[c.id],w),0);return{base,bonus,syn:synergy(t),score:(base+bonus)*(1+synergy(t))}}
 function bestAssign(team,w){const k=team.length;if(!k)return{map:{},score:0};PERM[k]=PERM[k]||perms(5,k);let best=null;for(const p of PERM[k]){const m={};team.forEach((c,i)=>m[c.id]=ROLES[p[i]]);const s=total(team,m,w).score;if(!best||s>best.score)best={map:m,score:s}}return best}
 /* Scontro i: la i-esima carta reclutata da A contro la i-esima di B. Punteggio = (valore+bonus ruolo)·(1+sinergia)·(1+contromossa). */
 function clashes(A,mA,B,mB,w,cb){cb=cb===undefined?CB:cb;const sa=1+synergy(A),sb=1+synergy(B),pa=[],pb=[],ca=[],cbk=[];
  for(let i=0;i<A.length;i++){const ra=mA[A[i].id],rb=mB[B[i].id],c=counter(ra,rb);ca.push(c);cbk.push(-c);
   pa.push((val(A[i],w)+roleBonus(A[i],ra,w))*sa*(c>0?1+cb:1));pb.push((val(B[i],w)+roleBonus(B[i],rb,w))*sb*(c<0?1+cb:1))}
  const x=pa.reduce((s,v)=>s+v,0),y=pb.reduce((s,v)=>s+v,0);return{pa,pb,ca,cb:cbk,x,y,xs:sa-1,ys:sb-1}}
 /* Offerte: 5 candidati da una fascia di valore (nello scenario) di ampiezza ~5 punti, ampliata solo se mancano candidati.
    Deterministiche da (seed, turno, reclutati) — nessuna rigenerazione gratuita, nessuna informazione sulle offerte future. */
 function offers(drafted,w,seed,turn,mine,opp){
  const rng=mulberry32(hash32(seed+'|o|'+turn)),av=D.roster.filter(c=>!drafted.has(c.id)),v=new Map(av.map(c=>[c.id,val(c,w)]));
  const a=av[Math.floor(rng()*av.length)],va=v.get(a.id);let width=BAND,lo=va-rng()*BAND,cand;
  for(;;){cand=av.filter(c=>{const x=v.get(c.id);return x>=lo-1e-9&&x<=lo+width+1e-9});if(cand.length>=MINC||width>=MAXW)break;width+=1;lo-=.5}
  if(cand.length<5){cand=[...av].sort((p,q)=>Math.abs(v.get(p.id)-va)-Math.abs(v.get(q.id)-va)||(p.id<q.id?-1:1)).slice(0,Math.max(5,MINC));width=Math.max(...cand.map(c=>v.get(c.id)))-Math.min(...cand.map(c=>v.get(c.id)))}
  const myG=new Set(mine.map(c=>c.group)),oppR=new Set(opp.map(ideal)),want=new Set(ROLES.filter(r=>[...oppR].some(o=>BEATS[r]===o)));
  const S=[a],rest=cand.filter(c=>c!==a);
  while(S.length<5){const roles=new Set(S.map(ideal)),groups=new Set(S.map(c=>c.group)),hasSyn=S.some(c=>myG.has(c.group)),hasCtr=S.some(c=>want.has(ideal(c)));let bi=-1,bs=-1e9;
   rest.forEach((c,i)=>{const r=ideal(c);const s=(roles.has(r)?0:3)+(groups.has(c.group)?0:1)+(!hasSyn&&myG.has(c.group)?2.5:0)+(!hasCtr&&want.has(r)?1.5:0)+rng()*1.2-.15*Math.abs(v.get(c.id)-va);if(s>bs){bs=s;bi=i}});
   S.push(rest.splice(bi,1)[0])}
  S.sort((p,q)=>v.get(q.id)-v.get(p.id)||(p.id<q.id?-1:1));const vs=S.map(c=>v.get(c.id));
  return{list:S,spread:Math.max(...vs)-Math.min(...vs),width,anchor:a.id,roles:new Set(S.map(ideal)).size}}
 /* CPU: sceglie solo tra le 5 offerte del proprio turno. recluta=casuale pesato; stratega=squadra migliore (ruoli+sinergie); maestro=anche contromosse previste sul prossimo avversario noto. */
 function cpuChoose(level,off,mine,opp,w,rng){
  const sorted=[...off].sort((p,q)=>val(q,w)-val(p,w));
  if(level==='recluta'){const wt=sorted.map((_,i)=>sorted.length-i),sum=wt.reduce((a,b)=>a+b,0);let r=rng()*sum;for(let i=0;i<sorted.length;i++){r-=wt[i];if(r<0)return sorted[i]}return sorted[0]}
  let best=null,bs=-1e9;const k=mine.length,O=opp[k];
  for(const c of off){let s=bestAssign([...mine,c],w).score;
   if(level==='stratega')s+=(rng()-.5)*6;
   else if(O){const cc=counter(ideal(c),ideal(O));s+=cc*CB*val(c,w)}
   if(s>bs){bs=s;best=c}}
  return best}
 /* Ruoli CPU (nascosti al giocatore fino alla battaglia, deterministici da seed+squadre): si sceglie tra le migliori assegnazioni con pesi per livello.
    recluta=tra le 8 migliori della propria squadra; stratega=tra le 4 migliori; maestro=tra le 3 migliori per esito atteso contro i ruoli ideali previsti del giocatore. */
 function cpuAssign(level,B,A,w,rng){PERM[5]=PERM[5]||perms(5,5);if(B.length<5)return bestAssign(B,w).map;rng=rng||(()=>.5);
  const pm=level==='maestro'&&A.length===5?bestAssign(A,w).map:null,ps=PERM[5].map(p=>{const m={};B.forEach((c,i)=>m[c.id]=ROLES[p[i]]);let s=total(B,m,w).score;if(pm){const o=clashes(A,pm,B,m,w);s=o.y-o.x}return{m,s}}).sort((x,y)=>y.s-x.s);
  const K={recluta:8,stratega:4,maestro:3}[level]||1,wt={recluta:[1,1,1,1,1,1,1,1],stratega:[4,3,2,1],maestro:[5,3,1]}[level]||[1],sum=wt.reduce((a,b)=>a+b,0);let r=rng()*sum;for(let i=0;i<K;i++){r-=wt[i];if(r<0)return ps[i].m}return ps[0].m}
 /* Giocatore informato: sceglie i ruoli migliori conoscendo i ruoli CPU (come nel gioco, dove i ruoli CPU sono visibili). */
 function playerAssign(A,B,mB,w){PERM[5]=PERM[5]||perms(5,5);let best=null,bs=-1e9;for(const p of PERM[5]){const m={};A.forEach((c,i)=>m[c.id]=ROLES[p[i]]);const o=clashes(A,m,B,mB,w);const s=o.x-o.y;if(s>bs){bs=s;best=m}}return best}
 /* Bot giocatore per le simulazioni */
 function botChoose(policy,off,mine,opp,w,rng,level){
  if(policy==='random')return off[Math.floor(rng()*off.length)];
  if(policy==='greedy')return [...off].sort((p,q)=>val(q,w)-val(p,w))[0];
  return cpuChoose(policy==='smart'?'maestro':policy,off,mine,opp,w,rng)}
 /* Draft completo: restituisce offerte, scelte, squadre ed esito */
 function play(o){const w=D.scenarios[o.scenario],seed=o.seed,A=[],B=[],drafted=new Set(),log=[],roles=o.roles||'guess';
  for(let t=0;t<10;t++){const side=ORDER[t],mine=side==='A'?A:B,opp=side==='A'?B:A,off=offers(drafted,w,seed,t,mine,opp);
   const ch=side==='A'?botChoose(o.player.startsWith('m:')?o.player.slice(2):o.player,off.list,mine,opp,w,mulberry32(hash32(seed+'|p|'+t))):cpuChoose(o.cpu,off.list,mine,opp,w,mulberry32(hash32(seed+'|c|'+t)));
   mine.push(ch);drafted.add(ch.id);log.push({t,side,off:off.list.map(c=>c.id),pick:ch.id,spread:off.spread,width:off.width,roles:off.roles})}
  const mir=o.player.startsWith('m:'),mB=cpuAssign(o.cpu,B,A,w,mulberry32(hash32(seed+'|roles')));
  const mA=mir?cpuAssign(o.cpu,A,B,w,mulberry32(hash32(seed+'|rolesA'))):roles==='blind'?bestAssign(A,w).map:roles==='leak'?playerAssign(A,B,mB,w):playerAssign(A,B,bestAssign(B,w).map,w);
  const r=clashes(A,mA,B,mB,w),r0=clashes(A,mA,B,mB,w,0);
  return{A,B,mA,mB,log,res:r,win:r.x>r.y?1:r.x<r.y?-1:0,flip:(r.x>r.y)!==(r0.x>r0.y)}}
 return{byId,val,ideal,synergy,roleBonus,total,bestAssign,clashes,offers,cpuChoose,cpuAssign,playerAssign,botChoose,play,counter}}
const api={ORDER,STATS,ROLES,BEATS,CB,BAND,MINC,MAXW,hash32,mulberry32,counter,make};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.Core=api;
})(typeof self!=='undefined'?self:this);
