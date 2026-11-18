const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(require('node:path').join(__dirname,'../index.html'),'utf8');
const addresses=['bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z','bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9'];
const alphabet='qpzry9x8gf2tvdw0s3jn54khce6mua7l';
function bech32Mod(vals) {
 let chk=1;
 for(const v of vals) {
   const top=chk>>>25;
   chk=((chk&0x1ffffff)<<5)^v;
   const factors=[0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3];
   factors.forEach((poly,i)=>{if((top>>>i)&1)chk^=poly;});
 }
 return chk;
}
function validNativeBTC(addr) {
 if(!/^bc1q[023456789acdefghjklmnpqrstuvwxyz]{38}$/.test(addr))return false;
 const cut=addr.lastIndexOf('1'),hrp=addr.slice(0,cut);
 const bits=[...addr.slice(cut+1)].map(c=>alphabet.indexOf(c));
 if(bits.includes(-1)||bits[0]!==0)return false;
 const hrpb=[...hrp].map(c=>c.charCodeAt(0)>>>5).concat([0],[...hrp].map(c=>c.charCodeAt(0)&31));
 return bech32Mod(hrpb.concat(bits))===1;
}
test('both public support destinations have valid native BTC mainnet bech32 checksums',()=>{
 for(const address of addresses)assert.equal(validNativeBTC(address),true,address);
});
test('each Bitcoin-payment URI exactly matches an approved public destination',()=>{
 for(const address of addresses){
   assert.ok(html.includes('href="bitcoin:'+address+'?label='));
   assert.ok(html.includes('data-copy-btc="'+address+'"'));
 }
});
test('the support route is clearly optional and never asks for another token or chain',()=>{
 assert.ok(html.includes('Optional Bitcoin-mainnet support.'));
 assert.ok(html.includes('Never send USDC, tokens, Lightning payments'));
 assert.ok(html.includes('The browser tools are free to use without paying.'));
});
test('two usable independent customer contact routes are present',()=>{
 assert.ok(html.includes('issues/new?template=paid-work-request.yml'));
 assert.ok(html.includes('www.task-bounty.com/board/23a2a3ff-672e-4db7-8ff8-7d9845afb40b'));
});