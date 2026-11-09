const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const projectRoot = path.resolve(__dirname, '..');
const harness = fs.readFileSync(path.resolve(projectRoot, 'tools/test_sfx_harness.js'), 'utf8');

// Import generator
const execOptions = { cwd: projectRoot, env: { ...process.env, PYTHONPATH: projectRoot } };
const jsCode = execSync(`python3 -c "import sys; sys.path.insert(0, '${projectRoot}'); import tools.sfx_banks_generator as g; print(g.get_sfx_banks_js()); print(g.get_play_arcade_sfx_js())"`, execOptions).toString();

// Combine and evaluate
const vm = require('vm');
const contextObj = {
  console: console,
  require: require,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  document: {
    querySelectorAll: () => [],
    querySelector: () => null,
    getElementById: () => null
  }
};
contextObj.global = contextObj;
const context = vm.createContext(contextObj);

vm.runInContext(harness, context);
vm.runInContext(jsCode, context);

// Test every single sound across all 4 banks
const banks = vm.runInContext('SFX_BANKS', context);
console.log(`Found ${banks.length} SFX Banks:`);

let totalSounds = 0;
banks.forEach((bank, bIdx) => {
  console.log(`\nTesting ${bank.name} (${bank.sounds.length} sounds)...`);
  if (bank.sounds.length !== 27) {
    throw new Error(`Bank ${bank.name} has ${bank.sounds.length} sounds, expected exactly 27!`);
  }
  bank.sounds.forEach((s, sIdx) => {
    try {
      vm.runInContext(`playArcadeSfx('${s.id}')`, context);
      totalSounds++;
    } catch (e) {
      console.error(`Error playing sound [${s.id}] in bank ${bIdx}:`, e);
      throw e;
    }
  });
  console.log(`  All 27 sounds in ${bank.shortName} played successfully!`);
});

// Test switching banks
vm.runInContext(`
  switchSfxBank(0);
  switchSfxBank(1);
  switchSfxBank(2);
  switchSfxBank(3);
  switchSfxBank(0);
`, context);

console.log(`\nSUCCESS! Verified all ${totalSounds} sounds across all ${banks.length} banks!`);

process.exit(0);
