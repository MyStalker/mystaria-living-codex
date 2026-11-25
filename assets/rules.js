(function(scope){
'use strict';
const MP={0:.55,1:1,2:1.35,4:1.70,8:2.05,12:2.25,20:2.51};
function impact(power,defense){
 if(!Number.isFinite(power)||!Number.isFinite(defense)||power<0||defense<=0)return null;
 const ratio=power/defense;
 const stages=ratio<=.75?0:ratio<=1.75?1:ratio<=3?2:3;
 return {ratio,stages,tier:['Superficial','Solid','Devastating','Overwhelming'][stages]};
}
function spell(attribute,rating,mp){
 if(!Number.isFinite(attribute)||!Number.isFinite(rating)||attribute<1||rating<0||!Object.hasOwn(MP,mp))return null;
 return (attribute**2+rating**2)*MP[mp];
}
function elementalSR(end,mr,er){
 if(![end,mr,er].every(Number.isFinite)||end<1||mr<0||er<0)return null;
 return Math.ceil(((end+.65*mr)**2*er)/.70);
}
function ritual(cl){return Number.isFinite(cl)&&cl>=0?4*cl:null;}
const api={impact,spell,elementalSR,ritual};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
scope.MystariaRules=api;
if(typeof document==='undefined')return;
function update(){
 const get=id=>{const el=document.getElementById(id);return !el||el.value.trim()===''?NaN:Number(el.value);};
 const show=(id,text)=>{const el=document.getElementById(id);if(el)el.textContent=text;};
 const fmt=n=>n.toLocaleString(undefined,{maximumFractionDigits:6});
 const i=impact(get('impact-power'),get('impact-defense'));
 show('impact-out',i?'Impact '+String(i.ratio)+' — '+i.tier+'; '+i.stages+' injury-stage advancement(s).':'Enter nonnegative final Power and positive final Defense.');
 const p=spell(get('spell-attribute'),get('spell-ir'),get('spell-mp'));
 show('spell-out',p===null?'Enter valid neutral inputs and one listed MP investment.':fmt(p)+' ordinary offensive Power; costs, capacity and other defenses still apply.');
 const sr=elementalSR(get('sr-end'),get('sr-mr'),get('sr-er'));
 show('sr-out',sr===null?'Enter valid applicable END, MR and resistance multiplier.':fmt(sr)+' elemental Status Resistance.');
 const cap=ritual(get('ritual-cl'));
 show('ritual-out',cap===null?'Enter an already determined nonnegative full CL.':fmt(cap)+' MP maximum ten-minute ritual capacity, further limited by available mana and legal costs.');
}
document.querySelectorAll('.calc input,.calc select').forEach(el=>el.addEventListener('input',update));
update();
})(typeof globalThis!=='undefined'?globalThis:this);

