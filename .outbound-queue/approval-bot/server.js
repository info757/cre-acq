#!/usr/bin/env node
/**
 * Approval bot: long-poll Telegram. On /start save chat_id. On callback_query
 * approve/<id> or delete/<id> run queue.sh send/delete. On edit/<id> ask for edit.
 * Only this process may run queue.sh send or queue.sh delete.
 */

const https = require('https');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const OUTBOUND_QUEUE_DIR = path.join(__dirname, '..');
const WORKSPACE_ROOT = path.join(OUTBOUND_QUEUE_DIR, '..');
const QUEUE_SCRIPT = path.join(OUTBOUND_QUEUE_DIR, 'queue.sh');
const CHAT_ID_FILE = path.join(OUTBOUND_QUEUE_DIR, 'approval_chat_id');

const ENV_FILE = path.join(WORKSPACE_ROOT, 'skills', 'n8n-trigger', '.env');
function loadToken() {
  if (process.env.TELEGRAM_APPROVAL_BOT_TOKEN) return process.env.TELEGRAM_APPROVAL_BOT_TOKEN;
  if (!fs.existsSync(ENV_FILE)) {
    console.error('TELEGRAM_APPROVAL_BOT_TOKEN not set and', ENV_FILE, 'not found');
    process.exit(1);
  }
  const content = fs.readFileSync(ENV_FILE, 'utf8');
  const m = content.match(/TELEGRAM_APPROVAL_BOT_TOKEN=(.+)/);
  if (!m) {
    console.error('TELEGRAM_APPROVAL_BOT_TOKEN not in', ENV_FILE);
    process.exit(1);
  }
  return m[1].trim().replace(/^["']|["']$/g, '');
}

const BOT_TOKEN = loadToken();
const API_BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;

function api(method, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(API_BASE + '/' + method);
    const data = JSON.stringify(body);
    const req = https.request(
      url,
      { method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            resolve(JSON.parse(buf));
          } catch (e) {
            reject(new Error(buf || res.statusCode));
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function runQueue(subcommand, id) {
  execSync(`"${QUEUE_SCRIPT}" ${subcommand} "${id}"`, {
    cwd: WORKSPACE_ROOT,
    stdio: 'pipe',
    env: { ...process.env, OUTBOUND_QUEUE_APPROVAL_BOT: '1' },
  });
}

async function handleUpdate(update) {
  if (update.message) {
    const text = (update.message.text || '').trim();
    if (text === '/start') {
      const chatId = update.message.chat.id;
      fs.writeFileSync(CHAT_ID_FILE, String(chatId), 'utf8');
      await api('sendMessage', { chat_id: chatId, text: 'Approval bot ready. Draft approvals will appear here.' });
    }
    return;
  }
  if (update.callback_query) {
    const { id: callbackId, data, message } = update.callback_query;
    const chatId = message.chat.id;
    const match = data && data.match(/^(approve|delete|edit):(.+)$/);
    if (!match) {
      await api('answerCallbackQuery', { callback_query_id: callbackId });
      return;
    }
    const [, action, draftId] = match;
    if (action === 'approve') {
      try {
        runQueue('send', draftId);
        await api('answerCallbackQuery', { callback_query_id: callbackId, text: 'Sent' });
      } catch (e) {
        await api('answerCallbackQuery', { callback_query_id: callbackId, text: 'Send failed' });
      }
      return;
    }
    if (action === 'delete') {
      try {
        runQueue('delete', draftId);
        await api('answerCallbackQuery', { callback_query_id: callbackId, text: 'Deleted' });
      } catch (e) {
        await api('answerCallbackQuery', { callback_query_id: callbackId, text: 'Delete failed' });
      }
      return;
    }
    if (action === 'edit') {
      await api('answerCallbackQuery', { callback_query_id: callbackId });
      await api('sendMessage', {
        chat_id: chatId,
        text: `Reply in the main OpenClaw chat with your edit instructions for draft ${draftId}.`,
      });
    }
  }
}

async function poll(offset) {
  const timeout = 30;
  const url = `${API_BASE}/getUpdates?timeout=${timeout}${offset ? `&offset=${offset}` : ''}`;
  const res = await new Promise((resolve, reject) => {
    https.get(url, (r) => { let b = ''; r.on('data', (c) => (b += c)); r.on('end', () => resolve(JSON.parse(b))); }).on('error', reject);
  });
  if (!res.ok) {
    if (res.error_code === 409) {
      console.error('Conflict: another process is long-polling this bot (only one getUpdates allowed per bot).');
      console.error('Stop the other process, then start this script again. Example:');
      console.error('  pkill -f "approval-bot/server.js"   # stop all approval-bot instances');
      console.error('  .outbound-queue/run-approval-bot.sh');
      process.exit(1);
    }
    console.error(res);
    return offset;
  }
  const updates = res.result || [];
  let nextOffset = offset;
  for (const u of updates) {
    nextOffset = u.update_id + 1;
    try {
      await handleUpdate(u);
    } catch (e) {
      console.error('handleUpdate', e);
    }
  }
  return nextOffset;
}

(async () => {
  let offset = 0;
  console.log('Approval bot polling...');
  while (true) {
    try {
      offset = await poll(offset);
    } catch (e) {
      console.error('poll error', e);
      await new Promise((r) => setTimeout(r, 5000));
    }
  }
})();
