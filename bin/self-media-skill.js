#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const { getSupportedAgents, detectInstalledAgents, getAgentConfig } = require('../lib/agents.js');
const { discoverSkills } = require('../lib/discover-skills.js');
const { installSkills, uninstallSkills } = require('../lib/installer.js');
const { buildReleaseChecklist } = require('../lib/publish.js');

function print(message = '') {
  process.stdout.write(`${message}\n`);
}

function printError(message) {
  process.stderr.write(`${message}\n`);
}

function parseArgs(argv) {
  const args = { _: [] };

  for (let index = 0; index < argv.length; index += 1) {
    const current = argv[index];

    if (current === '--agent') {
      args.agent = (argv[index + 1] || '')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
      index += 1;
      continue;
    }

    if (current === '--mode') {
      args.mode = argv[index + 1] || 'symlink';
      index += 1;
      continue;
    }

    if (current === '--scope') {
      args.scope = argv[index + 1] || 'global';
      index += 1;
      continue;
    }

    if (current === '--skill') {
      args.skill = (argv[index + 1] || '')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
      index += 1;
      continue;
    }

    if (current === '--dry-run') {
      args.dryRun = true;
      continue;
    }

    if (current === '--project') {
      args.scope = 'project';
      continue;
    }

    if (current === '--global') {
      args.scope = 'global';
      continue;
    }

    if (current === '--postinstall') {
      args.postinstall = true;
      continue;
    }

    args._.push(current);
  }

  return args;
}

function shouldSkipPostinstall() {
  if (process.env.SELF_MEDIA_SKILL_SKIP_POSTINSTALL === '1') {
    return true;
  }

  const isGlobalInstall =
    process.env.npm_config_global === 'true' || process.env.npm_config_location === 'global';

  return !isGlobalInstall;
}

function getPackageRoot() {
  return path.resolve(__dirname, '..');
}

function listAgents() {
  const supportedAgents = getSupportedAgents();
  const detectedAgents = detectInstalledAgents();

  print('Supported agents:');
  for (const agentName of supportedAgents) {
    const marker = detectedAgents.includes(agentName) ? '[detected]' : '[not detected]';
    print(`- ${agentName} ${marker}`);
  }
}

function listSkills() {
  const packageRoot = getPackageRoot();
  const skills = discoverSkills(packageRoot);

  print('Discovered skills:');
  for (const skill of skills) {
    print(`- ${skill.name} -> ${skill.sourceDir}`);
  }
}

function resolveAgents(requestedAgents) {
  if (requestedAgents && requestedAgents.length > 0) {
    return requestedAgents.map((agentName) => getAgentConfig(agentName));
  }

  return detectInstalledAgents().map((agentName) => getAgentConfig(agentName));
}

function resolveSkills(requestedSkillNames) {
  const packageRoot = getPackageRoot();
  const skills = discoverSkills(packageRoot);

  if (!requestedSkillNames || requestedSkillNames.length === 0) {
    return skills;
  }

  const requested = new Set(requestedSkillNames.map((item) => item.toLowerCase()));
  return skills.filter((skill) => requested.has(skill.name.toLowerCase()));
}

function printInstallResults(results) {
  for (const result of results) {
    const actionLabel = result.dryRun ? 'Would install' : 'Installed';
    const overwriteLabel =
      result.overwriteCanonical || result.overwriteTarget ? ' overwrite' : '';
    print(
      `${actionLabel} ${result.skillName} -> ${result.agentName} (${result.installedBy}, ${result.scope}${overwriteLabel})`
    );
    print(`  ${result.targetDir}`);
  }
}

function printUninstallResults(results) {
  for (const result of results) {
    const actionLabel = result.dryRun ? 'Would remove' : 'Removed';
    print(`${actionLabel} ${result.skillName} -> ${result.agentName} (${result.scope})`);
    print(`  ${result.targetDir}`);
  }
}

function runInstall(options = {}) {
  const packageRoot = getPackageRoot();
  const skills = resolveSkills(options.skill);
  const agents = resolveAgents(options.agent);

  if (skills.length === 0) {
    print('No matching skills were found in the package.');
    return 1;
  }

  if (agents.length === 0) {
    print('No supported agent installation was detected. Nothing to install.');
    return 0;
  }

  const results = installSkills({
    packageRoot,
    skills,
    targetAgents: agents,
    mode: options.mode || 'symlink',
    scope: options.scope || 'global',
    cwd: process.cwd(),
    dryRun: Boolean(options.dryRun),
  });

  printInstallResults(results);
  return 0;
}

function runUpdate(options = {}) {
  return runInstall(options);
}

function runUninstall(options = {}) {
  const skills = resolveSkills(options.skill);
  const agents = resolveAgents(options.agent);

  if (skills.length === 0) {
    print('No matching skills were found in the package.');
    return 1;
  }

  if (agents.length === 0) {
    print('No supported agent installation was detected. Nothing to remove.');
    return 0;
  }

  const results = uninstallSkills({
    skillNames: skills.map((skill) => skill.name),
    targetAgents: agents,
    scope: options.scope || 'global',
    cwd: process.cwd(),
    dryRun: Boolean(options.dryRun),
  });

  printUninstallResults(results);
  return 0;
}

function runReleaseCheck() {
  const packageRoot = getPackageRoot();
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')
  );
  const checklist = buildReleaseChecklist({
    packageJson,
    packageRoot,
  });

  print('Release checklist:');
  for (const item of checklist.items) {
    print(`- ${item.ok ? 'OK' : 'FAIL'} ${item.label}`);
  }

  try {
    const output = execFileSync('npm', ['view', packageJson.name, 'version', '--json'], {
      cwd: packageRoot,
      stdio: ['ignore', 'pipe', 'pipe'],
      encoding: 'utf8',
    }).trim();
    if (output) {
      print(`- INFO package name exists on npm: ${packageJson.name}`);
      print(`  latest published version: ${output.replace(/^"|"$/g, '')}`);
    }
  } catch {
    print(`- INFO package name not found on npm or registry query failed: ${packageJson.name}`);
  }

  return checklist.ok ? 0 : 1;
}

function runPublishHelp() {
  print('Publish flow:');
  print('1. npm test');
  print('2. npm run pack:check');
  print('3. npm run release:check');
  print('4. npm publish --access public');
  return 0;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] || 'install';

  if (args.postinstall && shouldSkipPostinstall()) {
    return;
  }

  if (command === 'list-agents') {
    listAgents();
    return;
  }

  if (command === 'list-skills') {
    listSkills();
    return;
  }

  if (command === 'install') {
    process.exitCode = runInstall(args);
    return;
  }

  if (command === 'update') {
    process.exitCode = runUpdate(args);
    return;
  }

  if (command === 'uninstall' || command === 'remove') {
    process.exitCode = runUninstall(args);
    return;
  }

  if (command === 'release-check') {
    process.exitCode = runReleaseCheck();
    return;
  }

  if (command === 'publish-help') {
    process.exitCode = runPublishHelp();
    return;
  }

  printError(`Unsupported command: ${command}`);
  process.exitCode = 1;
}

main();
