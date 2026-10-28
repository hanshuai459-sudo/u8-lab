const vm = require('vm');
const fs = require('fs');
const assert = require('assert');
const source = fs.readFileSync(require('path').join(__dirname, '../assets/app.js'), 'utf8');
const results = [];
function run(name, fn) { fn(); results.push('PASS '+name); }
function env(options={}) {
  const nodes = {}, all = [], store = options.store || {};
  class Node {
    constructor(tag,id,attrs={}) { this.tagName=tag; this.id=id; this.attrs=attrs; this.value=''; this.textContent=''; this.style={}; this.className=''; this.events={}; this.children=[]; all.push(this); if(id) nodes[id]=this; }
    getAttribute(name) { return Object.hasOwn(this.attrs,name) ? this.attrs[name] : null; }
    addEventListener(name,fn) { this.events[name]=fn; }
    attachEvent(name,fn) { this.events[name.slice(2)]=function(){fn.call(undefined);}; }
    getElementsByTagName(tag) { return this.children.filter(x=>x.tagName===tag); }
    click() { if(this.events.click)this.events.click.call(this); }
    focus(){} select(){this.selected=true;}
  }
  ['message','storage-state','progress-status','progress-step','progress-note','save-progress','transfer-text','import-progress','export-text','download-progress','copy-progress','import-file','copy-close','manual-copy','copy-text','copy-help','search','search-button','search-result','done-count'].forEach(id=>new Node(id.indexOf('progress')>=0?'input':'div',id));
  const progress = new Node('span','badge',{'data-progress':'02'});
  const input1 = new Node('input','f1',{'data-field':'1'}); input1.value='001';
  const input2 = new Node('input','f2',{'data-field':'1'}); input2.value='01';
  const row = new Node('tr','r1',{'data-search':'001 华宏公司'}); row.children=[input1,input2];
  const pending = new Node('tr','r2',{'data-search':'待核对'});
  const header = new Node('tr','h'); const table = new Node('table','t1');
  const h1 = new Node('th','h1',{'data-label':'编码'}), h2 = new Node('th','h2',{'data-label':'分类'}), h3=new Node('th','h3'); table.children=[h1,h2,h3,header,row,pending];
  const b1=new Node('button','copy-field',{'data-copy':'field','data-target':'f1'}), b2=new Node('button','copy-row',{'data-copy':'row','data-target':'r1'}), b3=new Node('button','copy-table',{'data-copy':'table','data-target':'t1'});
  if(options.legacy) for(const n of all)n.addEventListener=undefined;
  const document={body:{getAttribute:()=> '02'},getElementById:id=>nodes[id]||null,getElementsByTagName:tag=>tag==='*'?all:all.filter(n=>n.tagName===tag),execCommand:()=>!!options.execCopy};
  let copied;
  const window={localStorage:{getItem:k=>{if(options.blocked)throw Error('disabled');return store[k]||null;},setItem:(k,v)=>{if(options.blocked)throw Error('disabled');store[k]=v;}},navigator:{},setTimeout:()=>{}};
  if(options.ieCopy) window.clipboardData={setData:(format,value)=>{copied=value;return true;}};
  vm.runInNewContext(source,{window,document,JSON,Object,String,Error,Blob:undefined});
  return {nodes,store,copy:()=>copied,progress};
}
run('IE clipboard preserves 001 and row tab delimiters',()=>{const x=env({ieCopy:true,legacy:true});x.nodes['copy-field'].click();assert.equal(x.copy(),'001');x.nodes['copy-row'].click();assert.equal(x.copy(),'001\t01');});
run('Table copying omits unverified rows and preserves header',()=>{const x=env({ieCopy:true});x.nodes['copy-table'].click();assert.equal(x.copy(),'编码\t分类\r\n001\t01');});
run('Search filters table; table copy excludes hidden rows',()=>{const x=env({ieCopy:true});x.nodes.search.value='无匹配';x.nodes['search-button'].click();assert.equal(x.nodes.r1.style.display,'none');x.nodes['copy-table'].click();assert.equal(x.copy(),undefined);assert.match(x.nodes.message.textContent,/没有可复制/);});
run('Manual copy fallback selects complete text',()=>{const x=env();x.nodes['copy-field'].click();assert.equal(x.nodes['copy-text'].value,'001');assert.equal(x.nodes['copy-text'].selected,true);assert.equal(x.nodes['manual-copy'].className,'manual');});
run('Progress persists and restores across page reloads',()=>{const x=env();x.nodes['progress-status'].value='doing';x.nodes['progress-step'].value='001';x.nodes['progress-note'].value='notes';x.nodes['save-progress'].click();const y=env({store:x.store});assert.equal(y.nodes['progress-step'].value,'001');assert.equal(y.progress.textContent,'进行中');});
run('Progress export/import merges different labs and accepts UTF8 BOM',()=>{const x=env();x.nodes['progress-status'].value='doing';x.nodes['progress-step'].value='a';x.nodes['save-progress'].click();x.nodes['transfer-text'].value='\ufeff'+JSON.stringify({app:'u8-lab',version:1,progress:{'03':{status:'done',step:'b',note:'<script>text</script>'}}});x.nodes['import-progress'].click();x.nodes['export-text'].click();const v=JSON.parse(x.nodes['transfer-text'].value);assert.equal(v.progress['02'].step,'a');assert.equal(v.progress['03'].status,'done');});
run('Malformed imports never partially change prior progress',()=>{const x=env();x.nodes['export-text'].click();const before=x.nodes['transfer-text'].value;for(const value of ['{',JSON.stringify({app:'u8-lab',version:2,progress:{}}),JSON.stringify({app:'u8-lab',version:1,progress:{'02':{status:'done',step:'ok',note:''},'14':{status:'done',step:'bad',note:''}}})]){x.nodes['transfer-text'].value=value;x.nodes['import-progress'].click();assert.match(x.nodes.message.textContent,/导入失败/);x.nodes['export-text'].click();assert.equal(x.nodes['transfer-text'].value,before);}});
run('Disabled localStorage still allows current-page export',()=>{const x=env({blocked:true});x.nodes['progress-status'].value='done';x.nodes['save-progress'].click();assert.match(x.nodes['storage-state'].textContent,/无法保存/);x.nodes['export-text'].click();assert.equal(JSON.parse(x.nodes['transfer-text'].value).progress['02'].status,'done');});
console.log(results.join('\n'));


