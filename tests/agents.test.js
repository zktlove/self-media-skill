const test = require('node:test');
const assert = require('node:assert/strict');

const {
  getSupportedAgents,
  getAgentConfig,
  detectInstalledAgents,
  getCanonicalSkillsDir,
} = require('../lib/agents.js');

test('supports the requested agent list only', () => {
  assert.deepEqual(getSupportedAgents(), [
    'codex',
    'claude-code',
    'cursor',
    'trae',
    'opencode',
    'github-copilot',
    'gemini-cli',
    'kimi-cli',
    'windsurf',
    'openclaw',
    'trae-cn',
    'qoder',
    'qwen-code',
  ]);
});

test('resolves codex and claude global paths from env overrides', () => {
  const codex = getAgentConfig('codex', {
    homeDir: 'C:\\Users\\tester',
    env: { CODEX_HOME: 'D:\\CustomCodex', CLAUDE_CONFIG_DIR: 'D:\\CustomClaude' },
  });
  const claude = getAgentConfig('claude-code', {
    homeDir: 'C:\\Users\\tester',
    env: { CODEX_HOME: 'D:\\CustomCodex', CLAUDE_CONFIG_DIR: 'D:\\CustomClaude' },
  });

  assert.equal(codex.globalSkillsDir, 'D:\\CustomCodex\\skills');
  assert.equal(claude.globalSkillsDir, 'D:\\CustomClaude\\skills');
});

test('uses package canonical dir under user home', () => {
  assert.equal(
    getCanonicalSkillsDir({ homeDir: 'C:\\Users\\tester', scope: 'global' }),
    'C:\\Users\\tester\\.self-media-skill\\skills'
  );
});

test('uses package canonical dir inside cwd for project scope', () => {
  assert.equal(
    getCanonicalSkillsDir({
      homeDir: 'C:\\Users\\tester',
      cwd: 'D:\\AI_Skill\\self-media-skill',
      scope: 'project',
    }),
    'D:\\AI_Skill\\self-media-skill\\.self-media-skill\\skills'
  );
});

test('detectInstalledAgents only returns agents whose home markers exist', () => {
  const exists = (targetPath) =>
    new Set([
      'C:\\Users\\tester\\.codex',
      'C:\\Users\\tester\\.cursor',
      'C:\\Users\\tester\\.qoder',
    ]).has(targetPath);

  assert.deepEqual(
    detectInstalledAgents({
      homeDir: 'C:\\Users\\tester',
      env: {},
      exists,
    }),
    ['codex', 'cursor', 'qoder']
  );
});
