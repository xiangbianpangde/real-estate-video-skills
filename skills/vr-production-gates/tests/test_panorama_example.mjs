// Offline control-contract tests, NOT an SDK/VR visual acceptance test.
import assert from 'node:assert/strict';
import {runRoute} from '../scripts/technical_examples/panorama.mjs';
function mock() {
  const vector = x => ({x,toArray:()=>[x,0,0],clone:()=>vector(x),distanceTo:b=>Math.abs(x-b.x)});
  const f={work:{workCode:'synthetic-work'},state:{mode:'Panorama',panoIndex:0,longitude:0,latitude:0,fov:90},helperVisible:true,needsRender:false,pano:{panoIndex:0},observers:[0,1].map(i=>({position:vector(i),accessibleNodes:[1-i]})),camera:{position:vector(0),perspectiveCamera:{view:null}},calls:[]};
  f.renderer={ratio:2,domElement:{width:320,height:568},getPixelRatio(){return this.ratio;},setPixelRatio(v){this.ratio=v;}};
  f.controller={isReady:()=>true,isTileReady:()=>true};
  f.getPose=()=>({longitude:f.state.longitude,latitude:0,fov:f.state.fov,distance:0,offset:vector(f.pano.panoIndex)});
  f.setState=s=>{f.state=JSON.parse(JSON.stringify(s));f.pano.panoIndex=s.panoIndex;f.camera.position=vector(s.panoIndex);};
  f.updateCamera=async p=>{Object.assign(f.state,p);};
  f.preloadPano=async p=>{f.calls.push(['preload',p.panoIndex]);};f.render=()=>{};
  f.moveToPano=async (target,options)=>{f.calls.push(['move',target.panoIndex]);options.moveStartCallback();if(f.fail)throw Error('synthetic SDK failure');f.pano.panoIndex=target.panoIndex;f.camera.position=vector(target.panoIndex);Object.assign(f.state,{panoIndex:target.panoIndex,longitude:options.longitude});options.moveEndCallback();};
  return f;
}
const recipe={workCode:'synthetic-work',start:{pano:0,yawRad:1,fovDeg:80},width:320,height:568,dpr:1,tolerance:{fovDeg:.02,position:.001},steps:[{kind:'move',pano:1,yawRad:1,ms:1},{kind:'pan',yawRad:1.2,ms:1}]};
let cases=0;
{
  const f=mock(),before=JSON.stringify(f.state);const report=await runRoute(f,recipe,{pause:async()=>{}});
  assert.equal(report.status,'CONTROLS_CHECKED_VISUAL_PENDING');assert.equal(report.restored,true);assert.equal(JSON.stringify(f.state),before);assert.equal(Object.hasOwn(f,'syncState'),false);assert.equal(f.renderer.ratio,2);assert.equal(f.helperVisible,true);
  assert.deepEqual(f.calls.slice(0,2),[['preload',0],['preload',1]]);assert.equal(report.visual_verified,false);cases++;
}
{
  const f=mock();f.fail=true;const original=()=>true;Object.defineProperty(f,'syncState',{value:original,configurable:true,writable:true,enumerable:false});
  const report=await runRoute(f,recipe,{pause:async()=>{}});assert.equal(report.status,'FAILED');assert.equal(report.restored,true);assert.equal(f.syncState,original);assert.equal(Object.getOwnPropertyDescriptor(f,'syncState').enumerable,false);cases++;
}
{
  const f=mock();let stopped=0;f.fail=true;const report=await runRoute(f,recipe,{record:true,pause:async()=>{},recorderFactory:()=>async()=>{stopped++;return new Blob(['fixture']);}});
  assert.equal(stopped,1);assert.equal(report.restored,true);assert.equal(report.status,'FAILED');cases++;
}
{
  const f=mock();await assert.rejects(()=>runRoute(f,{...recipe,workCode:'other-work'}));assert.equal(f.calls.length,0);cases++;
}
console.log(JSON.stringify({passed:true,cases,kind:'offline mock control lifecycle, no real SDK or capture'}));
