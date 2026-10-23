// Deterministic host-boundary policy. Not a shell sandbox or intent classifier.
import {resolve} from 'node:path';
import {realpathSync, readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const readTools=new Set(['read','grep','find','ls','google_search','web_search','fetch_content','get_search_content','source_check','task_guard_checkpoint','ask_user_question']);
const textExtensions=/\.(?:md|json|jsonl|html|css|svg|txt|py|mjs|js|ts|toml|ya?ml)$/i;
export function preparationAllowed(name, args={}) {
  if(readTools.has(name) || name==='video_script_submit' || name==='video_gate_status') return true;
  if(name==='write' || name==='edit') return typeof args.path==='string' && textExtensions.test(args.path);
  // Discovery/observation only. Arbitrary browser evaluation, click, navigation,
  // recording and raw shells remain locked; they cannot be proven read-only by name.
  return /^mcp__[^_]*(?:chrome|devtools)[\w_]*__(?:list_pages|take_snapshot|take_screenshot|list_console_messages|get_console_message|list_network_requests|get_network_request)$/.test(name);
}

export function linksDocument(text, document, cwd) {
  // Only a standalone, visible Markdown link line is a presentation. Constrain
  // the format rather than treating images, code or HTML as clickable links.
  const visible=text.replace(/<!--[\s\S]*?(?:-->|$)/g,'');
  let fence;
  for(const line of visible.split('\n')) {
    const delimiter=/^ {0,3}(`{3,}|~{3,})/.exec(line);
    if(delimiter) {
      if(!fence) fence=delimiter[1];
      else if(delimiter[1][0]===fence[0] && delimiter[1].length>=fence.length) fence=undefined;
      continue;
    }
    if(fence || /^(?: {4}|\t)/.test(line)) continue;
    const match=/^ {0,3}\[([^\]\n]+)\]\(([^)\n]+)\)(?:[。！!]?\s*)$/.exec(line);
    if(!match) continue;
    try {
      const raw=match[2].replace(/^<|>$/g,'').split('#')[0];
      const path=raw.startsWith('file:')?fileURLToPath(raw):resolve(cwd,decodeURIComponent(raw));
      if(realpathSync(path)===realpathSync(document)) return true;
    } catch { /* Invalid links are not presentations. */ }
  }
  return false;
}

// Shared syntax only; the live host still owns source/branch/identity checks.
const confirmation=JSON.parse(readFileSync(new URL('./confirmation.json',import.meta.url),'utf8'));
export function approves(text, version) {
  if(typeof text!=='string') return false;
  const value=text.replace(new RegExp(confirmation.whitespace,'g'),' ').trim();
  if(!value || value.length>300 || new RegExp(confirmation.reject,'i').test(value)) return false;
  const versions=value.match(new RegExp(confirmation.versions,'gi')) || [];
  if(versions.some(v=>v.toLowerCase()!==version.toLowerCase())) return false;
  const prefix=new RegExp(confirmation.prefix,'i').exec(value);
  if(!prefix) return false;
  // Consume one token at a time; no ambiguous nested repetition/backtracking.
  let rest=value.slice(prefix[0].length);
  while(rest) {
    if(confirmation.separators.includes(rest[0])) {rest=rest.slice(1);continue;}
    const token=confirmation.tail_tokens.find(word=>rest.startsWith(word));
    if(token) {rest=rest.slice(token.length);continue;}
    const v=/^v[\w.-]+/i.exec(rest);
    if(!v || v[0].toLowerCase()!==version.toLowerCase()) return false;
    rest=rest.slice(v[0].length);
  }
  return true;
}

export function revokes(text) {
  return /不(?:要|同意|批准|确认|制作)|暂不|先(?:修改|调整|停止)|撤回|取消|停止|reject|do not|don['’]?t|\b(?:stop|cancel|revoke|withdraw)\b/i.test(text);
}
