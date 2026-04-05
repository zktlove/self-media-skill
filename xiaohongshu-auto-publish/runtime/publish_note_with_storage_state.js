const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const helperModulePath =
  process.env.XHS_HELPER_MODULE_PATH ||
  path.join(__dirname, 'publish_helpers.js');
const {
  loadJsonFile,
  normalizePublishMode,
  getTopicSuggestionSelectionKeys,
} = require(helperModulePath);

const TARGET_URL = 'https://creator.xiaohongshu.com/publish/publish';
const CONFIG_PATH = process.env.XHS_PUBLISH_CONFIG_PATH;
const STORAGE_STATE_PATH = process.env.XHS_STORAGE_STATE_PATH;
const RESULT_PATH = process.env.XHS_RESULT_PATH;
const SCREENSHOT_PATH = process.env.XHS_SCREENSHOT_PATH;
const PUBLISH_MODE = normalizePublishMode(process.env.XHS_PUBLISH_MODE);

if (!CONFIG_PATH) {
  throw new Error('缺少 XHS_PUBLISH_CONFIG_PATH');
}
if (!STORAGE_STATE_PATH) {
  throw new Error('缺少 XHS_STORAGE_STATE_PATH');
}
if (!RESULT_PATH) {
  throw new Error('缺少 XHS_RESULT_PATH');
}
if (!SCREENSHOT_PATH) {
  throw new Error('缺少 XHS_SCREENSHOT_PATH');
}

const config = loadJsonFile(CONFIG_PATH);
const imagePaths = Array.isArray(config.image_paths) ? config.image_paths : [];

function writeResult(payload) {
  fs.writeFileSync(RESULT_PATH, JSON.stringify(payload, null, 2), 'utf8');
}

async function clickImageTab(page) {
  const switched = await page.evaluate(() => {
    const candidates = Array.from(document.querySelectorAll('*')).filter(
      (el) => (el.textContent || '').trim() === '上传图文',
    );
    for (const el of candidates) {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        el.dispatchEvent(
          new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window,
          }),
        );
        return true;
      }
    }
    return false;
  });

  if (!switched) {
    throw new Error('没有成功切换到上传图文标签');
  }

  await page.waitForTimeout(1500);
}

async function ensureLoggedIn(page) {
  await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);

  const currentUrl = page.url();
  if (/login/i.test(currentUrl)) {
    throw new Error(`登录态失效，当前跳转到了登录页: ${currentUrl}`);
  }
}

async function uploadImages(page) {
  if (!imagePaths.length) {
    throw new Error('配置里缺少 image_paths');
  }

  const fileInput = page.locator('input.upload-input[type="file"], input[type="file"]').first();
  await fileInput.setInputFiles(imagePaths);
  await page.waitForTimeout(8000);
}

async function fillTitle(page) {
  const selectors = [
    'input[placeholder*="标题"]',
    'textarea[placeholder*="标题"]',
    'input:not([type="file"])',
  ];

  for (const selector of selectors) {
    const candidates = page.locator(selector);
    const count = await candidates.count();
    for (let index = 0; index < count; index += 1) {
      const locator = candidates.nth(index);
      const box = await locator.boundingBox();
      if (!box || box.width <= 0 || box.height <= 0) {
        continue;
      }
      await locator.click({ force: true });
      await locator.fill(config.title);
      return { selector, index };
    }
  }

  throw new Error('没有找到可填写的标题输入框');
}

async function fillBody(page) {
  const selectors = [
    'div[contenteditable="true"]',
    '.ql-editor',
    '.ProseMirror',
    'textarea[placeholder*="描述"]',
    'textarea[placeholder*="正文"]',
    'textarea',
  ];

  for (const selector of selectors) {
    const candidates = page.locator(selector);
    const count = await candidates.count();
    for (let index = 0; index < count; index += 1) {
      const locator = candidates.nth(index);
      const box = await locator.boundingBox();
      if (!box || box.width <= 0 || box.height <= 0) {
        continue;
      }

      await locator.click({ force: true });
      const tagName = await locator.evaluate((el) => el.tagName.toLowerCase());
      const contentEditable = await locator.evaluate(
        (el) => el.getAttribute('contenteditable') === 'true',
      );

      if (tagName === 'textarea' || tagName === 'input') {
        await locator.fill(config.body);
      } else if (contentEditable || selector.includes('ql-editor') || selector.includes('ProseMirror')) {
        await page.keyboard.press('Control+A').catch(() => {});
        await page.keyboard.type(config.body, { delay: 20 });
      } else {
        continue;
      }

      return { locator, selector, index };
    }
  }

  throw new Error('没有找到可填写的正文编辑区');
}

