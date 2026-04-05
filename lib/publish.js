const fs = require('node:fs');
const path = require('node:path');

function isSemver(version) {
  return /^\d+\.\d+\.\d+(-[0-9A-Za-z-.]+)?$/.test(version || '');
}

function buildReleaseChecklist({
  packageJson,
  packageRoot,
  fileExists = (targetPath) => fs.existsSync(targetPath),
}) {
  const items = [
    {
      label: 'package.json name',
      ok: Boolean(packageJson.name && String(packageJson.name).trim()),
    },
    {
      label: 'package.json version',
      ok: isSemver(packageJson.version),
    },
    {
      label: 'README.md exists',
      ok: fileExists(path.join(packageRoot, 'README.md')),
    },
    {
      label: 'SKILL.md exists',
      ok: fileExists(path.join(packageRoot, 'SKILL.md')),
    },
    {
      label: 'test script exists',
      ok: Boolean(packageJson.scripts && packageJson.scripts.test),
    },
    {
      label: 'pack:check script exists',
      ok: Boolean(packageJson.scripts && packageJson.scripts['pack:check']),
    },
  ];

  return {
    ok: items.every((item) => item.ok),
    items,
  };
}

module.exports = {
  buildReleaseChecklist,
};
