/** Host-bound video-script approval. Load with Pi -e or project settings.
 * Closed by default. Only live interactive/RPC input after a displayed, pinned
 * script can unlock execution; model-written approval JSON is never authority.
 * This controls this Pi session, not other processes or hostile extensions.
 */
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {realpathSync} from 'node:fs';
import {dirname, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {Type} from '@earendil-works/pi-ai';
import type {ExtensionAPI, ExtensionContext} from '@earendil-works/pi-coding-agent';
import {approves, linksDocument, preparationAllowed, revokes} from './policy.mjs';

const run=promisify(execFile);
const here=dirname(fileURLToPath(import.meta.url));
const scripts=resolve(here,'..');
const skill=resolve(scripts,'..');
const words=(message:any)=>typeof message?.content==='string'?message.content:
  (message?.content||[]).filter((c:any)=>c.type==='text').map((c:any)=>c.text).join('\n');
const result=(value:unknown)=>({content:[{type:'text' as const,text:JSON.stringify(value,null,2)}],details:value});
const within=(path:string,root:string)=>path===root || path.startsWith(root+sep);
function canonical(path:string):string {
  try {return realpathSync(path);} catch {const parent=dirname(path);return parent===path?path:resolve(canonical(parent),path.slice(parent.length+1));}
}

type Snapshot={record_path:string;document_path:string;version:string;fingerprint:string;authorized_actions:string[];[key:string]:unknown};
type Pending={snapshot:Snapshot;sessionId:string;presented:boolean;shownMessage?:any;approved:boolean;userMessage?:any};

export default function(pi:ExtensionAPI) {
  let maintenance=false;
  let pending:Pending|undefined;
  let confirming:string|undefined;
  const lock=()=>{pending=undefined;confirming=undefined;};
  const branchHas=(ctx:ExtensionContext,message:any)=>ctx.sessionManager.getBranch().some((e:any)=>e.type==='message' && e.message.role===message?.role && e.message.timestamp===message?.timestamp && words(e.message)===words(message));
  const status=()=>({loaded:true,mode:maintenance?'maintenance':'production',
    state:maintenance?'MAINTENANCE_ONLY':!pending?'SCRIPT_REQUIRED':!pending.presented?'PRESENTATION_REQUIRED':pending.approved?'USER_CONFIRMED':'USER_CONFIRMATION_REQUIRED',
    version:pending?.snapshot.version,document_path:pending?.snapshot.document_path,
    production_authorized:!maintenance && pending?.approved===true});
  async function snapshot(path:string,cwd:string):Promise<Snapshot> {
    const {stdout}=await run(process.env.VR_GATE_PYTHON||'python3',[resolve(here,'snapshot.py'),resolve(cwd,path)],
      {cwd,encoding:'utf8',maxBuffer:1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
    const data=JSON.parse(stdout);
    if(data.review_passed!==true || !data.fingerprint) throw Error('Invalid script review snapshot');
    return data;
  }
  async function current(ctx:ExtensionContext) {
    const captured=pending;
    if(!captured || captured.sessionId!==ctx.sessionManager.getSessionId()) {lock();return false;}
    try {
      const actual=await snapshot(captured.snapshot.record_path,ctx.cwd);
      if(pending!==captured) return false;
      if(actual.fingerprint!==captured.snapshot.fingerprint) {lock();return false;}
      // Presentation has to remain on this branch; summaries or an abandoned
      // branch do not create approval. Reload always starts locked.
      if((pending.presented && !branchHas(ctx,pending.shownMessage)) || (pending.approved && !branchHas(ctx,pending.userMessage))) {
        lock();return false;
      }
      return true;
    } catch {if(pending===captured) lock();return false;}
  }
  pi.on('resources_discover',()=>({skillPaths:[skill]}));
  pi.on('session_start',()=>{maintenance=false;lock();});
  pi.on('session_switch',()=>{maintenance=false;lock();});
  pi.on('input',async(event,ctx)=>{
    confirming=undefined;
    if(event.source==='extension' || maintenance || !pending) return;
    if(/另一|另一个|另套|新(?:房源|视频|项目)|换(?:房源|一套)|another (?:house|video)|next listing/i.test(event.text)) {lock();return;}
    if(revokes(event.text)) {pending.approved=false;pending.userMessage=undefined;return;}
    if(pending.presented && await current(ctx) && approves(event.text,pending!.snapshot.version)) confirming=event.text;
  });
  pi.on('message_end',async(event,ctx)=>{
    if(!pending || !await current(ctx)) return;
    if(event.message.role==='user') {
      if(confirming && words(event.message)===confirming) {
        pending.approved=true;pending.userMessage=event.message;
        ctx.ui.setStatus('video-gate','脚本 '+pending.snapshot.version+' 已由用户确认');
      }
      confirming=undefined;return;
    }
    if(event.message.role==='assistant' && linksDocument(words(event.message),pending.snapshot.document_path,ctx.cwd)) {
      pending.presented=true;pending.shownMessage=event.message;
    }
  });
  pi.on('before_agent_start',()=>({message:{customType:'video-gate-status',
    content:'视频脚本门禁：'+JSON.stringify(status())+'。未获本版真实用户确认时，只准备/提交脚本并等待，不制作视频。',display:false}}));

  pi.on('tool_call',async(event,ctx)=>{
    if(maintenance) return;
    // Protect gate/config/session bytes even after approval. This is not an OS
    // sandbox: a human can disable an extension, and other processes are outside it.
    if(['write','edit'].includes(event.toolName) && typeof event.input.path==='string') {
      const path=canonical(resolve(ctx.cwd,event.input.path));
      const session=ctx.sessionManager.getSessionFile();
      if(within(path,canonical(skill)) || within(path,canonical(resolve(ctx.cwd,'.pi'))) || (session && path===canonical(session)))
        return {block:true,reason:'视频门禁配置/宿主会话不可由制作模型修改；维护仅由用户 /video-gate maintenance 开启。'};
      // A content change is caught by the pinned snapshot before execution;
      // writing an unrelated note does not invalidate an unchanged approval.
    }
    if(preparationAllowed(event.toolName,event.input) || event.toolName==='video_script_prepare') return;
    // Navigation is not read-only: even local HTML may execute active content.
    // Before approval, only observation tools on an already-open review page run.
    if(await current(ctx) && pending?.approved) return;
    return {block:true,reason:'视频脚本—用户确认门禁未通过：先用 video_script_prepare 准备完整脚本、video_script_submit 绑定本版，在聊天展示链接并等待用户明确确认。模型自填已批准、工具回执或旧版批准不解锁。当前：'+status().state};
  });

  pi.registerTool({name:'video_gate_status',label:'视频脚本门禁状态',description:'读取宿主门禁状态；状态来自当前Pi运行时，不读取模型自填approval。',
    parameters:Type.Object({}),executionMode:'sequential',
    async execute(_id,_args,_signal,_update,ctx){if(pending) await current(ctx);return result(status());}});
  pi.registerTool({name:'video_script_prepare',label:'准备视频脚本',description:'门禁锁定时只运行固定的资料清单、脚本生成或review检查；不采集、不调用配音、不执行任意shell。',
    parameters:Type.Object({action:Type.Union([Type.Literal('inspect'),Type.Literal('build'),Type.Literal('review')]),
      record_path:Type.Optional(Type.String()),listing_root:Type.Optional(Type.String()),floorplan:Type.Optional(Type.String()),output_dir:Type.Optional(Type.String())}),executionMode:'sequential',
    async execute(_id,args,signal,_update,ctx) {
      lock();const path=(name:unknown)=>{if(typeof name!=='string'||!name) throw Error('Explicit path required');return resolve(ctx.cwd,name);};
      let script:string,argv:string[];
      if(args.action==='inspect') {script='inspect_listing_materials.py';argv=[path(args.listing_root)];}
      else if(args.action==='build') {script='build_script_package.py';argv=['--record',path(args.record_path),'--floorplan',args.floorplan||'floorplan.png','--output-dir',path(args.output_dir)];}
      else {script='check_shooting_plan.py';argv=['--record',path(args.record_path),'--phase','review'];}
      const {stdout}=await run(process.env.VR_GATE_PYTHON||'python3',[resolve(scripts,script),...argv],
        {cwd:ctx.cwd,signal,encoding:'utf8',maxBuffer:1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
      return result({preparation_only:true,production_authorized:false,result:JSON.parse(stdout)});
    }});
  pi.registerTool({name:'video_script_submit',label:'提交视频脚本等待用户确认',description:'校验并冻结完整本版record/脚本，只进入待展示/待用户确认；随后必须在assistant文本展示返回的链接并停下等待。此工具不能批准制作。',
    parameters:Type.Object({record_path:Type.String()}),executionMode:'sequential',
    async execute(_id,args,_signal,_update,ctx) {
      lock();const data=await snapshot(args.record_path,ctx.cwd);
      pending={snapshot:data,sessionId:ctx.sessionManager.getSessionId(),presented:false,approved:false};
      return result({...status(),review_passed:true,link:`[视频脚本 ${data.version}](${data.document_path})`,
        next_action:'将此Markdown完整脚本链接单独一行交给用户（范围说明另起段），结束本轮并等待明确确认。'});
    }});
  pi.registerTool({name:'video_production_check',label:'核查已确认制作范围',
    description:'本版真实用户确认后运行固定capture/post结构检查；可预留采集目录，不录制、不配音、不渲染。宿主传递确认，模型不能填写批准或换record。',
    parameters:Type.Object({phase:Type.Union([Type.Literal('capture'),Type.Literal('post')]),claim:Type.Optional(Type.Boolean())}),executionMode:'sequential',
    async execute(_id,args,signal,_update,ctx) {
      if(maintenance || !await current(ctx) || !pending?.approved)
        throw Error('Requires a live production-mode user confirmation for this script');
      if(args.claim && args.phase!=='capture') throw Error('claim is capture-only');
      const pinned=pending;
      // No record mutation/exported approval token. Feed the current in-memory
      // fingerprint to the existing technical checker, which revalidates content.
      const request=JSON.stringify({phase:args.phase,claim:args.claim===true,fingerprint:pinned.snapshot.fingerprint});
      const stdout=await new Promise<string>((accept,reject)=>{
        const child=execFile(process.env.VR_GATE_PYTHON||'python3',
          [resolve(here,'snapshot.py'),pinned.snapshot.record_path,'--host-check'],
          {cwd:ctx.cwd,signal,encoding:'utf8',maxBuffer:1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}},
          (error,out,err)=>error?reject(Error(out||err||error.message)):accept(out));
        child.stdin?.end(request);
      });
      return result({...JSON.parse(stdout),authorization_source:'live_host_confirmation'});
    }});
  pi.registerCommand('video-gate',{description:'用户控制：status / maintenance（仅修Skill测试）/ production（重锁并制作）',
    handler:async(args,ctx)=>{
      const action=args.trim()||'status';
      if(action==='maintenance') {lock();maintenance=true;}
      else if(action==='production') {lock();maintenance=false;}
      else if(action!=='status') throw Error('Use /video-gate status|maintenance|production');
      ctx.ui.notify(JSON.stringify(status()),maintenance?'warning':'info');
    }});
}
