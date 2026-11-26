import test from "node:test";
import assert from "node:assert/strict";
import { LEARNING_PATHS } from "../../frontend/js/paths-registry.js";

test("Learning Paths registry has unique IDs and valid stages",()=>{
  assert.ok(LEARNING_PATHS.length>=5);
  const ids=LEARNING_PATHS.map(path=>path.id);
  assert.equal(new Set(ids).size,ids.length);
  for(const path of LEARNING_PATHS){
    assert.ok(path.title);
    assert.ok(path.stages.length);
    for(const stage of path.stages){
      assert.ok(stage.title);
      assert.ok(stage.items.length);
      for(const item of stage.items){
        assert.ok(item.title);
        assert.match(item.href,/^#/);
        assert.ok(item.source);
      }
    }
  }
});
test("Paths link to existing PLD zones and use internal routes",()=>{
  const allLinks=LEARNING_PATHS.flatMap(path=>path.stages.flatMap(stage=>stage.items.map(item=>item.href)));
  assert.ok(allLinks.includes("#/aprender"));
  assert.ok(allLinks.includes("#/daw"));
  assert.ok(allLinks.includes("#/ciberseguridad"));
  assert.ok(allLinks.every(href=>href.startsWith("#/")));
});

import { pathProgress } from "../../frontend/js/paths-progress.js";

test("Python Path aggregates existing concept progress",async()=>{
  const oldFetch=globalThis.fetch,oldStorage=globalThis.localStorage;
  globalThis.fetch=async()=>({ok:true,json:async()=>({concepts:[{id:"a"},{id:"b"},{id:"c"}]})});
  globalThis.localStorage={getItem(key){return key==="pld:learn"?JSON.stringify({concepts:{a:{read:"2026-01-01"},b:{box:2},c:{box:1}}}):null}};
  try{assert.deepEqual(await pathProgress("python-developer"),{done:2,total:3,label:"conceptos",percent:67})}
  finally{globalThis.fetch=oldFetch;if(oldStorage===undefined)delete globalThis.localStorage;else globalThis.localStorage=oldStorage}
});

test("Excel Path reuses completed lessons from the existing course store",async()=>{
  const oldFetch=globalThis.fetch,oldStorage=globalThis.localStorage;
  globalThis.fetch=async()=>({ok:true,json:async()=>({modules:[{lessons:[{slug:"xl1"},{slug:"xl2"}]}]})});
  globalThis.localStorage={getItem(key){return key==="pld:course:excel"?JSON.stringify({done:{xl1:"2026-01-01"}}):null}};
  try{assert.deepEqual(await pathProgress("excel-professional"),{done:1,total:2,label:"unidades Excel",percent:50})}
  finally{globalThis.fetch=oldFetch;if(oldStorage===undefined)delete globalThis.localStorage;else globalThis.localStorage=oldStorage}
});
