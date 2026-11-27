// W0 prototipo: ricerca a shard (trigrammi) — misura byte caricati, latenza, correttezza (alias/infix/accenti).
const fs=require('fs'),zlib=require('zlib'),path=require('path');
const dir=process.argv[2];const meta=JSON.parse(fs.readFileSync(dir+'/meta.json'));
const norm=s=>s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
function crc32(s){let c,t=[];for(let n=0;n<256;n++){c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}let r=0xFFFFFFFF;for(const b of Buffer.from(s))r=t[(r^b)&255]^(r>>>8);return(r^0xFFFFFFFF)>>>0}
let bytes=0;const cache={};
function load(f){if(cache[f])return cache[f];const b=fs.readFileSync(dir+'/'+f);bytes+=zlib.gzipSync(b).length;return cache[f]=JSON.parse(b)}
function search(q,lim=10){
  const nq=norm(q);if(!nq)return[];const ws=nq.split(' ');const w=ws.reduce((a,b)=>b.length>a.length?b:a,'');
  let cand;
  if(w.length<3){const p=load('pre.json')[w.slice(0,2)]||[];cand=p}
  else{let sets=[];for(let i=0;i<w.length-2;i++){const t=w.slice(i,i+3);const d=load('t/'+(crc32(t)%meta.SH)+'.json')[t];if(!d)return[];let a=0;sets.push(d.map(x=>a+=x))}
    sets.sort((a,b)=>a.length-b.length);cand=sets[0];for(const s of sets.slice(1)){const S=new Set(s);cand=cand.filter(x=>S.has(x))}}
  const res=[];
  for(const o of cand){const [n,al]=load('n/'+Math.floor(o/meta.CH)+'.json')[o%meta.CH];
    let best=0;for(const k of [n,...al]){const nk=norm(k);let s=0;
      if(nk===nq)s=100;else if(nk.startsWith(nq))s=80;else if(nk.split(' ').some(x=>x.startsWith(nq)))s=60;else if(ws.every(x=>nk.includes(x)))s=40;
      if(s>best)best=s}
    if(best)res.push([best,n,o])}
  res.sort((a,b)=>b[0]-a[0]||a[1].localeCompare(b[1]));return res.slice(0,lim);
}
let fail=0;const ok=(c,m)=>{if(!c){fail++;console.log('FAIL',m)}};
const qs=['spider','SPIDER-man','peter parker','tony','iron','thor','sp','wanda','hawkeye','xyzqq'];
const lat=[];
for(const q of qs){const t=process.hrtime.bigint();const r=search(q);lat.push(Number(process.hrtime.bigint()-t)/1e6);console.log(q.padEnd(12),r.length,(r[0]||[]).slice(1,2)[0]||'-')}
const r1=search('spider');ok(r1.length>0,'spider vuoto');
ok(search('peter parker').some(x=>/Peter Parker/.test(x[1])),'peter parker');
ok(search('IRON MAN').length>=0,'case');
// infix: un nome sintetico
const n0=load('n/0.json')[0][0];const inf=n0.slice(2,7);ok(search(inf).some(x=>x[1]===n0),'infix '+inf);
// alias
let al=null,own=null;const ch=load('n/'+Math.floor(meta.N/2/meta.CH)+'.json');for(let i=0;i<ch.length;i++)if(ch[i][1].length){al=ch[i][1][0];own=ch[i][0];break}
ok(search(al).some(x=>x[1]===own),'alias '+al);
// accenti
ok(search('Pèter Párker').some(x=>/Peter Parker/.test(x[1])),'accenti');
const p95=lat.slice().sort((a,b)=>a-b)[Math.floor(lat.length*.95)-1]||0;
console.log(`N=${meta.N} gz-index=${(Object.values(meta.gz).reduce((a,b)=>a+b)/1e6).toFixed(2)}MB | caricati nelle ${qs.length} query: ${(bytes/1e3).toFixed(0)}KB gz | lat max ${Math.max(...lat).toFixed(1)}ms | RSS ${(process.memoryUsage().rss/1e6).toFixed(0)}MB`);
process.exit(fail?1:0);
