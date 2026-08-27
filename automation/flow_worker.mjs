#!/usr/bin/env node
// Dependency-free local Chrome/CDP worker. A dedicated Chrome profile preserves
// owner sign-in; secrets and cookies are never copied into request/result files.

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { spawn } from "node:child_process";

const arg = process.argv.indexOf("--request");
if (arg < 0 || !process.argv[arg + 1]) throw new Error("--request is required");
const requestPath = path.resolve(process.argv[arg + 1]);
const request = JSON.parse(await fs.readFile(requestPath, "utf8"));
const resultPath = path.resolve(request.result_path);
const debugPort = 9223;
const profile = path.resolve("automation/state/flow-chrome-profile");

async function result(status, detail = {}) {
  const payload = { run_id: request.run_id, job_id: request.job_id, action: request.action, status, detail, updated_at: new Date().toISOString() };
  await fs.mkdir(path.dirname(resultPath), { recursive: true });
  await fs.writeFile(resultPath, JSON.stringify(payload, null, 2), "utf8");
  return payload;
}

async function json(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP_${response.status}`);
  return response.json();
}

async function ensureChrome() {
  try { return await json(`http://127.0.0.1:${debugPort}/json/version`); } catch {}
  const candidates = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  ];
  let executable = "";
  for (const item of candidates) { try { await fs.access(item); executable = item; break; } catch {} }
  if (!executable) throw new Error("CHROME_NOT_FOUND");
  await fs.mkdir(profile, { recursive: true });
  spawn(executable, [`--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, "--no-first-run", "--new-window", request.flow_url], { detached: true, stdio: "ignore" }).unref();
  for (let i = 0; i < 30; i += 1) {
    await new Promise(resolve => setTimeout(resolve, 500));
    try { return await json(`http://127.0.0.1:${debugPort}/json/version`); } catch {}
  }
  throw new Error("CHROME_DEBUG_ENDPOINT_UNAVAILABLE");
}

class Cdp {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); }
  async open() {
    await new Promise((resolve, reject) => { this.ws.addEventListener("open", resolve, { once: true }); this.ws.addEventListener("error", reject, { once: true }); });
    this.ws.addEventListener("message", event => { const msg = JSON.parse(event.data); if (msg.id && this.pending.has(msg.id)) { const { resolve, reject } = this.pending.get(msg.id); this.pending.delete(msg.id); msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result); } });
  }
  send(method, params = {}, sessionId = "") { const id = ++this.id; this.ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) })); return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject })); }
  close() { this.ws.close(); }
}

