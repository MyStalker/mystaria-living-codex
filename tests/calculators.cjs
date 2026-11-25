const assert=require('node:assert/strict');
const rules=require('../assets/rules.js');
for(const [power,stages] of [[0,0],[.75,0],[.75000001,1],[1.75,1],[1.75000001,2],[3,2],[3.00000001,3]])assert.equal(rules.impact(power,1).stages,stages);
assert.equal(rules.impact(1,0),null);assert.equal(rules.impact(-1,1),null);
assert.equal(rules.spell(50,35,1),3725);assert.equal(rules.spell(50,35,20),9349.75);assert.equal(rules.spell(50,35,3),null);
assert.equal(rules.elementalSR(50,40,1),8252);assert.equal(rules.ritual(10),40);
console.log('Passed 14 operative calculator boundary assertions.');
