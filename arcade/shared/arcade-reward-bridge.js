/* TVA Arcade -> Archives: candidate events only. No XP, account or Firebase writes. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.TVAArcadeBridge=factory()})(typeof self!=='undefined'?self:this,function(){
'use strict';
const TYPES=Object.freeze(['who-am-i','time-crisis','secret-wars-draft','multiverse-escape']);
const MAX_SCORE=10000000;
function valid(e){return !!e&&typeof e==='object'&&!Array.isArray(e)&&TYPES.includes(e.game)&&['standard','daily','campaign'].includes(e.mode)&&typeof e.runId==='string'&&/^[a-zA-Z0-9:_-]{8,100}$/.test(e.runId)&&typeof e.completedAt==='string'&&!isNaN(Date.parse(e.completedAt))&&typeof e.score==='number'&&Number.isInteger(e.score)&&e.score>=0&&e.score<=MAX_SCORE&&typeof e.completed==='boolean'&&(e.day===undefined||/^\d{4}-\d{2}-\d{2}$/.test(e.day))&&(e.mode!=='daily'||typeof e.day==='string')}
function key(e){return e.game+'|'+e.mode+'|'+(e.mode==='daily'?e.day:e.runId)}
function preview(events){const seen=new Set(),accepted=[],rejected=[];for(const e of events){if(!valid(e)){rejected.push({reason:'invalid'});continue}const k=key(e);if(seen.has(k)){rejected.push({reason:'duplicate',key:k});continue}seen.add(k);accepted.push({key:k,game:e.game,mode:e.mode,score:e.score,completed:e.completed,completedAt:e.completedAt})}return {schema:1,writeEnabled:false,xpAwarded:0,missionUpdates:0,accepted,rejected}}
return Object.freeze({valid,key,preview});
});
