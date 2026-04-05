const fs = require('fs');

function stripBom(text) {
  if (typeof text !== 'string') {
    return text;
  }
  return text.replace(/^\uFEFF/, '');
}

function loadJsonFile(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(stripBom(raw));
}

function normalizePublishMode(mode) {
  if (!mode) {
    return 'preview';
  }

  const normalized = String(mode).trim().toLowerCase();
  if (normalized === 'publish') {
    return 'publish';
  }
  if (['preview', 'draft', 'stop_before_publish', 'ready_before_publish'].includes(normalized)) {
    return 'preview';
  }
  return 'preview';
}

function getTopicSuggestionSelectionKeys() {
  return ['Enter'];
}

module.exports = {
  stripBom,
  loadJsonFile,
  normalizePublishMode,
  getTopicSuggestionSelectionKeys,
};
