const test = require('node:test');
const assert = require('node:assert/strict');

const { buildReleaseChecklist } = require('../lib/publish.js');

test('builds release checklist with required files and scripts', () => {
  const checklist = buildReleaseChecklist({
    packageJson: {
      name: 'self-media-skill',
      version: '0.1.0',
      scripts: {
        test: 'node --test tests/*.test.js',
        'pack:check': 'npm pack --dry-run',
      },
      files: ['bin', 'lib', 'README.md', 'SKILL.md'],
    },
    fileExists: (targetPath) =>
      new Set([
        'D:\\AI_Skill\\self-media-skill\\README.md',
        'D:\\AI_Skill\\self-media-skill\\SKILL.md',
      ]).has(targetPath),
    packageRoot: 'D:\\AI_Skill\\self-media-skill',
  });

  assert.equal(checklist.ok, true);
  assert.equal(checklist.items.length, 6);
});

test('reports missing publish prerequisites', () => {
  const checklist = buildReleaseChecklist({
    packageJson: {
      name: '',
      version: 'not-semver',
      scripts: {},
      files: [],
    },
    fileExists: () => false,
    packageRoot: 'D:\\AI_Skill\\self-media-skill',
  });

  assert.equal(checklist.ok, false);
  assert.ok(checklist.items.some((item) => item.ok === false));
});
