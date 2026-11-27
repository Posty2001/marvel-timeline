// Ricerca dell'archivio esteso (atlante2/db.js) su una radice dati passata come argomento (fixture o reale).
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=process.argv[2];let fail=0;const ok=(c,m)=>{if(!c){fail++;console.log('FAIL',m)}};
global.window=global;global.document={currentScript:{src:'file://'+path.resolve('atlante2/db.js')}};
global.fetch=u=>{const p=u.replace('file://','').replace(/^.*atlante2\/data\/db\//,'');const f=path.join(root,p);return fs.existsSync(f)?Promise.resolve({ok:true,json:()=>Promise.resolve(JSON.parse(fs.readFileSync(f)))}):Promise.resolve({ok:false,status:404})};
global.unescape=global.unescape||(s=>s);
vm.runInThisContext(fs.readFileSync('atlante2/db.js','utf8'));
const S=q=>new Promise(r=>tvaDb.search(q,r));
(async()=>{
  const m=JSON.parse(fs.readFileSync(path.join(root,'meta.json')));
  ok((await S('zaxx')).filter(r=>r.t!=='x').length===2,'due omonimi non fusi');
  ok((await S('Z-Man')).some(r=>r.i==='id-zaxx-the-wanderer'),'alias');
  ok((await S('vagabondo')).some(r=>r.i==='id-zaxx-the-wanderer'),'nome italiano');
  ok((await S('anderer')).some(r=>r.i==='id-zaxx-the-wanderer'),'infisso');
  ok((await S('ZÀXX')).length>=1,'accenti/maiuscole');
  ok((await S('scarlet witch')).some(r=>r.t==='x'&&r.x==='id-wanda-maximoff'),'alias di voce esistente -> scheda esistente');
  ok((await S('test performer')).some(r=>r.t==='x'||r.i),'interprete');
  ok((await S('zz')).length>=0,'query corta senza errori');
  ok((await S('qqqqqq')).length===0,'nessun falso positivo');
  const g=await new Promise(r=>tvaDb.get('luo-hidden-vault',r));ok(g&&g.wd==='Q104','get per id');
  ok(!(await S('rogue case')).length,'staging NON nel runtime');
  ok(!(await S('some episode')).length,'episodi fuori ambito');
  console.log('db_js_test: record',m.N,fail?'FAIL':'ok');process.exit(fail?1:0);
})();
