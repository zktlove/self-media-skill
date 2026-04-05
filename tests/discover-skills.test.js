const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { discoverSkills } = require('../lib/discover-skills.js');

test('discovers root skill and direct child skills that contain SKILL.md', () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'self-media-skill-discover-'));

  fs.writeFileSync(
    path.join(tempRoot, 'SKILL.md'),
    '---\nname: root-skill\ndescription: root\n---\n',
    'utf8'
  );
  fs.mkdirSync(path.join(tempRoot, 'child-a'));
  fs.writeFileSync(
    path.join(tempRoot, 'child-a', 'SKILL.md'),
    '---\nname: child-a\ndescription: child a\n---\n',
    'utf8'
  );
  fs.mkdirSync(path.join(tempRoot, 'child-b'));
  fs.writeFileSync(
    path.join(tempRoot, 'child-b', 'SKILL.md'),
    '---\nname: child-b\ndescription: child b\n---\n',
    'utf8'
  );
  fs.mkdirSync(path.join(tempRoot, 'ignored-dir'));
  fs.writeFileSync(path.join(tempRoot, 'ignored-dir', 'README.md'), 'ignore me', 'utf8');

  const names = discoverSkills(tempRoot).map((skill) => skill.name);

  assert.deepEqual(names, ['root-skill', 'child-a', 'child-b']);

  fs.rmSync(tempRoot, { recursive: true, force: true });
});
