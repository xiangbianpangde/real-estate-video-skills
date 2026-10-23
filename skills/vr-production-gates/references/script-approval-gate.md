# 视频脚本—用户确认门禁

先交完整本版脚本，再等真实用户明确确认，最后制作。这里的暂停是用户要求的必经门禁，不是可被“持续推进”“自主完成”跳过的进度点。

## 加载与确认生效

Pi Skill正文只提供指令，不能拦截工具。硬拦截由包内[scripts/approval/index.ts](../scripts/approval/index.ts)扩展提供；本仓库的项目设置`.pi/settings.json`在项目受信任并重新加载后自动加载它。将Skill用于其他制作目录时，须同时显式加载同一个扩展，不复制第二份Skill：

```bash
pi --extension /path/to/vr-production-gates/scripts/approval/index.ts \
   --skill /path/to/vr-production-gates
```

`video_gate_status`实际返回`loaded=true`、`mode=production`才是当前宿主门禁已接入；看见文件、读过Skill或模型说“已加载”均不是证据。没有这个工具时，只准备脚本并说明需加载扩展；不能降级成无门禁制作。Python默认`python3`，宿主可通过`VR_GATE_PYTHON`指定已有运行时，不安装依赖。

维护本Skill而非制作房源时，由用户在Pi输入`/video-gate maintenance`允许代码编辑/测试；模型没有开启维护模式的工具。用户输入`/video-gate production`重新锁定。维护模式状态始终标`MAINTENANCE_ONLY`，不代表视频制作已批准；用户命令不由模型通过bash、工具回执或伪造消息代发。

## 提交、等待、解锁

1. **准备脚本**：默认`SCRIPT_REQUIRED`。允许读取素材、编写文档；`video_script_prepare`只运行固定的`inspect`资料清单、`build`剧本生成、`review`结构检查，不执行任意shell。制作所用的FFmpeg、TTS、浏览器求值/录制与其他执行类工具保持锁定。需要脚本前动态预检或任意SDK求值时，先另给本次候选脚本并审核，不把完整制作伪装为预检。
2. **提交本版**：`video_script_submit({record_path})`复用已有`check_shooting_plan --phase review`，核完整正文、源图、制作范围及本版口播/风险/音乐；单独HTML还必须与当前标准生成器输出逐字一致，并逐章核口播/风险/音乐/黄标，不能把必审内容藏进HTML。绑定实际审核文档及内容快照，只进入`PRESENTATION_REQUIRED`。record的`status`和`approval`字段不授予宿主权限。
3. **交给用户并停下**：assistant在聊天**单独一行**展示工具返回的本版完整脚本Markdown链接（其他范围说明另起段），随后请求审核并结束本轮。图片引用、代码块、引文或HTML注释中的伪链接不算交付。工具输出中的链接不算交付，生成成功、截图或模型说“用户已确认”都不算批准。此后状态为`USER_CONFIRMATION_REQUIRED`，同一轮继续制作仍会被拦截。
4. **真实用户确认**：宿主收到后续interactive或RPC用户输入，例如“审核通过，现在开始制作”“确认本版脚本，开始制作”，且该用户消息实际进入当前分支，才进入`USER_CONFIRMED`。无需用户读哈希或背固定口令；模糊的“确认/同意/好/继续”、室内/室外选择、提问、否定、引文、其他版本或extension注入均不能解锁。不确定时保持锁定，问清本版脚本是否通过。
5. **按已确认范围制作**：每次执行前重核本版内容快照及当前分支的展示/用户确认消息。模型仍须遵守列明的动作、费用、来源与不发布等范围；门禁不是任意shell的语义沙箱。已有CLI的采集/后期内容、来源与输出校验继续使用，不能用宿主已确认替代技术检查。

提交工具参数只接受record路径，没有`approved=true`、用户回复、令牌或跳过字段。批准不来自模型写的本地JSON、历史转录或旧批准文件；宿主内存保存当前有效确认。

## 变更、撤回与恢复

- 脚本正文、审核文档、来源/内容或制作范围变更会使快照失配并重锁；重新提交、展示、等待确认。提交失败也清除旧批准，不能沿用旧版继续。
- 输出目录、DPR/编码等已有规则认定的运行修复不改变内容快照，避免每次技术重试都要求重新审核。变更事实、覆盖、声音承诺、权利或费用仍回审。
- 用户撤回、要求暂停/修改、开始另一房源，或切到没有本次确认的分支会重锁。`/reload`或新会话默认重新锁定，不从模型可写的本地凭据自动恢复；确认状态不能因摘要而凭空迁移。
- 门禁状态工具和提交/准备操作按顺序执行；审批期间不并发改写本版脚本。文件外部改写会在下次执行前重核，但本扩展不提供操作系统级的文件锁或跨进程事务。

## 浏览器与验证边界

浏览器仍使用[Chrome DevTools MCP](../SKILL.md#浏览器工具)。未批准时仅开放已打开页面的列表、快照/截图和控制台/网络读取；导航也可能触发HTML主动内容，因此和任意`evaluate_script`、点击、录制一起锁住。用户可自行打开本版审核页供只读截图检查；不能让模型以导航审核页为名执行脚本。MCP缺失时准确说明，不换工具绕门禁；本轮模拟MCP测试只证明宿主在执行前拦截，不证明真实MCP或房源可用。

这是**加载本扩展的Pi会话工具执行门禁**，不是操作系统沙箱。未加载/被人禁用的扩展、外部命令行、其他进程、具有同等权限的恶意扩展不在覆盖内。确认后通用执行工具仍有自身范围约束，发布或新增费用不因脚本批准自动获准。未批准时默认拒绝未知执行工具，而非用危险命令关键词猜测是否制作。

## 可复现验收

```bash
# 原Python CLI与快照回归
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/vr-production-gates/tests -p 'test_*.py'

# 已安装Pi的真实AgentSession、工具hook与真实bash哨兵；离线faux响应，无模型费用
node skills/vr-production-gates/tests/test_approval_runtime.mjs
```

Node测试通过`PI_CODING_AGENT_PACKAGE`或`npm root -g`定位已安装Pi；Python可用`PYTHON`指定。它在独立临时工作目录验证未提交/未展示/伪批准/错版本/否定/偏好拒绝、真实interactive/RPC批准放行、漂移/撤回/分支重锁和维护边界，最后移除自己创建的工作目录。通过不等于房源成片、用户观感或真实MCP验收。
