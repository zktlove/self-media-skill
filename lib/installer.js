const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { getCanonicalSkillsDir, getTargetBaseDir } = require('./agents.js');

const EXCLUDED_NAMES = new Set([
  '.git',
  '.gitignore',
  '__pycache__',
  '.venv',
  'node_modules',
  'memory.md',
  '.DS_Store',
]);

function sanitizeName(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function ensureDir(targetDir) {
  fs.mkdirSync(targetDir, { recursive: true });
}

function removePath(targetPath) {
  fs.rmSync(targetPath, { recursive: true, force: true });
}

function pathExists(targetPath) {
  return fs.existsSync(targetPath);
}

function copyDirectory(sourceDir, targetDir) {
  ensureDir(targetDir);

  const entries = fs.readdirSync(sourceDir, { withFileTypes: true });
  for (const entry of entries) {
    if (EXCLUDED_NAMES.has(entry.name)) {
      continue;
    }

    const sourcePath = path.join(sourceDir, entry.name);
    const targetPath = path.join(targetDir, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(sourcePath, targetPath);
      continue;
    }

    fs.copyFileSync(sourcePath, targetPath);
  }
}

function copySkill(skill, targetDir) {
  ensureDir(targetDir);

  if (skill.rootSkill) {
    fs.copyFileSync(skill.skillFile, path.join(targetDir, 'SKILL.md'));
    return;
  }

  copyDirectory(skill.sourceDir, targetDir);
}

function createSymlink(targetDir, linkPath) {
  try {
    ensureDir(path.dirname(linkPath));
    removePath(linkPath);
    fs.symlinkSync(targetDir, linkPath, process.platform === 'win32' ? 'junction' : 'dir');
    return true;
  } catch {
    return false;
  }
}

function getInstallPlan({ canonicalDir, targetAgents, skills, scope = 'global', cwd = process.cwd() }) {
  const plan = [];

  for (const skill of skills) {
    const skillSlug = sanitizeName(skill.name);
    const skillCanonicalDir = path.join(canonicalDir, skillSlug);

    for (const agent of targetAgents) {
      const agentBaseDir = getTargetBaseDir(agent, { scope, cwd });
      plan.push({
        skillName: skill.name,
        skillSlug,
        sourceDir: skill.sourceDir,
        canonicalDir: skillCanonicalDir,
        agentName: agent.name,
        targetDir: path.join(agentBaseDir, skillSlug),
      });
    }
  }

  return plan;
}

function getUninstallPlan({
  canonicalDir,
  targetAgents,
  skillNames,
  scope = 'global',
  cwd = process.cwd(),
}) {
  const plan = [];

  for (const skillName of skillNames) {
    const skillSlug = sanitizeName(skillName);

    for (const agent of targetAgents) {
      const agentBaseDir = getTargetBaseDir(agent, { scope, cwd });
      plan.push({
        skillName,
        skillSlug,
        canonicalDir: path.join(canonicalDir, skillSlug),
        agentName: agent.name,
        targetDir: path.join(agentBaseDir, skillSlug),
      });
    }
  }

  return plan;
}

function installSkills({
  packageRoot,
  skills,
  targetAgents,
  mode = 'symlink',
  scope = 'global',
  cwd = process.cwd(),
  dryRun = false,
}) {
  const canonicalDir = getCanonicalSkillsDir({
    homeDir: os.homedir(),
    cwd,
    scope,
  });
  ensureDir(canonicalDir);

  const plan = getInstallPlan({
    canonicalDir,
    targetAgents,
    skills,
    scope,
    cwd,
  });

  const results = [];

  for (const entry of plan) {
    const skill = skills.find((item) => sanitizeName(item.name) === entry.skillSlug);
    const overwriteCanonical = pathExists(entry.canonicalDir);
    const overwriteTarget = pathExists(entry.targetDir);

    if (!dryRun) {
      removePath(entry.canonicalDir);
      ensureDir(entry.canonicalDir);
      copySkill(skill, entry.canonicalDir);
    }

    let installedBy = mode === 'symlink' ? 'symlink' : 'copy';
    if (!dryRun) {
      if (mode === 'symlink') {
        const linked = createSymlink(entry.canonicalDir, entry.targetDir);
        if (!linked) {
          installedBy = 'copy';
          removePath(entry.targetDir);
          copyDirectory(entry.canonicalDir, entry.targetDir);
        }
      } else {
        removePath(entry.targetDir);
        copyDirectory(entry.canonicalDir, entry.targetDir);
      }
    }

    results.push({
      ...entry,
      installedBy,
      overwriteCanonical,
      overwriteTarget,
      scope,
      packageRoot,
      dryRun,
    });
  }

  return results;
}

function uninstallSkills({
  skillNames,
  targetAgents,
  scope = 'global',
  cwd = process.cwd(),
  dryRun = false,
}) {
  const canonicalDir = getCanonicalSkillsDir({
    homeDir: os.homedir(),
    cwd,
    scope,
  });

  const plan = getUninstallPlan({
    canonicalDir,
    targetAgents,
    skillNames,
    scope,
    cwd,
  });

  const results = [];

  for (const entry of plan) {
    const targetExists = pathExists(entry.targetDir);
    const canonicalExists = pathExists(entry.canonicalDir);

    if (!dryRun) {
      removePath(entry.targetDir);
      removePath(entry.canonicalDir);
    }

    results.push({
      ...entry,
      removedTarget: targetExists,
      removedCanonical: canonicalExists,
      dryRun,
      scope,
    });
  }

  return results;
}

module.exports = {
  sanitizeName,
  getInstallPlan,
  getUninstallPlan,
  installSkills,
  uninstallSkills,
};
