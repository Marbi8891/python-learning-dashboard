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
