
(function(){
const root=document.documentElement.dataset.root||'';
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const saved=(k,d)=>{try{return localStorage.getItem(k)??d}catch(e){return d}};
const store=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}};
const proposalShown=saved('mystaria-proposals','yes')==='yes';
if(!proposalShown)document.documentElement.classList.add('hide-proposals');
if(saved('mystaria-theme','day')==='night')document.documentElement.classList.add('night');
document.querySelectorAll('[data-theme-toggle]').forEach(b=>b.addEventListener('click',()=>{const isNight=document.documentElement.classList.toggle('night');store('mystaria-theme',isNight?'night':'day');}));
let spoilerSearch=saved('mystaria-spoiler-search','no')==='yes';
document.querySelectorAll('[data-proposal-toggle]').forEach(e=>{e.checked=proposalShown;e.addEventListener('change',()=>{document.documentElement.classList.toggle('hide-proposals',!e.checked);store('mystaria-proposals',e.checked?'yes':'no');document.querySelectorAll('[data-proposal-toggle]').forEach(x=>x.checked=e.checked);if(window.runSearch)window.runSearch();})});
document.querySelectorAll('[data-spoiler-toggle]').forEach(e=>{e.checked=spoilerSearch;e.addEventListener('change',()=>{spoilerSearch=e.checked;store('mystaria-spoiler-search',spoilerSearch?'yes':'no');document.querySelectorAll('[data-spoiler-toggle]').forEach(x=>x.checked=e.checked);if(window.runSearch)window.runSearch();})});
const mb=document.getElementById('mobile-menu'),nv=document.getElementById('global-nav'),sd=document.getElementById('side-nav');if(mb)mb.addEventListener('click',()=>{const open=nv.classList.toggle('open');sd?.classList.toggle('open',open);mb.setAttribute('aria-expanded',String(open));});
function revealHash(){if(!location.hash)return;let id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return};const el=document.getElementById(id);if(!el)return;let p=el;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;} setTimeout(()=>el.scrollIntoView({block:'start',behavior:'smooth'}),50);}
window.addEventListener('hashchange',revealHash);revealHash();
const results=document.getElementById('search-results'),q=document.getElementById('search-q'),category=document.getElementById('search-category'),statusFilter=document.getElementById('search-status'),manaFilter=document.getElementById('search-mana'),spFilter=document.getElementById('search-sp'),count=document.getElementById('search-count');
if(results&&q){
 let idx=[];let loaded=false;
 const aliases={'draykin':'drakyn','draykyn':'drakyn','jester craft':'jestercraft','manacraft':'warlock','mysteria':'mystaria','nagas':'naga'};
 const normalize=s=>String(s||'').toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'');
 const parse=(t)=>{let n=normalize(t).trim();Object.keys(aliases).forEach(a=>{if(n.includes(a))n=n.replaceAll(a,aliases[a])});return n;};
 function search(){if(!loaded)return;const query=parse(q.value),tokens=query.split(/\s+/).filter(Boolean);const cat=category?.value||'all',st=statusFilter?.value||'all',mana=manaFilter?.value||'all',sp=spFilter?.value||'all';const proposals=document.querySelector('[data-proposal-toggle]')?.checked??true;
 let found=idx.map((x)=>{if((['historical','source'].includes(x.status)&&st==='all')||(x.status==='proposal'&&!proposals)||(x.spoiler&&!spoilerSearch)||(cat!=='all'&&cat!==x.category)||(st!=='all'&&st!==x.status)||(mana!=='all'&&!new RegExp('\b'+mana+'\b','i').test(x.title+' '+x.text))||(sp!=='all'&&!new RegExp('\b'+sp+'\s*SP\b','i').test(x.title+' '+x.text)))return null;const ttl=parse(x.title),desc=parse(x.summary),full=parse(x.text);const matches=(val,t)=>t.length<3?val.split(/[^a-z0-9]+/).includes(t):val.includes(t);let score=0;for(let t of tokens){if(matches(ttl,t))score+=14;else if(matches(desc,t))score+=6;else if(matches(full,t))score+=2;else return null;}return {...x,score:score+(x.kind==='entry'?2:0)-(x.category==='Source Transcript'?2:0)}}).filter(Boolean);
 if(!tokens.length)found=found.filter(x=>x.kind==='entry');found.sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));const seenTitles=new Set();found=found.filter(x=>{const key=x.title.toLocaleLowerCase()+'|'+x.kind;if(seenTitles.has(key))return false;seenTitles.add(key);return true;}).slice(0,80);
 if(count)count.textContent=found.length+' result'+(found.length===1?'':'s')+(found.length===80?' (showing first 80)':'');
 if(!found.length){results.innerHTML='<p>No matching entries in the currently visible canon and spoiler filters.</p>';return}
 const labels={canon:'Current Canon',revision:'Under Major Revision',incomplete:'Incomplete',proposal:'Experimental — Not Approved',historical:'Historical',source:'Mixed-status Source Reference',spoiler:'GM Spoilers'};
 results.innerHTML=found.map(x=>'<div class="search-result"><a href="'+esc(root+x.url)+'">'+esc(x.title)+'</a> <span class="badge '+esc(({revision:'under-revision',proposal:'proposed',source:'source',historical:'source'})[x.status]||x.status)+'">'+esc(labels[x.status]||'Reference')+'</span><p>'+esc(x.summary).slice(0,220)+'</p><small>'+esc(x.category)+' · '+esc(x.kind)+'</small></div>').join('');
 }
 window.runSearch=search;
 fetch(root+'assets/search-index.json').then(r=>{if(!r.ok)throw Error('Index could not load');return r.json()}).then(data=>{idx=data;loaded=true;search()}).catch(()=>{results.innerHTML='<p>The search index could not load. Open this website through its hosted URL, not directly as a file, or check that assets/search-index.json was uploaded.</p>'});
 [q,category,statusFilter,manaFilter,spFilter].forEach(el=>el?.addEventListener(el===q?'input':'change',search));
 const urlparams=new URLSearchParams(location.search);if(urlparams.has('q')){q.value=urlparams.get('q');q.focus()}
 }
 // Device-local reading bookmarks. These never publish or sync user data.
 const bookmarkKey='mystaria-bookmarks';
 const getBookmarks=()=>{try{let val=JSON.parse(localStorage.getItem(bookmarkKey)||'[]');return Array.isArray(val)?val:[]}catch(e){return []}};
 const pageId=document.documentElement.dataset.page,pageTitle=document.documentElement.dataset.title;
 const updateBookmarks=()=>{const active=getBookmarks().some(x=>x.path===pageId);document.querySelectorAll('[data-bookmark-toggle]').forEach(b=>{b.textContent=active?'★ Saved to bookmarks':'☆ Save this page';b.setAttribute('aria-pressed',String(active));});const target=document.getElementById('bookmarks-list');if(target){const list=getBookmarks();target.innerHTML=list.length?list.map(x=>'<div class="search-result"><a href="'+esc(root+x.path)+'">'+esc(x.title)+'</a> <button type="button" class="remove-bookmark" data-remove-bookmark="'+esc(x.path)+'">Remove</button></div>').join(''):'<p>No bookmarks yet. Use “☆ Save this page” on any Codex entry.</p>';target.querySelectorAll('[data-remove-bookmark]').forEach(b=>b.addEventListener('click',()=>{store(bookmarkKey,JSON.stringify(getBookmarks().filter(x=>x.path!==b.dataset.removeBookmark)));updateBookmarks();}));}};
 document.querySelectorAll('[data-bookmark-toggle]').forEach(b=>b.addEventListener('click',()=>{let list=getBookmarks();list=list.some(x=>x.path===pageId)?list.filter(x=>x.path!==pageId):[...list,{path:pageId,title:pageTitle}];store(bookmarkKey,JSON.stringify(list));updateBookmarks();}));updateBookmarks();
 const by=id=>document.getElementById(id);
 const num=(id,d=0)=>{let n=Number(by(id)?.value);return Number.isFinite(n)?n:d};
 function calculate(){
 const level=Math.max(1,Math.floor(num('calc-level',1))),m=Math.max(0,Math.floor(num('calc-mana',0))),L=Math.max(25,Math.floor(num('calc-sponge-level',25))),N=Math.max(0,Math.floor(num('calc-stitches',1)));
 const out=(id,v)=>{let el=by(id);if(el)el.textContent=v};
 out('calc-attributes-out',`${2*(level-1)} allocation points earned after level 1; +${Math.floor(level/5)} to each base stat from level 5 milestones`);
 out('calc-stitch-out',`${20+Math.floor(m/4)} maximum Stitches · ${1+Math.floor(m/25)} can regenerate per 6-second round · 2 MP per new Stitch`);
 const V=5*Math.pow(2,Math.floor((L-25)/5)),Q=2*Math.pow(2,Math.floor((L-25)/10));
 out('calc-sponge-out',`${(N*V).toLocaleString()} L stored · ${(N*Q).toLocaleString()} L per 6-second round (with ${N} intake Stitches)`);
 const t=Math.max(0,Math.floor(num('calc-thread-stitches',1))),width=Math.max(.01,num('calc-thread-width',5));out('calc-thread-out',`${((t*.05)/(width/100)).toLocaleString(undefined,{maximumFractionDigits:2})} m of fabric strip at ordinary thickness (ignores thinning/strength limits)`);
 const count=Math.max(0,Math.floor(num('calc-sorcery-count',30))),price=by('calc-sorcery-race')?.value==='drakyn'?2:3;out('calc-sorcery-out',`${count*price} SP for ${count} separately purchased bases/alterations; each costs ${price} SP`);
 const r=Math.min(5,Math.max(0,Math.floor(num('calc-warlock-ranks',5))));out('calc-warlock-out',`${5*r} SP per ${r}-rank discipline; five disciplines all to rank ${r}: ${25*r} SP`);
 }
 document.querySelectorAll('.calc input,.calc select').forEach(el=>el.addEventListener('input',calculate));calculate();
})();
