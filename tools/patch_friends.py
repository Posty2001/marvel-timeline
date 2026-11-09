#!/usr/bin/env python3
"""Patch TVA Friends: aggiunge CSS + script (IIFE) in coda al body. Idempotente. Non modifica altro (Timeline, Atlante, Centrale, TD2, sync)."""
import re, os
BASE='/home/claude/work'; P=BASE+'/index.html'; SW=BASE+'/sw.js'; D=BASE+'/tools/friends/'
BUILD='20261109-2100-friends'
s=open(P,encoding='utf-8').read()
js=''.join(open(D+f,encoding='utf-8').read()+'\n' for f in ('friends_core.js','friends_logic.js','friends_cloud.js','friends_ui.js','friends_boot.js'))
assert '</script>' not in js
css=open(D+'friends.css',encoding='utf-8').read()
block_css='<style id="friends-css">\n'+css+'</style>\n'
block_js='<script id="friends-js">/* TVA FRIENDS: moduli locali (codici/file) + trasporto cloud DISATTIVATO. Non legge ne\' scrive il profilo sincronizzato. */\n(function () { \'use strict\';\ntry {\n'+js+'} catch (errTf) { if (window.console) console.error(\'TVA Friends:\', errTf); }\n})();\n</script>\n'
s=re.sub(r'<style id="friends-css">.*?</style>\n','',s,flags=re.S)
s=re.sub(r'<script id="friends-js">.*?</script>\n','',s,flags=re.S)
assert s.count('</head>')==1 and s.count('</body>')==1
s=s.replace('</head>',block_css+'</head>',1)
s=s.replace('</body>',block_js+'</body>',1)
s=re.sub(r'(<meta name="tva-build" content=")[^"]*(")',r'\g<1>'+BUILD+r'\2',s)
open(P,'w',encoding='utf-8').write(s)
sw=open(SW,encoding='utf-8').read()
sw=re.sub(r"(const SW_BUILD = ')[^']*(')",r'\g<1>'+BUILD+r'\2',sw)
sw=re.sub(r"(const CACHE_NAME = 'marvel-timeline-cache-)[^']*(')",r'\g<1>'+BUILD+r'\2',sw)
open(SW,'w',encoding='utf-8').write(sw)
print('ok',BUILD)
