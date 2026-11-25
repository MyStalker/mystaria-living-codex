(() => {
  'use strict';
  const q=document.getElementById('codex-q');
  if(!q)return;
  const section=document.getElementById('codex-section'),status=document.getElementById('codex-status'),count=document.getElementById('codex-count'),results=document.getElementById('codex-results');
  const labels={reference:'Reference · revisions apply',experimental:'Approved experimental rules',proposal:'Unapproved development proposal',historical:'Historical / superseded',revision:'Under major revision',incomplete:'Incomplete reference',development:'Development · approval varies'};
  const normalize=s=>String(s).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  let data=[];
  function search(){
    const tokens=normalize(q.value).trim().split(/\s+/).filter(Boolean);
    const found=data.filter(x=>(section.value==='all'||x.category===section.value)&&(status.value==='all'||(status.value==='current'?!['experimental','proposal','historical','development'].includes(x.status):x.status===status.value))).map(x=>{
      let score=x.kind==='entry'?1:0;
      const title=normalize(x.title),text=normalize(x.text);
      for(const t of tokens){if(title.includes(t))score+=20;else if(text.includes(t))score+=2;else return null;}
      return {...x,score};
    }).filter(Boolean).filter(x=>tokens.length||x.kind==='entry').sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));
    const shown=found.slice(0,80);count.textContent=found.length+' results'+(found.length>80?' · first 80 shown':'');
    results.replaceChildren();
    if(!shown.length){const p=document.createElement('p');p.textContent='No matching entries. Try a broader term or include development and history.';results.append(p);}
    for(const x of shown){
      const box=document.createElement('div');box.className='search-result';
      const a=document.createElement('a');a.href=x.url;a.textContent=x.title;
      const badge=document.createElement('span');badge.className='badge '+x.status;badge.textContent=labels[x.status]||labels.reference;
      const p=document.createElement('p');
      if(tokens.length){const normalized=normalize(x.text);const position=Math.max(0,normalized.indexOf(tokens[0]));p.textContent=(position>50?'…':'')+x.text.slice(Math.max(0,position-50),position+230)+(x.text.length>position+230?'…':'');}else p.textContent=x.summary;
      box.append(a,' ',badge,p);results.append(box);
    }
  }
  const initial=new URLSearchParams(location.search);q.value=initial.get('q')||'';
  if(initial.get('status')==='all')status.value='all';
  fetch('/assets/search-index.json').then(r=>{if(!r.ok)throw Error('index');return r.json();}).then(x=>{data=x;search();}).catch(()=>{count.textContent='Search is temporarily unavailable. Browse the section indexes while the index loads.';});
  let debounce; q.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(search,90);});
  section.addEventListener('change',search);status.addEventListener('change',search);
})();
