'use strict';
// ENIGMA browser check-in interactive script regression tests.
// Uses Node's built-in test/vm modules and a deliberately minimal fake DOM.
// These test the real inline app logic, not a full browser; no network or customer data.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('docs/personal-daily-checkin-demo.html','utf8');
const script = (html.match(/<script>([\s\S]*?)<\/script>/)||[])[1];
assert.ok(script,'inline check-in script must exist');

function createFixture(opts={}) {
  const nodes=new Map(), store=new Map();
  class Element {
    constructor(id='') {this.id=id;this.value='';this.textContent='';this.children=[];this.listeners={};this.checked=false;this.attributes={};this.hidden=false;}
    addEventListener(event,callback){this.listeners[event]=callback;}
    dispatch(event){assert.equal(typeof this.listeners[event],'function',event+' handler missing');this.listeners[event]({preventDefault(){}});}
    setAttribute(name,value){this.attributes[name]=value;}
    append(...children){this.children.push(...children);}
    replaceChildren(...children){this.children=children;}
    reset(){byId('routine-name').value='';byId('routine-time').value='';}
    remove(){}
    click(){}
  }
  const byId=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
  const localStorage={
    getItem(k){return store.has(k)?store.get(k):null;},
    setItem(k,v){if(opts.failSet)throw new Error('Quota exceeded');store.set(k,String(v));},
    removeItem(k){if(opts.failRemove)throw new Error('Blocked storage removal');store.delete(k);}
  };
  const document={
    getElementById:byId,
    createElement:()=>new Element(),
    body:{append(){}},
    addEventListener(){},
    hidden:false
  };
  const window={addEventListener(){},confirm:()=>true};
  const URL={createObjectURL:()=> 'blob:mock',revokeObjectURL(){}};
  vm.runInNewContext(script,{document,window,localStorage,URL,Blob,Date,Math,JSON,Error,console},{timeout:3000,filename:'personal-daily-checkin-demo.inline.js'});
  return {byId,localStorage,store};
}
const KEY='enigma_checkin_demo_v1';

test('routine and reflection succeed only after local storage writes',()=>{
 const {byId,localStorage}=createFixture();
 byId('routine-name').value='Water plants';
 byId('routine-time').value='08:30';
 byId('routine-form').dispatch('submit');
 assert.equal(byId('routine-feedback').textContent,'Routine added.');
 assert.equal(byId('completion-count').textContent,'0 of 1');
 assert.equal(JSON.parse(localStorage.getItem(KEY)).routines[0].name,'Water plants');
 byId('reflection').value='Felt productive';
 byId('reflection').dispatch('input');
 assert.equal(byId('reflection-status').textContent,'Reflection saved on this device.');
 assert.ok(JSON.stringify(JSON.parse(localStorage.getItem(KEY)).reflections).includes('Felt productive'));
 byId('erase-data').dispatch('click');
 assert.equal(localStorage.getItem(KEY),null);
 assert.equal(byId('backup-feedback').textContent,'Stored check-in data erased from this browser.');
 assert.equal(byId('completion-count').textContent,'0 of 0');
});

test('storage quota failure must never claim routines or reflections were saved',()=>{
 const {byId,localStorage}=createFixture({failSet:true});
 byId('routine-name').value='Take a break';
 byId('routine-form').dispatch('submit');
 assert.match(byId('routine-feedback').textContent,/session only.*storage failed/i);
 assert.equal(byId('completion-count').textContent,'0 of 1');
 assert.equal(localStorage.getItem(KEY),null);
 byId('reflection').value='Local only';
 byId('reflection').dispatch('input');
 assert.match(byId('reflection-status').textContent,/session only.*saving failed/i);
 byId('clear-completed').dispatch('click');
 assert.match(byId('routine-feedback').textContent,/session only.*storage failed/i);
});

test('failed deletion warns and retains visible user entries',()=>{
 const {byId,localStorage}=createFixture({failRemove:true});
 byId('routine-name').value='Exercise';
 byId('routine-form').dispatch('submit');
 assert.ok(localStorage.getItem(KEY));
 byId('erase-data').dispatch('click');
 assert.match(byId('backup-feedback').textContent,/Could not verify deletion/);
 assert.ok(localStorage.getItem(KEY),'data remains if browser removal failed');
 assert.equal(byId('completion-count').textContent,'0 of 1');
});

test('user input remains text, not interpreted as HTML',()=>{
 const {byId}=createFixture();
 byId('routine-name').value='<script>alert(1)</script>';
 byId('routine-form').dispatch('submit');
 const row=byId('routine-list').children[0];
 const userLabel=row.children[0].children[1].children[0];
 assert.equal(userLabel.textContent,'<script>alert(1)</script>');
});