async function placeCaretAtTextEnd(locator) {
  return await locator.evaluate((el) => {
    function findLastTextNode(root) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          return node.textContent && node.textContent.length > 0
            ? NodeFilter.FILTER_ACCEPT
            : NodeFilter.FILTER_SKIP;
        },
      });

      let current = null;
      while (walker.nextNode()) {
        current = walker.currentNode;
      }
      return current;
    }

    const selection = window.getSelection();
    const range = document.createRange();
    const lastTextNode = findLastTextNode(el);

    el.focus();
    if (lastTextNode) {
      range.setStart(lastTextNode, lastTextNode.textContent.length);
    } else {
      range.selectNodeContents(el);
      range.collapse(false);
    }

    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);

    return {
      focusNodeName: selection.focusNode?.nodeName || null,
      focusOffset: selection.focusOffset,
      focusTextTail: selection.focusNode?.textContent?.slice(-30) || null,
    };
  });
}

async function topicInserted(page, topic) {
  return await page.evaluate((topicText) => {
    const normalizedTopic = topicText.toLowerCase();
    return Array.from(document.querySelectorAll('.tiptap-topic')).some((el) => {
      const text = (el.textContent || '').replace(/\s+/g, '').trim().toLowerCase();
      return text.includes(`#${normalizedTopic}`);
    });
  }, topic);
}

async function clickFirstTopicSuggestion(page, topic) {
  await page.waitForTimeout(800);

  const clicked = await page.evaluate((topicText) => {
    const normalizedTopic = topicText.toLowerCase();
    const elements = Array.from(document.querySelectorAll('li, [role="option"], .item, button, div'))
      .filter((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) {
          return false;
        }

        const text = (el.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
        if (!text.startsWith(`#${normalizedTopic}`)) {
          return false;
        }

        if (!/浏览/.test(text) && text !== `#${normalizedTopic}`) {
          return false;
        }

        if (el.closest('[contenteditable="true"]')) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        const rectA = a.getBoundingClientRect();
        const rectB = b.getBoundingClientRect();
        if (rectA.top !== rectB.top) {
          return rectA.top - rectB.top;
        }
        if (rectA.left !== rectB.left) {
          return rectA.left - rectB.left;
        }
        const areaA = rectA.width * rectA.height;
        const areaB = rectB.width * rectB.height;
        return areaB - areaA;
      });

    const target = elements[0];
    if (!target) {
      return null;
    }

    const clickable = target.closest('li, button, div') || target;
    clickable.dispatchEvent(
      new MouseEvent('mousedown', {
        bubbles: true,
        cancelable: true,
        view: window,
      }),
    );
    clickable.dispatchEvent(
      new MouseEvent('mouseup', {
        bubbles: true,
        cancelable: true,
        view: window,
      }),
    );
    clickable.dispatchEvent(
      new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window,
      }),
    );

    return {
      clickedText: (clickable.textContent || '').replace(/\s+/g, ' ').trim(),
      tag: clickable.tagName,
      className: clickable.className || null,
    };
  }, topic);

  if (!clicked) {
    throw new Error(`没有找到话题建议项: ${topic}`);
  }

  await page.waitForTimeout(800);
  return clicked;
}

async function appendTopics(page, bodyLocator) {
  const steps = [];

  for (const topic of config.topics || []) {
    const beforeTyping = await placeCaretAtTextEnd(bodyLocator);
    await page.keyboard.type(`\n#${topic}`, { delay: 30 });
    await page.waitForTimeout(1000);

    let selectionMethod = 'keyboard';
    let clickedSuggestion = null;

    const selectionKeys = getTopicSuggestionSelectionKeys();
    for (const key of selectionKeys) {
      await page.keyboard.press(key).catch(() => {});
      await page.waitForTimeout(300);
    }
    await page.waitForTimeout(800);

    let inserted = await topicInserted(page, topic);
    if (!inserted) {
      selectionMethod = 'dom_click';
      clickedSuggestion = await clickFirstTopicSuggestion(page, topic);
      inserted = await topicInserted(page, topic);
    }

    if (!inserted) {
      throw new Error(`话题没有成功插入为平台标签: ${topic}`);
    }

    steps.push({
      topic,
      beforeTyping,
      selectionMethod,
      clickedSuggestion,
    });
  }

  return steps;
}

