const os = require('node:os');
const path = require('node:path');
const fs = require('node:fs');

const SUPPORTED_AGENTS = [
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
];

function defaultExists(targetPath) {
  return fs.existsSync(targetPath);
}

function getConfigHome(homeDir, env) {
  return (env && env.XDG_CONFIG_HOME) || path.join(homeDir, '.config');
}

function getCanonicalSkillsDir({
  homeDir = os.homedir(),
  cwd = process.cwd(),
  scope = 'global',
} = {}) {
  const baseDir = scope === 'project' ? cwd : homeDir;
  return path.join(baseDir, '.self-media-skill', 'skills');
}

function buildAgentDefinitions({ homeDir = os.homedir(), env = process.env } = {}) {
  const configHome = getConfigHome(homeDir, env);
  const codexHome = (env.CODEX_HOME || '').trim() || path.join(homeDir, '.codex');
  const claudeHome = (env.CLAUDE_CONFIG_DIR || '').trim() || path.join(homeDir, '.claude');

  return {
    codex: {
      name: 'codex',
      displayName: 'Codex',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(codexHome, 'skills'),
      markers: [codexHome],
    },
    'claude-code': {
      name: 'claude-code',
      displayName: 'Claude Code',
      projectSkillsDir: '.claude/skills',
      globalSkillsDir: path.join(claudeHome, 'skills'),
      markers: [claudeHome],
    },
    cursor: {
      name: 'cursor',
      displayName: 'Cursor',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(homeDir, '.cursor', 'skills'),
      markers: [path.join(homeDir, '.cursor')],
    },
    trae: {
      name: 'trae',
      displayName: 'Trae',
      projectSkillsDir: '.trae/skills',
      globalSkillsDir: path.join(homeDir, '.trae', 'skills'),
      markers: [path.join(homeDir, '.trae')],
    },
    opencode: {
      name: 'opencode',
      displayName: 'OpenCode',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(configHome, 'opencode', 'skills'),
      markers: [path.join(configHome, 'opencode')],
    },
    'github-copilot': {
      name: 'github-copilot',
      displayName: 'GitHub Copilot',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(homeDir, '.copilot', 'skills'),
      markers: [path.join(homeDir, '.copilot')],
    },
    'gemini-cli': {
      name: 'gemini-cli',
      displayName: 'Gemini CLI',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(homeDir, '.gemini', 'skills'),
      markers: [path.join(homeDir, '.gemini')],
    },
    'kimi-cli': {
      name: 'kimi-cli',
      displayName: 'Kimi Code CLI',
      projectSkillsDir: '.agents/skills',
      globalSkillsDir: path.join(configHome, 'agents', 'skills'),
      markers: [path.join(homeDir, '.kimi')],
    },
    windsurf: {
      name: 'windsurf',
      displayName: 'Windsurf',
      projectSkillsDir: '.windsurf/skills',
      globalSkillsDir: path.join(homeDir, '.codeium', 'windsurf', 'skills'),
      markers: [path.join(homeDir, '.codeium', 'windsurf')],
    },
    openclaw: {
      name: 'openclaw',
      displayName: 'OpenClaw',
      projectSkillsDir: 'skills',
      globalSkillsDir: path.join(homeDir, '.openclaw', 'skills'),
      markers: [
        path.join(homeDir, '.openclaw'),
        path.join(homeDir, '.clawdbot'),
        path.join(homeDir, '.moltbot'),
      ],
      resolveGlobalSkillsDir(currentHomeDir, exists = defaultExists) {
        if (exists(path.join(currentHomeDir, '.openclaw'))) {
          return path.join(currentHomeDir, '.openclaw', 'skills');
        }
        if (exists(path.join(currentHomeDir, '.clawdbot'))) {
          return path.join(currentHomeDir, '.clawdbot', 'skills');
        }
        if (exists(path.join(currentHomeDir, '.moltbot'))) {
          return path.join(currentHomeDir, '.moltbot', 'skills');
        }

        return path.join(currentHomeDir, '.openclaw', 'skills');
      },
    },
    'trae-cn': {
      name: 'trae-cn',
      displayName: 'Trae CN',
      projectSkillsDir: '.trae/skills',
      globalSkillsDir: path.join(homeDir, '.trae-cn', 'skills'),
      markers: [path.join(homeDir, '.trae-cn')],
    },
    qoder: {
      name: 'qoder',
      displayName: 'Qoder',
      projectSkillsDir: '.qoder/skills',
      globalSkillsDir: path.join(homeDir, '.qoder', 'skills'),
      markers: [path.join(homeDir, '.qoder')],
    },
    'qwen-code': {
      name: 'qwen-code',
      displayName: 'Qwen Code',
      projectSkillsDir: '.qwen/skills',
      globalSkillsDir: path.join(homeDir, '.qwen', 'skills'),
      markers: [path.join(homeDir, '.qwen')],
    },
  };
}

function getSupportedAgents() {
  return [...SUPPORTED_AGENTS];
}

function getAgentConfig(agentName, options = {}) {
  const definitions = buildAgentDefinitions(options);
  const exists = options.exists || defaultExists;
  const agent = definitions[agentName];

  if (!agent) {
    throw new Error(`Unsupported agent: ${agentName}`);
  }

  if (typeof agent.resolveGlobalSkillsDir === 'function') {
    return {
      ...agent,
      globalSkillsDir: agent.resolveGlobalSkillsDir(options.homeDir || os.homedir(), exists),
    };
  }

  return agent;
}

function getTargetBaseDir(agent, { scope = 'global', cwd = process.cwd() } = {}) {
  if (scope === 'project') {
    return path.join(cwd, agent.projectSkillsDir);
  }

  return agent.globalSkillsDir;
}

function detectInstalledAgents(options = {}) {
  const exists = options.exists || defaultExists;
  const homeDir = options.homeDir || os.homedir();

  return SUPPORTED_AGENTS.filter((agentName) => {
    const agent = getAgentConfig(agentName, options);
    return agent.markers.some((markerPath) => exists(markerPath.replace(/^~(?=$|[\\/])/, homeDir)));
  });
}

module.exports = {
  SUPPORTED_AGENTS,
  getSupportedAgents,
  getCanonicalSkillsDir,
  getAgentConfig,
  getTargetBaseDir,
  detectInstalledAgents,
};
