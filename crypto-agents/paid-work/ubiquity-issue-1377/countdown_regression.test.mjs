import test from 'node:test';
import assert from 'node:assert/strict';
import { isDeepStrictEqual } from 'node:util';
// Isolated extraction from upstream source, not a full Bun integration test.
const TOLERANCE_MS = 1000;
const resetInstant = (time, seconds, observedAt) =>
  time !== undefined ? Date.parse(time) : seconds === undefined ? undefined : observedAt + seconds * 1000;
function quotaEqual(previous, current, patch) {
  if (previous.status !== 'observed' || current.status !== 'observed') return previous.status === current.status;
  if (previous.plan_tier !== current.plan_tier || Object.keys(previous.quota).length !== Object.keys(current.quota).length) return false;
  return Object.entries(current.quota).every(([id, bucket]) => {
    if (!Object.hasOwn(previous.quota, id)) return false;
    const { reset_time: time, reset_in_seconds: seconds, ...values } = bucket;
    const { reset_time: priorTime, reset_in_seconds: priorSeconds, ...priorValues } = previous.quota[id];
    if (!isDeepStrictEqual(values, priorValues)) return false;
    if (patch && time === undefined && priorTime === undefined &&
        seconds !== undefined && seconds === priorSeconds) return true;
    const reset = resetInstant(time, seconds, current.observed_at_ms);
    const priorReset = resetInstant(priorTime, priorSeconds, previous.observed_at_ms);
    if (reset === priorReset) return true;
    if (reset === undefined || priorReset === undefined) return false;
    return (seconds !== undefined || priorSeconds !== undefined) && Math.abs(reset - priorReset) <= TOLERANCE_MS;
  });
}
const previous = ({time=1000000,seconds=80,resetTime,fraction=0.5}={}) => ({
  status:'observed',plan_tier:'Pro',observed_at_ms:time,
  quota:{weekly:{remaining_fraction:fraction,
    ...(seconds==null?{}:{reset_in_seconds:seconds}),
    ...(resetTime===undefined?{}:{reset_time:resetTime})}}
});
const newer = ({time=1014000,seconds=80,resetTime,fraction=0.5}={}) => previous({time,seconds,resetTime,fraction});
test('upstream: identical countdown reported 14s apart gets treated as new',()=>{
  assert.equal(quotaEqual(previous(),newer(),false),false);
  assert.equal(quotaEqual(previous(),newer(),true),true);
});
test('same relative countdown after 29 seconds is still coalesced',()=>{
  assert.equal(quotaEqual(previous(),newer({time:1029000}),true),true);
});
test('changed countdown with changed implied reset instant is not coalesced',()=>{
  assert.equal(quotaEqual(previous(),newer({seconds:79,time:1014000}),true),false);
});
test('actual quota fraction change still updates snapshot',()=>{
  assert.equal(quotaEqual(previous(),newer({fraction:0.4}),true),false);
});
test('absolute reset_time change is not hidden',()=>{
  const a=previous({seconds:null,resetTime:'2026-11-18T16:00:00.000Z'});
  const b=newer({seconds:null,resetTime:'2026-11-18T16:00:02.000Z'});
  assert.equal(quotaEqual(a,b,true),false);
});
test('consistent relative to absolute transition preserves original tolerance',()=>{
  const a=previous({time:1000000,seconds:80});
  const b=newer({time:1014000,seconds:null,resetTime:new Date(1080000).toISOString()});
  assert.equal(quotaEqual(a,b,true),true);
});
test('inconsistent relative to absolute transition updates',()=>{
  const a=previous({time:1000000,seconds:80});
  const b=newer({time:1014000,seconds:null,resetTime:new Date(1085000).toISOString()});
  assert.equal(quotaEqual(a,b,true),false);
});
test('same unknown reset fields stay equal',()=>{
  assert.equal(quotaEqual(previous({seconds:null}),newer({seconds:null}),true),true);
});
test('countdown removed from current event updates',()=>{
  assert.equal(quotaEqual(previous(),newer({seconds:null}),true),false);
});
