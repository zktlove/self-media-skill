const fs = require('node:fs');
const path = require('node:path');

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);

  if (!match) {
    return {};
  }

  const result = {};
  const lines = match[1].split(/\r?\n/);

  for (const line of lines) {
    const separatorIndex = line.indexOf(':');
    if (separatorIndex === -1) {
      continue;
    }

    const key = line.slice(0, separatorIndex).trim();
    const value = line
      .slice(separatorIndex + 1)
      .trim()
      .replace(/^['"]|['"]$/g, '');

    result[key] = value;
  }

  return result;
}

function readSkill(skillDir, isRootSkill = false) {
  const skillPath = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    return null;
  }

  const content = fs.readFileSync(skillPath, 'utf8');
  const frontmatter = parseFrontmatter(content);

  if (!frontmatter.name || !frontmatter.description) {
    throw new Error(`Invalid SKILL.md metadata: ${skillPath}`);
  }

  return {
    name: frontmatter.name,
    description: frontmatter.description,
    sourceDir: skillDir,
    skillFile: skillPath,
    rootSkill: isRootSkill,
  };
}

function discoverSkills(packageRoot) {
  const skills = [];
  const rootSkill = readSkill(packageRoot, true);

  if (rootSkill) {
    skills.push(rootSkill);
  }

  const entries = fs.readdirSync(packageRoot, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    const nestedSkill = readSkill(path.join(packageRoot, entry.name), false);
    if (nestedSkill) {
      skills.push(nestedSkill);
    }
  }

  return skills;
}

module.exports = {
  discoverSkills,
};
