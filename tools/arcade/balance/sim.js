// Simulazioni di bilanciamento del Draft 3.0 — usa il nucleo REALE (core.js) e il roster REALE (roster.json). Seed riproducibili.
const fs=require('fs'),C=require('./core.js'),R=require('./roster.json');
const SCN={asgard:[.3,.1,.15,.3,.15],wakanda:[.15,.3,.1,.2,.25],quantum:[.1,.25,.3,.1,.25],battleworld:[.2,.2,.2,.2,.2]},LV=['recluta','stratega','maestro'];
const D={roster:R,scenarios:SCN},g=C.make(D),N1=+process.argv[2]||900,N2=+process.argv[3]||300,tag=process.argv[4]||'v3';
const out={meta:{roster:R.length,N_main_per_cell:N1,N_other_per_cell:N2,seedPrefix:tag,cb:C.CB,band:C.BAND},sets:{}};
const pct=(a,p)=>{const s=[...a].sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.floor(s.length*p))]};
const agg={games:0,dup:0,badOffers:0,badSnake:0,offersN:0,spreadAll:[],widened:0,roles:[],groups:[],flips:0,over5:0};
const charStat={};R.forEach(c=>charStat[c.id]={offered:0,picked:0,games:0,wins:0,pickedGreedyRank:0});
function runSet(name,player,N,collect,roles){const rows=[];
 for(const sc of Object.keys(SCN))for(const lv of LV){let win=0,loss=0,tie=0,flip=0,margin=0;
  for(let i=0;i<N;i++){const seed=`${tag}|${name}|${sc}|${lv}|${i}`,r=g.play({scenario:sc,seed,player,cpu:lv,roles});
   if(r.win>0)win++;else if(r.win<0)loss++;else tie++;if(r.flip)flip++;margin+=(r.res.x-r.res.y);
   agg.games++;const ids=[...r.A,...r.B].map(c=>c.id);if(new Set(ids).size!==10)agg.dup++;
   if(r.A.length!==5||r.B.length!==5||r.log.map(l=>l.side).join('')!==C.ORDER)agg.badSnake++;
   const seen=new Set();for(const l of r.log){agg.offersN++;if(l.off.length!==5||new Set(l.off).size!==5||l.off.some(id=>seen.has(id)||!g.byId[id]))agg.badOffers++;
    if(l.off.includes(l.pick)===false)agg.badOffers++;agg.spreadAll.push(l.spread);if(l.width>C.BAND)agg.widened++;if(l.spread>C.BAND+1e-9)agg.over5++;agg.roles.push(l.roles);
    seen.add(l.pick);}
   if(collect){for(const l of r.log){for(const id of l.off)charStat[id].offered++;if(l.side==='A')charStat[l.pick].picked++}
    for(const c of r.A){charStat[c.id].games++;if(r.win>0)charStat[c.id].wins++}}}
  rows.push({scenario:sc,cpu:lv,n:N,winPct:+(100*win/N).toFixed(1),lossPct:+(100*loss/N).toFixed(1),tiePct:+(100*tie/N).toFixed(2),flipPct:+(100*flip/N).toFixed(1),avgMargin:+(margin/N).toFixed(1)})}
 out.sets[name]={player,rows};return rows}
