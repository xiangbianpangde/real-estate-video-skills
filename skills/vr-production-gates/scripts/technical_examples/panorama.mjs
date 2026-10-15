/** Extracted Five SDK recipe example. Importing does NOT navigate or record.
 * Supply the current authorized SDK instance and recipe. No embedded Work,
 * transport URL, global attempt counter or automatically executed capture.
 * Portable extraction is mock-tested, not yet validated on a real SDK session.
 */
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const copy = value => JSON.parse(JSON.stringify(value));
const angle = value => Math.atan2(Math.sin(value), Math.cos(value));

async function waitFor(check, timeout, pause) {
  const started = Date.now();
  while (!check()) {
    if (Date.now() - started > timeout) throw Error('SDK readiness/pose timeout');
    await pause(25);
  }
}

export function startCanvasRecorder(f, {fps = 30, bitRate = 8000000} = {}) {
  const canvas = f.renderer.domElement;
  if (!MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) throw Error('VP9 recorder unavailable');
  const stream = canvas.captureStream(0), track = stream.getVideoTracks()[0];
  if (typeof track.requestFrame !== 'function') {stream.getTracks().forEach(t => t.stop());throw Error('requestFrame unavailable');}
  const chunks = [];let raf, last = -Infinity, recorderError;
  const recorder = new MediaRecorder(stream, {mimeType: 'video/webm;codecs=vp9', videoBitsPerSecond: bitRate});
  recorder.ondataavailable = event => {if (event.data.size) chunks.push(event.data);};
  recorder.onerror = event => {recorderError = event.error || Error('Recorder failed');};
  const ended = new Promise(resolve => {recorder.onstop = resolve;});
  try {recorder.start(1000);} catch (error) {stream.getTracks().forEach(t => t.stop());throw error;}
  const tick = now => {
    try {
      f.needsRender = true;f.render();
      if (now - last >= 1000 / fps) {track.requestFrame();last = now;}
      raf = requestAnimationFrame(tick);
    } catch (error) {recorderError = error;}
  };
  raf = requestAnimationFrame(tick);
  return async () => {
    cancelAnimationFrame(raf);
    try {if (recorder.state !== 'inactive') {recorder.stop();await ended;}}
    finally {stream.getTracks().forEach(t => t.stop());}
    if (recorderError) throw recorderError;
    return new Blob(chunks, {type: 'video/webm;codecs=vp9'});
  };
}

