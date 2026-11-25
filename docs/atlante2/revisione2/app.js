(function(){
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var STATIC=/static/.test(location.search);
if(STATIC)document.body.classList.add('static');
/* reveal */
$$('.scr').forEach(function(sc){
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)e.target.classList.add('in')})},{root:sc,threshold:.1});
 $$('.rev',sc).forEach(function(r){io.observe(r)});
 if(STATIC)$$('.rev',sc).forEach(function(r){r.classList.add('in')});
});
/* catalog toggle */
$$('#vseg button').forEach(function(b){b.onclick=function(){$$('#vseg button').forEach(function(x){x.classList.remove('on')});b.classList.add('on');var g=b.dataset.v=='g';$('#vg').style.display=g?'grid':'none';$('#vl').style.display=g?'none':'block'}});
/* dossier tabs + progress */
var seen={s1:1};
function prog(){var e=$('#dprog');if(e)e.textContent=Math.min(Object.keys(seen).length,3)+'/3'}
$$('#dtabs .chip').forEach(function(c){c.onclick=function(){$$('#dtabs .chip').forEach(function(x){x.classList.remove('on')});c.classList.add('on');var t=$('#'+c.dataset.s);var sc=t.closest('.scr');sc.scrollTo({top:t.offsetTop-110,behavior:'smooth'});seen[c.dataset.s]=1;prog()}});
var ds=$('#f3 .scr');if(ds)ds.addEventListener('scroll',function(){var p=$('#dparx');if(p)p.style.transform='translateY('+(ds.scrollTop*.35)+'px)'});
/* hub count from data */
var hn=$('#hn');if(hn)hn.textContent=$$('#f4 .hid').length;
/* places tabs */
$$('#pseg button').forEach(function(b){b.onclick=function(){$$('#pseg button').forEach(function(x){x.classList.remove('on')});b.classList.add('on');$$('.pp').forEach(function(p){p.style.display=p.dataset.p==b.dataset.p?'grid':'none'})}});
/* map */
var mapw=$('#mapw');
if(mapw){var s=1,tx=0,ty=0,svg=$('#msvg');
 function ap(){svg.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')'}
 $('#zi').onclick=function(){s=Math.min(2.6,s*1.3);ap()};$('#zo').onclick=function(){s=Math.max(.7,s/1.3);ap()};
 var pts={},lx,ly,ld,moved=0;
 mapw.addEventListener('pointerdown',function(e){mapw.setPointerCapture(e.pointerId);pts[e.pointerId]=e;lx=e.clientX;ly=e.clientY;moved=0});
 mapw.addEventListener('pointermove',function(e){if(!pts[e.pointerId])return;pts[e.pointerId]=e;var k=Object.keys(pts);
  if(k.length==2){var a=pts[k[0]],b=pts[k[1]],d=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);if(ld)s=Math.max(.7,Math.min(2.6,s*d/ld));ld=d;ap()}
  else{tx+=e.clientX-lx;ty+=e.clientY-ly;moved+=Math.abs(e.clientX-lx)+Math.abs(e.clientY-ly);lx=e.clientX;ly=e.clientY;ap()}});
 var first=$('.mn');if(first)setTimeout(function(){pick(first)},0);
 function up(e){delete pts[e.pointerId];ld=0;if(moved<=6){var t=document.elementFromPoint(e.clientX,e.clientY),n=t&&t.closest&&t.closest('.mn');if(n)pick(n)}}
 mapw.addEventListener('pointerup',up);mapw.addEventListener('pointercancel',up);
 mapw.addEventListener('wheel',function(e){e.preventDefault();s=Math.max(.7,Math.min(2.6,s*(e.deltaY<0?1.1:.9)));ap()},{passive:false});
 function pick(n){$$('.mn circle:nth-child(2)').forEach(function(c){c.setAttribute('stroke-width',2)});n.querySelector('circle:nth-child(2)').setAttribute('stroke-width',5);$('#mt').textContent=n.dataset.n;$('#md').textContent=n.dataset.d+' · '+n.dataset.t+' titoli · '+n.dataset.p+' personaggi';$('#mk').textContent=n.dataset.k}
 
}
/* nexus */
var NX={'Loki':[['Thor','Fratello','#e0707a'],['Odino','Padre adottivo','#e0707a'],['Laufey','Padre biologico','#e0707a'],['Sylvie','Variante','#b48ae0'],['Mobius','Alleato','#4fd0ff'],['Frigga','Correlato','#E3C79B']],
'Thor':[['Loki','Fratello','#e0707a'],['Odino','Padre','#e0707a'],['Frigga','Correlato','#E3C79B']],
'Odino':[['Thor','Figlio','#e0707a'],['Loki','Figlio adottivo','#e0707a']],
'Sylvie':[['Loki','Variante','#b48ae0'],['Mobius','Alleato','#4fd0ff']],
'Mobius':[['Loki','Alleato','#4fd0ff'],['Sylvie','Alleato','#4fd0ff']],
'Frigga':[['Thor','Correlato','#E3C79B'],['Loki','Correlato','#E3C79B']],
'Laufey':[['Loki','Figlio','#e0707a']]};
var AV={'Loki':'variante','Thor':'esploratore','Odino':'sentinella','Sylvie':'mistico','Mobius':'cronista','Frigga':'sentinella','Laufey':'astratto','Steve Rogers':'agente','Hela':'mistico'};
function nexus(c){var svg=$('#nx');if(!svg)return;var L=NX[c]||[],cx=195,cy=270,R=150,o='<defs>';
 L.concat([[c]]).forEach(function(x,i){o+='<clipPath id="cp'+i+'"><circle r="'+(i==L.length?52:32)+'"/></clipPath>'});o+='</defs>';
 L.forEach(function(x,i){var a=-Math.PI/2+i*2*Math.PI/L.length,px=cx+R*Math.cos(a),py=cy+R*Math.sin(a);
  o+='<line x1="'+cx+'" y1="'+cy+'" x2="'+px+'" y2="'+py+'" stroke="'+x[2]+'" stroke-width="2.5" stroke-opacity=".7"/>';});
 L.forEach(function(x,i){var a=-Math.PI/2+i*2*Math.PI/L.length,px=cx+R*Math.cos(a),py=cy+R*Math.sin(a);
  o+='<g class="nn" data-n="'+x[0]+'" transform="translate('+px+' '+py+')" style="cursor:pointer"><circle r="35" fill="none" stroke="'+x[2]+'" stroke-width="2"/><g clip-path="url(#cp'+i+')"><image href="'+window.__AV[AV[x[0]]||'astratto']+'" x="-45" y="-45" width="90" height="90" preserveAspectRatio="xMidYMid slice"/></g><text y="52" text-anchor="middle" fill="#ede0c0" font-size="12" font-family="Inter" font-weight="600">'+x[0]+'</text><text y="66" text-anchor="middle" fill="'+x[2]+'" font-size="10" font-family="Inter">'+x[1]+'</text></g>'});
 o+='<g transform="translate('+cx+' '+cy+')"><circle r="58" fill="none" stroke="#F59A23" stroke-width="2.5"><animate attributeName="r" values="56;62;56" dur="3s" repeatCount="indefinite"/></circle><g clip-path="url(#cp'+L.length+')"><image href="'+window.__AV[AV[c]||'astratto']+'" x="-60" y="-60" width="120" height="120" preserveAspectRatio="xMidYMid slice"/></g><text y="80" text-anchor="middle" fill="#fff" font-size="17" font-family="Spectral" font-weight="700">'+c+'</text></g>';
 svg.innerHTML=o;$$('.nn',svg).forEach(function(n){n.addEventListener('click',function(){nexus(n.dataset.n)})})}