runSet('principale_scelte_esperte_ruoli_ipotizzati','smart',N1,true,'guess');
runSet('scelte_esperte_ruoli_alla_cieca','smart',N2,false,'blind');
runSet('scelte_valore_massimo','greedy',N2,false,'blind');
runSet('scelte_casuali','random',N2,false,'blind');
runSet('LIMITE_SUPERIORE_ruoli_CPU_noti_(non_disponibile_nel_gioco)','smart',N2,false,'leak');
for(const lv of LV){const rows=[];for(const sc of Object.keys(SCN)){let w=0,l=0;for(let i=0;i<N2;i++){const r=g.play({scenario:sc,seed:`${tag}|mir|${sc}|${lv}|${i}`,player:'m:'+lv,cpu:lv});agg.games++;if(r.win>0)w++;else if(r.win<0)l++}rows.push({scenario:sc,cpu:lv,aWinPct:+(100*w/N2).toFixed(1),bWinPct:+(100*l/N2).toFixed(1)})}out.sets['specchio_'+lv]={rows}}
// riproducibilità: stessa partita due volte
const a=g.play({scenario:'wakanda',seed:'rep',player:'smart',cpu:'maestro'}),b=g.play({scenario:'wakanda',seed:'rep',player:'smart',cpu:'maestro'});
out.riproducibile=JSON.stringify(a.log)===JSON.stringify(b.log)&&a.res.x===b.res.x;
out.aggregato={draftSimulati:agg.games,duplicati:agg.dup,offerteNonValide:agg.badOffers,snakeErrati:agg.badSnake,offerteTotali:agg.offersN,spread:{mediana:+pct(agg.spreadAll,.5).toFixed(2),p90:+pct(agg.spreadAll,.9).toFixed(2),p99:+pct(agg.spreadAll,.99).toFixed(2),max:+agg.spreadAll.reduce((m,x)=>x>m?x:m,0).toFixed(2),entro5Pct:+(100*(1-agg.over5/agg.offersN)).toFixed(2),ampliatePct:+(100*agg.widened/agg.offersN).toFixed(2)},ruoliDistintiPerOfferta:+(agg.roles.reduce((s,x)=>s+x,0)/agg.roles.length).toFixed(2)};
const base=out.sets.principale_scelte_esperte_ruoli_ipotizzati.rows;const tot=base.reduce((s,r)=>s+r.winPct,0)/base.length;
const cs=Object.entries(charStat).map(([id,s])=>({id,name:g.byId[id].name,offered:s.offered,picked:s.picked,pickRate:+(s.picked/Math.max(1,s.offered)).toFixed(3),games:s.games,winPct:+(100*s.wins/Math.max(1,s.games)).toFixed(1)}));
const meanPick=cs.reduce((s,c)=>s+c.pickRate,0)/cs.length,meanWin=cs.reduce((s,c)=>s+c.winPct,0)/cs.length;
out.personaggi={pickRateMedio:+meanPick.toFixed(3),pickRateMax:cs.reduce((m,c)=>c.pickRate>m.pickRate?c:m),pickRateMin:cs.reduce((m,c)=>c.pickRate<m.pickRate?c:m),winMedio:+meanWin.toFixed(1),topPick:[...cs].sort((x,y)=>y.pickRate-x.pickRate).slice(0,8),bottomPick:[...cs].sort((x,y)=>x.pickRate-y.pickRate).slice(0,8),topWin:[...cs].filter(c=>c.games>=150).sort((x,y)=>y.winPct-x.winPct).slice(0,8),bottomWin:[...cs].filter(c=>c.games>=150).sort((x,y)=>x.winPct-y.winPct).slice(0,8),tutti:cs};
fs.writeFileSync('sim_results_'+tag+'.json',JSON.stringify(out,null,1));
console.log(JSON.stringify(out.aggregato));console.log('riproducibile',out.riproducibile);
for(const k of Object.keys(out.sets)){console.log('--',k);console.table(out.sets[k].rows)}
console.log('pick medio',out.personaggi.pickRateMedio,'max',out.personaggi.pickRateMax.name,out.personaggi.pickRateMax.pickRate,'min',out.personaggi.pickRateMin.name,out.personaggi.pickRateMin.pickRate);
console.log('topPick',out.personaggi.topPick.map(c=>c.name+' '+c.pickRate+'/'+c.offered).join('; '));console.log('topWin',out.personaggi.topWin.map(c=>c.name+' '+c.winPct).join('; '));console.log('bottomWin',out.personaggi.bottomWin.map(c=>c.name+' '+c.winPct).join('; '));