export async function runRoute(f, recipe, {record = false, pause = sleep, recorderFactory = startCanvasRecorder} = {}) {
  if (f.work.workCode !== recipe.workCode) throw Error('Wrong current Work');
  const {fovDeg, yawRad, pano} = recipe.start, tolerance = recipe.tolerance;
  if (![fovDeg, yawRad, tolerance?.fovDeg, tolerance?.position].every(Number.isFinite) || fovDeg <= 0 || fovDeg >= 180 || tolerance.fovDeg <= 0 || tolerance.position <= 0)
    throw Error('Explicit finite start and task-specific tolerances required');
  if (![recipe.width,recipe.height].every(v => Number.isInteger(v) && v > 0) || !Number.isFinite(recipe.dpr) || recipe.dpr <= 0 || !f.observers[pano]) throw Error('Current canvas and point required');
  let current = pano;
  for (const step of recipe.steps) {
    if (!['hold','pan','move'].includes(step.kind) || !Number.isFinite(step.ms) || step.ms <= 0 || (step.kind !== 'hold' && !Number.isFinite(step.yawRad))) throw Error('Invalid route step');
    if (step.kind === 'move') {
      if (!f.observers[current]?.accessibleNodes.includes(step.pano)) throw Error('Non-adjacent route');
      current = step.pano;
    }
  }
  const original = {state: copy(f.state), position: f.camera.position.clone(), pose: f.getPose(), helper: f.helperVisible, pixelRatio: f.renderer.getPixelRatio(), sync: Object.getOwnPropertyDescriptor(f, 'syncState'), needsRender: f.needsRender};
  const result = {status: 'PENDING', events: [], restored: false, visual_verified: false};
  const sample = kind => {const p = f.getPose();result.events.push({kind, time_ms: Date.now(), pano: f.pano.panoIndex, longitude: p.longitude, fov: p.fov, position: f.camera.position.toArray()});};
  const ready = () => f.controller.isReady() && f.controller.isTileReady();
  const timeout = recipe.timeoutMs || 15000;
  let stopRecording;
  try {
    // Current APIs are inherited from a known case; hosts must verify their SDK.
    for (const index of new Set([pano,...recipe.steps.filter(s => s.kind === 'move').map(s => s.pano)]))
      await f.preloadPano({workCode: recipe.workCode, panoIndex: index});
    f.syncState = () => false;f.helperVisible = false;
    f.setState({mode: 'Panorama',workCode: recipe.workCode,panoIndex: pano,longitude: yawRad,latitude: 0,fov: fovDeg,distance: 0},true,false);
    await waitFor(ready, timeout, pause);
    // Explicit pose settlement avoids treating ready=true as animation complete.
    // This portable initialization variant still needs real-SDK verification.
    await f.updateCamera({longitude: yawRad,latitude: 0,fov: fovDeg},0,false);
    await waitFor(() => ready() && Math.abs(f.getPose().fov - fovDeg) <= tolerance.fovDeg && f.camera.position.distanceTo(f.observers[pano].position) <= tolerance.position,timeout,pause);
    f.renderer.setPixelRatio(recipe.dpr);f.needsRender = true;f.render();
    if (f.renderer.domElement.width !== recipe.width || f.renderer.domElement.height !== recipe.height) throw Error('Canvas dimensions mismatch');
    if (record) stopRecording = recorderFactory(f, recipe);
    sample('start');
    for (const step of recipe.steps) {
      sample('step_start');
      if (step.kind === 'hold') await pause(step.ms);
      else if (step.kind === 'pan') await f.updateCamera({longitude: step.yawRad,latitude: 0,fov: fovDeg},step.ms,false);
      else await new Promise((resolve,reject) => {
        // Wait for actual SDK completion/cancellation. A timer alone would not
        // stop navigation and could let late callbacks overwrite restoration.
        Promise.resolve().then(() => f.moveToPano({workCode: recipe.workCode,panoIndex: step.pano}, {duration: step.ms,longitude: step.yawRad,latitude: 0,fov: fovDeg,effect: 'fly',moveStartCallback: () => sample('move_started'),moveEndCallback: resolve,moveCancelCallback: () => reject(Error('Move cancelled'))},false)).catch(reject);
      });
      const pose = f.getPose();
      if (Math.abs(pose.fov - fovDeg) > tolerance.fovDeg || f.camera.perspectiveCamera.view?.enabled || (step.yawRad !== undefined && Math.abs(angle(pose.longitude-step.yawRad)) > tolerance.fovDeg*Math.PI/180)) throw Error('Camera pose/projection mismatch');
      if (step.kind === 'move' && f.camera.position.distanceTo(f.observers[step.pano].position) > tolerance.position) throw Error('Move endpoint mismatch');
      f.setState({mode: 'Panorama',workCode: recipe.workCode,panoIndex: f.pano.panoIndex,longitude: pose.longitude,latitude: pose.latitude,fov: pose.fov,offset: pose.offset.clone(),distance: pose.distance},false,false);
      sample('step_end');
    }
    result.status = 'CONTROLS_CHECKED_VISUAL_PENDING';
  } catch (error) {result.status = 'FAILED';result.error = String(error.stack || error);}
  finally {
    try {if (stopRecording) result.media = await stopRecording();} catch (error) {result.status='FAILED';result.recorder_error=String(error);}
    try {
      if (original.sync) Object.defineProperty(f, 'syncState', original.sync);else delete f.syncState;
      f.helperVisible = original.helper;f.needsRender = original.needsRender;f.renderer.setPixelRatio(original.pixelRatio);
      f.setState(original.state,true,false);
      await f.updateCamera({longitude: original.state.longitude,latitude: original.state.latitude,fov: original.state.fov},0,false);
      await waitFor(() => ready() && Math.abs(f.getPose().fov-original.pose.fov) <= tolerance.fovDeg && Math.abs(angle(f.getPose().longitude-original.pose.longitude)) <= tolerance.fovDeg*Math.PI/180 && f.camera.position.distanceTo(original.position) <= tolerance.position,timeout,pause);
      result.restored = (JSON.stringify(f.state) === JSON.stringify(original.state) && f.renderer.getPixelRatio() === original.pixelRatio && f.helperVisible === original.helper && Object.prototype.hasOwnProperty.call(f,'syncState') === !!original.sync);
      if (!result.restored) throw Error('State restoration mismatch');
    } catch (error) {result.status = 'FAILED';result.restore_error = String(error);}
  }
  return result;
}