nexus('Loki');
/* search */
var DATA=window.__SR||[];
var sr=$('#q');
if(sr){var tf='';
 function rs(){var q=sr.value.toLowerCase().trim(),h='';DATA.filter(function(d){return(!q||d[0].toLowerCase().indexOf(q)>-1)&&(!tf||d[1].indexOf(tf)==0)}).forEach(function(d){h+='<div class="card" style="display:flex;gap:12px;align-items:center;padding:12px;margin-bottom:8px"><span class="dotc" style="background:'+d[2]+';width:12px;height:12px"></span><div style="flex:1"><b style="font-family:Spectral,serif;font-size:16px">'+d[0].replace(new RegExp('('+q+')','i'),'<span style="color:#F59A23">$1</span>')+'</b><div class="note">'+d[1]+'</div></div></div>'});
  $('#sr').innerHTML=h||'<div class="note">Nessun risultato. Prova con un altro nome.</div>'}
 sr.oninput=rs;$$('#sf .chip').forEach(function(c){c.onclick=function(){$$('#sf .chip').forEach(function(x){x.classList.remove('on')});c.classList.add('on');tf=c.dataset.t;rs()}});rs()}
/* progress ring */
var pr=$('#pr');if(pr){var f14=$('#f14 .scr');setTimeout(function(){pr.style.strokeDashoffset=276.5*(1-18/30)},300)}
/* compare */
$$('.cmp').forEach(function(c){var af=c.querySelector('.after'),h=c.querySelector('.hnd');function set(x){var r=c.getBoundingClientRect(),p=Math.max(0,Math.min(1,(x-r.left)/r.width));af.style.clipPath='inset(0 0 0 '+(p*100)+'%)';h.style.left=(p*100)+'%'}
 var d=0;c.addEventListener('pointerdown',function(e){d=1;c.setPointerCapture(e.pointerId);set(e.clientX)});c.addEventListener('pointermove',function(e){if(d)set(e.clientX)});c.addEventListener('pointerup',function(){d=0})});
})();