async function clickPublishButton(page) {
  const button = page.locator('button').filter({ hasText: /^发布$/ }).last();
  if (await button.count()) {
    await button.click({ force: true });
    return 'locator_click';
  }

  const clicked = await page.evaluate(() => {
    const candidates = Array.from(document.querySelectorAll('button, div, span')).filter((el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0 && (el.textContent || '').trim() === '发布';
    });
    const target = candidates[0];
    if (!target) {
      return false;
    }
    target.dispatchEvent(
      new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window,
      }),
    );
    return true;
  });

  if (!clicked) {
    throw new Error('没有找到发布按钮');
  }

  return 'dom_click';
}

async function collectDebugInfo(page) {
  return await page.evaluate(() => {
    const editor = document.querySelector('div[contenteditable="true"]');
    return {
      editorText: editor?.innerText || null,
      editorHtml: editor?.innerHTML || null,
      currentUrl: location.href,
      pageTextSnippet: (document.body?.innerText || '').slice(0, 1200),
      buttons: Array.from(document.querySelectorAll('button'))
        .slice(0, 50)
        .map((el) => (el.textContent || '').trim())
        .filter(Boolean),
    };
  });
}

async function detectPublishOutcome(page) {
  await page.waitForTimeout(5000);
  const debugInfo = await collectDebugInfo(page);
  const pageText = debugInfo.pageTextSnippet || '';

  if (/发布成功|笔记发布成功|查看笔记|内容管理|笔记管理|作品管理/.test(pageText)) {
    return {
      status: 'published',
      confirmationText: pageText.slice(0, 200),
    };
  }

  return {
    status: 'publish_clicked_pending_confirmation',
    confirmationText: pageText.slice(0, 200),
  };
}

async function main() {
  const browser = await chromium.launch({ headless: false, slowMo: 80 });
  const context = await browser.newContext({ storageState: STORAGE_STATE_PATH });
  const page = await context.newPage();

  try {
    await ensureLoggedIn(page);
    await clickImageTab(page);
    await uploadImages(page);
    const titleInfo = await fillTitle(page);
    await page.waitForTimeout(1000);
    const bodyInfo = await fillBody(page);
    await page.waitForTimeout(1000);
    const topicSteps = await appendTopics(page, bodyInfo.locator);
    await page.waitForSelector('text=发布', { timeout: 20000 });

    let status = 'ready_before_publish';
    let publishAction = null;
    let publishDetection = null;

    if (PUBLISH_MODE === 'publish') {
      publishAction = await clickPublishButton(page);
      publishDetection = await detectPublishOutcome(page);
      status = publishDetection.status;
    }

    await page.screenshot({ path: SCREENSHOT_PATH, fullPage: true });
    const debugInfo = await collectDebugInfo(page);

    writeResult({
      status,
      publishMode: PUBLISH_MODE,
      url: page.url(),
      screenshot: SCREENSHOT_PATH,
      title: config.title,
      body: config.body,
      topics: config.topics,
      titleInfo,
      bodyInfo: {
        selector: bodyInfo.selector,
        index: bodyInfo.index,
      },
      imagePaths,
      topicSteps,
      publishAction,
      publishDetection,
      debugInfo,
      savedAt: new Date().toISOString(),
    });

    console.log(status.toUpperCase());
    console.log(`RESULT_PATH=${RESULT_PATH}`);
    console.log(`SCREENSHOT_PATH=${SCREENSHOT_PATH}`);
  } catch (error) {
    const debugInfo = await collectDebugInfo(page).catch(() => null);
    writeResult({
      status: 'failed',
      message: error.message,
      publishMode: PUBLISH_MODE,
      url: page.url(),
      debugInfo,
      savedAt: new Date().toISOString(),
    });
    console.error(error);
    process.exitCode = 1;
  } finally {
    await page.waitForTimeout(1500).catch(() => {});
    await browser.close().catch(() => {});
  }
}

main();
