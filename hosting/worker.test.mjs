import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './worker.mjs';

const SOURCE = 'https://raw.githubusercontent.com/rangelovkiril/elsys-club-dns/main/index.html';
const request = (path='/', method='GET') => new Request('https://info.elsys.club'+path,{method});
const env = {ASSETS:{fetch:async req=>{
  assert.equal(new URL(req.url).pathname,'/index.html');
  return new Response('<html>approved bootstrap</html>');
}}};
function mockFetch(t, fn) {
  const original=globalThis.fetch;globalThis.fetch=fn;t.after(()=>{globalThis.fetch=original;});
}

test('serves approved main file, preserves bytes and ignores client query/headers',async t=>{
  mockFetch(t,async(url,options)=>{
    assert.equal(url,SOURCE);assert.equal(options.redirect,'error');
    assert.equal(options.cf.cacheTtlByStatus['200'],60);
    assert.equal(options.headers,undefined);
    return new Response('<html>latest merged page</html>');
  });
  const res=await worker.fetch(request('/?source=https://attacker.invalid'),env);
  assert.equal(res.status,200);assert.equal(res.headers.get('X-Clubs-Source'),'repository');
  assert.equal(res.headers.get('Cache-Control'),'no-store');
  assert.equal(res.headers.get('Content-Type'),'text/html; charset=utf-8');
  assert.equal(await res.text(),'<html>latest merged page</html>');
});
test('HEAD has no body',async t=>{
  mockFetch(t,async()=>new Response('<html>approved</html>'));
  const res=await worker.fetch(request('/index.html','HEAD'),env);
  assert.equal(res.status,200);assert.equal(await res.text(),'');
});
test('missing main file serves the bundled approved snapshot',async t=>{
  mockFetch(t,async()=>new Response('Not found',{status:404}));
  const res=await worker.fetch(request(),env);
  assert.equal(res.headers.get('X-Clubs-Source'),'bootstrap');
  assert.equal(await res.text(),'<html>approved bootstrap</html>');
});
test('GitHub outage serves snapshot and failed snapshot returns 503',async t=>{
  mockFetch(t,async()=>{throw new Error('network failure');});
  assert.equal((await worker.fetch(request(),env)).status,200);
  assert.equal((await worker.fetch(request(),{ASSETS:{fetch:async()=>new Response('',{status:404})}})).status,503);
});
test('does not expose repo/config files or accept writes',async t=>{
  mockFetch(t,async()=>{assert.fail('Rejected requests must not fetch GitHub');});
  for(const path of ['/README.md','/hosting/worker.mjs','/clubs/info.yaml','/.env','/_worker.js'])
    assert.equal((await worker.fetch(request(path),env)).status,404);
  assert.equal((await worker.fetch(request('/','POST'),env)).status,405);
});