async function findFlowTarget() {
  const targets = await json(`http://127.0.0.1:${debugPort}/json/list`);
  let target = targets.find(item => item.type === "page" && String(item.url).includes("labs.google/fx/tools/flow/project/"));
  if (!target) {
    target = await json(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(request.flow_url)}`, { method: "PUT" });
  }
  return target;
}

async function contexts(cdp, sessionId = "") {
  const found = new Map();
  cdp.ws.addEventListener("message", event => { const msg = JSON.parse(event.data); if ((msg.sessionId || "") === sessionId && msg.method === "Runtime.executionContextCreated") found.set(msg.params.context.id, msg.params.context); });
  await cdp.send("Runtime.enable", {}, sessionId);
  await new Promise(resolve => setTimeout(resolve, 1200));
  return [...found.values()].map(context => ({ contextId: context.id, context, sessionId }));
}

async function allContexts(cdp) {
  const scopes = await contexts(cdp);
  const targets = await cdp.send("Target.getTargets");
  for (const target of targets.targetInfos || []) {
    if (target.type !== "iframe" || target.url !== "about:srcdoc") continue;
    const attached = await cdp.send("Target.attachToTarget", { targetId: target.targetId, flatten: true });
    scopes.push(...await contexts(cdp, attached.sessionId));
  }
  return scopes;
}

async function evaluate(cdp, scope, expression) {
  const reply = await cdp.send("Runtime.evaluate", { contextId: scope.contextId, expression, awaitPromise: true, returnByValue: true, userGesture: true }, scope.sessionId);
  if (reply.exceptionDetails) throw new Error("FLOW_PAGE_EVALUATION_FAILED");
  return reply.result?.value;
}

async function importStep6(cdp, contextMap) {
  const bytes = await fs.readFile(request.source_path);
  const base64 = bytes.toString("base64");
  for (const scope of contextMap) {
    const present = await evaluate(cdp, scope, `Boolean([...document.querySelectorAll('input[type=file]')].find(x=>/\\.json|application\\/json/i.test(x.accept||'')))`).catch(() => false);
    if (!present) continue;
    return evaluate(cdp, scope, `(() => { const input=[...document.querySelectorAll('input[type=file]')].find(x=>/\\.json|application\\/json/i.test(x.accept||'')); if(!input)return false; const raw=atob(${JSON.stringify(base64)}); const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0)); const file=new File([bytes],'STEP6.json',{type:'application/json'}); const dt=new DataTransfer(); dt.items.add(file); input.files=dt.files; input.dispatchEvent(new Event('input',{bubbles:true,composed:true})); input.dispatchEvent(new Event('change',{bubbles:true,composed:true})); return {ok:true,name:file.name,size:file.size,accept:input.accept}; })()`);
  }
  throw new Error("FLOW_FILE_INPUT_NOT_FOUND");
}

async function enterStudio(cdp, contextMap) {
  const key = (await fs.readFile(request.access_key_path, "utf8")).trim();
  if (!key) throw new Error("FLOW_ACCESS_KEY_EMPTY");
  for (const scope of contextMap) {
    const prepared = await evaluate(cdp, scope, `(() => {
      const inputSelector='input,textarea,[contenteditable="true"]';
      const labelOf=(x)=>[
        x.placeholder,
        x.getAttribute('aria-label'),
        x.getAttribute('title'),
        x.name,
        x.id,
        x.closest('label')?.innerText,
        x.parentElement?.innerText,
      ].filter(Boolean).join(' ').replace(/\\s+/g,' ').trim();
      const visible=(x)=>{ const r=x.getBoundingClientRect(); const s=getComputedStyle(x); return r.width>20&&r.height>10&&s.visibility!=='hidden'&&s.display!=='none'; };
      const candidates=[...document.querySelectorAll(inputSelector)].filter(x=>visible(x)&&!x.disabled&&x.getAttribute('aria-disabled')!=='true');
      const input=candidates.find(x=>/ENTER ACCESS KEY|access key|รหัส/i.test(labelOf(x))) || (candidates.length===1?candidates[0]:null);
      if(!input)return false;
      input.scrollIntoView({block:'center',inline:'center'});
      input.focus();
      if (typeof input.select === 'function') input.select();
      input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,composed:true,key:'a',ctrlKey:true}));
      input.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,composed:true,key:'a',ctrlKey:true}));
      return {input_ready:true};
    })()`).catch(() => false);
    if (!prepared) continue;

    await cdp.send("Input.insertText", { text: key }, scope.sessionId);
    await new Promise(resolve => setTimeout(resolve, 250));

    const handled = await evaluate(cdp, scope, `(() => {
      const expectedLength=${key.length};
      const inputSelector='input,textarea,[contenteditable="true"]';
      const labelOf=(x)=>[
        x.placeholder,
        x.getAttribute('aria-label'),
        x.getAttribute('title'),
        x.name,
        x.id,
        x.closest('label')?.innerText,
        x.parentElement?.innerText,
      ].filter(Boolean).join(' ').replace(/\\s+/g,' ').trim();
      const visible=(x)=>{ const r=x.getBoundingClientRect(); const s=getComputedStyle(x); return r.width>20&&r.height>10&&s.visibility!=='hidden'&&s.display!=='none'; };
      const candidates=[...document.querySelectorAll(inputSelector)].filter(x=>visible(x)&&!x.disabled&&x.getAttribute('aria-disabled')!=='true');
      const input=candidates.find(x=>/ENTER ACCESS KEY|access key|รหัส/i.test(labelOf(x))) || (candidates.length===1?candidates[0]:null);
      if(!input)return false;
      const value=input.value||input.textContent||'';
      input.dispatchEvent(new InputEvent('input',{bubbles:true,composed:true,inputType:'insertText',data:'*'}));
      input.dispatchEvent(new Event('change',{bubbles:true,composed:true}));
      if(value.length!==expectedLength) return {key_entered:false,value_length:value.length};
      const controls=[...document.querySelectorAll('button,[role="button"],input[type="button"],input[type="submit"],a,[tabindex]:not([tabindex="-1"])')];
      const ctlLabel=(x)=>[x.innerText,x.value,x.getAttribute('aria-label'),x.getAttribute('title'),x.textContent].filter(Boolean).join(' ').replace(/\\s+/g,' ').trim();
      const enabled=(x)=>!x.disabled&&x.getAttribute('aria-disabled')!=='true'&&!/disabled/i.test(x.className||'');
      const button=controls.find(x=>visible(x)&&enabled(x)&&/เข้าสู่สตูดิโอ|enter studio/i.test(ctlLabel(x)));
      if(!button)return {key_entered:true,clicked:false};
      button.scrollIntoView({block:'center',inline:'center'});
      button.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,composed:true}));
      button.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,composed:true}));
      button.click();
      button.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,composed:true}));
      button.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,composed:true}));
      return {key_entered:true,clicked:true,label:ctlLabel(button)};
    })()`).catch(() => false);
    if (handled) {
      await new Promise(resolve => setTimeout(resolve, 2500));
      return true;
    }
  }
  return false;
}

async function accessKeyGateVisible(cdp, contextMap) {
  for (const scope of contextMap) {
    const visible = await evaluate(cdp, scope, `(() => {
      const text=(document.body?.innerText||'')+' '+[...document.querySelectorAll('input,textarea')].map(x=>x.placeholder||x.getAttribute('aria-label')||'').join(' ');
      return /ENTER ACCESS KEY|เข้าสู่สตูดิโอ|access key/i.test(text);
    })()`).catch(() => false);
    if (visible) return true;
  }
  return false;
}

async function expectedSceneCount() {
  try {
    const source = JSON.parse(await fs.readFile(request.source_path, "utf8"));
    const scenes = source?.movie?.scenes;
    return Array.isArray(scenes) ? scenes.length : 0;
  } catch {
    return 0;
  }
}

async function readyImageCount(cdp, contextMap) {
  let count = 0;
  for (const scope of contextMap) {
    count += Number(await evaluate(cdp, scope, `(() => {
      const visible=(x)=>{ const r=x.getBoundingClientRect(); const s=getComputedStyle(x); return r.width>100&&r.height>100&&s.visibility!=='hidden'&&s.display!=='none'; };
      return [...document.querySelectorAll('img')].filter(x=>visible(x)&&/(^data:image|flow-content\\.google\\/image)/i.test(x.currentSrc||x.src||'')).length;
    })()`).catch(() => 0));
  }
  return count;
}

async function studioReady(cdp, contextMap) {
  const text = await visibleText(cdp, contextMap);
  return /STEP\s*01|สไตล์หนัง/i.test(text) && /STEP\s*06|สร้างหนัง/i.test(text);
}

async function guard(cdp, contextMap) {
  const text = [];
  for (const scope of contextMap) {
    if (/google\.com/i.test(String(scope.context.origin || scope.context.name || ""))) continue;
    text.push(String(await evaluate(cdp, scope, "document.body?.innerText||''").catch(() => "")));
  }
  const joined = text.join("\n");
  for (const scope of contextMap) {
    const visibleChallenge = await evaluate(cdp, scope, `Boolean([...document.querySelectorAll('iframe[src*="recaptcha"][src*="bframe"]')].find(x=>{const r=x.getBoundingClientRect();return r.width>20&&r.height>20}))`).catch(() => false);
    if (visibleChallenge) throw new Error("BLOCKED_CAPTCHA");
  }
  if (/buy credits|purchase credits|ซื้อเครดิต|เครดิตไม่เพียงพอ/i.test(joined)) throw new Error("BLOCKED_CREDIT_PURCHASE_REQUIRED");
  if (/unusual activity|กิจกรรมที่ผิดปกติ|Please visit the Help Center/i.test(joined)) throw new Error("BLOCKED_GOOGLE_UNUSUAL_ACTIVITY");
  return joined;
}

const interactiveSelector = [
  "button",
  "[role='button']",
  "input[type='button']",
  "input[type='submit']",
  "a",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

async function clickButton(cdp, contextMap, pattern, label) {
  for (const scope of contextMap) {
    const clicked = await evaluate(cdp, scope, `(() => {
      const rx=new RegExp(${JSON.stringify(pattern)},'i');
      const items=[...document.querySelectorAll(${JSON.stringify(interactiveSelector)})];
      const labelOf=(x)=>[
        x.innerText,
        x.value,
        x.getAttribute('aria-label'),
        x.getAttribute('title'),
        x.textContent,
      ].filter(Boolean).join(' ').replace(/\\s+/g,' ').trim();
      const visible=(x)=>{ const r=x.getBoundingClientRect(); const s=getComputedStyle(x); return r.width>2&&r.height>2&&s.visibility!=='hidden'&&s.display!=='none'&&s.pointerEvents!=='none'; };
      const enabled=(x)=>!x.disabled&&x.getAttribute('aria-disabled')!=='true'&&!/disabled/i.test(x.className||'');
      const button=items.find(x=>visible(x)&&enabled(x)&&rx.test(labelOf(x)));
      if(!button)return false;
      button.scrollIntoView({block:'center',inline:'center'});
      button.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,composed:true}));
      button.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,composed:true}));
      button.click();
      button.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,composed:true}));
      button.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,composed:true}));
      return {ok:true,label:labelOf(button),tag:button.tagName,role:button.getAttribute('role')||''};
    })()`).catch(() => false);
    if (clicked) return true;
  }
  throw new Error(`BLOCKED_UI_CONTRACT_MISMATCH:${label}`);
}

async function enabledButtonCount(cdp, contextMap, pattern, rejectPattern = "") {
  let count = 0;
  for (const scope of contextMap) {
    count += Number(await evaluate(cdp, scope, `(() => {
      const rx=new RegExp(${JSON.stringify(pattern)},'i');
      const reject=${JSON.stringify(rejectPattern)}?new RegExp(${JSON.stringify(rejectPattern)},'i'):null;
      const labelOf=(x)=>[x.innerText,x.value,x.getAttribute('aria-label'),x.getAttribute('title'),x.textContent].filter(Boolean).join(' ').replace(/\\s+/g,' ').trim();
      const visible=(x)=>{ const r=x.getBoundingClientRect(); const s=getComputedStyle(x); return r.width>2&&r.height>2&&s.visibility!=='hidden'&&s.display!=='none'; };
      const enabled=(x)=>!x.disabled&&x.getAttribute('aria-disabled')!=='true'&&!/disabled/i.test(x.className||'');
      return [...document.querySelectorAll(${JSON.stringify(interactiveSelector)})].filter(x=>{
        const label=labelOf(x);
        return visible(x)&&enabled(x)&&rx.test(label)&&(!reject||!reject.test(label));
      }).length;
    })()`).catch(() => 0));
  }
  return count;
}

async function visibleText(cdp, contextMap) {
  const chunks = [];
  for (const scope of contextMap) {
    if (/google\.com/i.test(String(scope.context.origin || scope.context.name || ""))) continue;
    chunks.push(String(await evaluate(cdp, scope, "document.body?.innerText||''").catch(() => "")));
  }
  return chunks.join("\n");
}

async function verifyImagesReady(cdp, contextMap) {
  const expected = await expectedSceneCount();
  const ready = await readyImageCount(cdp, contextMap);
  if (expected > 0 && ready < expected) throw new Error("FLOW_IMAGES_NOT_READY_FOR_VIDEO");
  const videoButtons = await enabledButtonCount(cdp, contextMap, "สร้างวิดีโอ|generate video", "ทั้งหมด|all");
  const allVideoButtons = await enabledButtonCount(cdp, contextMap, "สร้างวิดีโอทั้งหมด|generate all videos");
  if (videoButtons <= 0 && allVideoButtons <= 0) throw new Error("FLOW_IMAGES_NOT_READY_FOR_VIDEO");
  return true;
}

async function verifyVideosGenerated(cdp, contextMap) {
  const text = await visibleText(cdp, contextMap);
  if (/ยังไม่มีวิดีโอที่พร้อมตัดต่อ|no videos? ready/i.test(text)) {
    throw new Error("FLOW_VIDEOS_NOT_READY_FOR_EXPORT");
  }
  const downloadButtons = await enabledButtonCount(cdp, contextMap, "ดาวน์โหลดวิดีโอ|download video");
  if (downloadButtons <= 0) throw new Error("FLOW_VIDEOS_NOT_READY_FOR_EXPORT");
  return true;
}

async function verifyVideosReadyForExport(cdp, contextMap) {
  const text = await visibleText(cdp, contextMap);
  if (/ยังไม่มีวิดีโอที่พร้อมตัดต่อ|no videos? ready/i.test(text)) {
    throw new Error("FLOW_VIDEOS_NOT_READY_FOR_EXPORT");
  }
  const exportButtons = await enabledButtonCount(cdp, contextMap, "ส่งออกรวมคลิป|export full clip|export clip");
  if (exportButtons <= 0) throw new Error("FLOW_EXPORT_NOT_READY");
  return true;
}

async function waitForIdle(cdp, contextMap, phase, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let stable = 0;
  while (Date.now() < deadline) {
    const text = await guard(cdp, contextMap);
    const busy = /กำลังสร้าง|generating|processing|กำลังประมวลผล|โปรดรอ/i.test(text);
    stable = busy ? 0 : stable + 1;
    if (stable >= 3) return;
    await result("RUNNING", { phase });
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  throw new Error(`FLOW_${phase}_TIMEOUT`);
}

async function runAction(cdp, contextMap) {
  const action = request.action;
  if (action === "FLOW_IMPORT_STEP6") return "IMPORTED";
  if (["FLOW_CREATE_ALL_IMAGES", "FLOW_RUN_TO_EXPORT"].includes(action)) {
    await clickButton(cdp, contextMap, "STEP\\s*06|สร้างหนัง", "STEP_06");
    await new Promise(resolve => setTimeout(resolve, 1500));
    contextMap = await allContexts(cdp);
    await clickButton(cdp, contextMap, "สร้างรูปทั้งหมด|create all images", "CREATE_ALL_IMAGES");
    await waitForIdle(cdp, contextMap, "IMAGE_GENERATION", 30 * 60 * 1000);
    contextMap = await allContexts(cdp);
    await verifyImagesReady(cdp, contextMap);
    if (action === "FLOW_CREATE_ALL_IMAGES") return "IMAGES_COMPLETE";
  }
  if (["FLOW_GENERATE_ALL_VIDEOS", "FLOW_RUN_TO_EXPORT"].includes(action)) {
    await clickButton(cdp, contextMap, "STEP\\s*06|สร้างหนัง", "STEP_06");
    await new Promise(resolve => setTimeout(resolve, 1500));
    contextMap = await allContexts(cdp);
    if (action === "FLOW_GENERATE_ALL_VIDEOS") await verifyImagesReady(cdp, contextMap);
    await clickButton(cdp, contextMap, "สร้างวิดีโอทั้งหมด|generate all videos", "GENERATE_ALL_VIDEOS");
    await waitForIdle(cdp, contextMap, "VIDEO_GENERATION", 60 * 60 * 1000);
    contextMap = await allContexts(cdp);
    await verifyVideosGenerated(cdp, contextMap);
    if (action === "FLOW_GENERATE_ALL_VIDEOS") return "VIDEOS_COMPLETE";
  }
  if (["FLOW_CREATE_COVER", "FLOW_RUN_TO_EXPORT"].includes(action)) {
    await clickButton(cdp, contextMap, "STEP\\s*07|ส่งออก", "STEP_07");
    await new Promise(resolve => setTimeout(resolve, 1500));
    contextMap = await allContexts(cdp);
    await verifyVideosReadyForExport(cdp, contextMap);
    await clickButton(cdp, contextMap, "สร้างปกใหม่|create new cover", "CREATE_COVER");
    await waitForIdle(cdp, contextMap, "COVER_GENERATION", 20 * 60 * 1000);
    contextMap = await allContexts(cdp);
    if (action === "FLOW_CREATE_COVER") return "COVER_COMPLETE";
  }
  if (["FLOW_EXPORT_1080P", "FLOW_RUN_TO_EXPORT"].includes(action)) {
    await clickButton(cdp, contextMap, "STEP\\s*07|ส่งออก", "STEP_07").catch(() => true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    contextMap = await allContexts(cdp);
    await verifyVideosReadyForExport(cdp, contextMap);
    await clickButton(cdp, contextMap, "1080P|1080p", "EXPORT_1080P");
    return "EXPORT_STARTED";
  }
  throw new Error("FLOW_ACTION_NOT_IMPLEMENTED");
}

try {
  await ensureChrome();
  const target = await findFlowTarget();
  const cdp = new Cdp(target.webSocketDebuggerUrl);
  await cdp.open();
  let contextMap = await allContexts(cdp);
  const bodyTexts = [];
  for (const scope of contextMap) {
    if (/google\.com/i.test(String(scope.context.origin || scope.context.name || ""))) continue;
    bodyTexts.push(String(await evaluate(cdp, scope, "document.body?.innerText||''").catch(() => "")));
  }
  const joined = bodyTexts.join("\n");
  if (/sign in|เข้าสู่ระบบ/i.test(joined) && !/STEP 01|สไตล์หนัง/i.test(joined)) { await result("BLOCKED_GOOGLE_SIGN_IN_REQUIRED", { profile }); cdp.close(); process.exit(3); }
  const studioEntered = await studioReady(cdp, contextMap) || await enterStudio(cdp, contextMap);
  contextMap = await allContexts(cdp);
  if (!await studioReady(cdp, contextMap) && (!studioEntered || await accessKeyGateVisible(cdp, contextMap))) {
    throw new Error("FLOW_ACCESS_KEY_ENTRY_NOT_CONFIRMED");
  }
  let imported = false;
  const mayContinueExistingStudio = ["FLOW_GENERATE_ALL_VIDEOS", "FLOW_CREATE_COVER", "FLOW_EXPORT_1080P"].includes(request.action);
  if (!mayContinueExistingStudio || await readyImageCount(cdp, contextMap) < await expectedSceneCount()) {
    imported = await importStep6(cdp, contextMap);
    await new Promise(resolve => setTimeout(resolve, 1500));
    contextMap = await allContexts(cdp);
  }
  const completed = await runAction(cdp, contextMap);
  await result(completed, { imported, output_path: request.output_path });
  cdp.close();
  process.exit(0);
} catch (error) {
  await result("FAILED", { error: String(error?.message || error).slice(0, 300) });
  process.exit(1);
}
