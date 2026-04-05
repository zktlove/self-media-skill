const test = require('node:test');
const assert = require('node:assert/strict');

const { getInstallPlan, getUninstallPlan } = require('../lib/installer.js');

test('builds install plan for root skill and child skills into detected agents', () => {
  const plan = getInstallPlan({
    canonicalDir: 'C:\\Users\\tester\\.self-media-skill\\skills',
    targetAgents: [
      {
        name: 'codex',
        projectSkillsDir: '.agents\\skills',
        globalSkillsDir: 'C:\\Users\\tester\\.codex\\skills',
      },
      {
        name: 'qoder',
        projectSkillsDir: '.qoder\\skills',
        globalSkillsDir: 'C:\\Users\\tester\\.qoder\\skills',
      },
    ],
    skills: [
      { name: 'self-media-skill', sourceDir: 'D:\\AI_Skill\\self-media-skill' },
      { name: 'social-copywriting-workflow', sourceDir: 'D:\\AI_Skill\\self-media-skill\\social-copywriting-workflow' },
      { name: 'xiaohongshu-auto-publish', sourceDir: 'D:\\AI_Skill\\self-media-skill\\xiaohongshu-auto-publish' },
    ],
  });

  assert.equal(plan.length, 6);
  assert.equal(plan[0].canonicalDir, 'C:\\Users\\tester\\.self-media-skill\\skills\\self-media-skill');
  assert.equal(plan[0].targetDir, 'C:\\Users\\tester\\.codex\\skills\\self-media-skill');
  assert.equal(plan[5].targetDir, 'C:\\Users\\tester\\.qoder\\skills\\xiaohongshu-auto-publish');
});

test('builds project-scope install plan into project skill directories', () => {
  const plan = getInstallPlan({
    canonicalDir: 'D:\\AI_Skill\\self-media-skill\\.self-media-skill\\skills',
    targetAgents: [
      {
        name: 'claude-code',
        projectSkillsDir: '.claude\\skills',
        globalSkillsDir: 'C:\\Users\\tester\\.claude\\skills',
      },
    ],
    skills: [{ name: 'self-media-skill', sourceDir: 'D:\\AI_Skill\\self-media-skill' }],
    scope: 'project',
    cwd: 'D:\\AI_Skill\\self-media-skill',
  });

  assert.equal(plan.length, 1);
  assert.equal(plan[0].targetDir, 'D:\\AI_Skill\\self-media-skill\\.claude\\skills\\self-media-skill');
});

test('builds uninstall plan for selected skills and agents', () => {
  const plan = getUninstallPlan({
    canonicalDir: 'C:\\Users\\tester\\.self-media-skill\\skills',
    targetAgents: [
      {
        name: 'cursor',
        projectSkillsDir: '.agents\\skills',
        globalSkillsDir: 'C:\\Users\\tester\\.cursor\\skills',
      },
    ],
    skillNames: ['self-media-skill', 'xiaohongshu-auto-publish'],
    scope: 'global',
    cwd: 'D:\\AI_Skill\\self-media-skill',
  });

  assert.equal(plan.length, 2);
  assert.equal(plan[0].canonicalDir, 'C:\\Users\\tester\\.self-media-skill\\skills\\self-media-skill');
  assert.equal(plan[1].targetDir, 'C:\\Users\\tester\\.cursor\\skills\\xiaohongshu-auto-publish');
});
