# 图文脚本与拍前提交协议

本协议解决“文件存在但用户没有真正看到可审对象”的问题。它约束提交证据，不替代房源事实合同、模型摄影合同或最终人审。

## 最小可审包

交付目录内保留同版本的：

1. `overview.png`：按[方案板版式合同](storyboard-layout.md)排版的整片方案板，含顶部目标/顺序、横向章节图文卡、下部户型/调整/待审范围；不是小缩略图接触表；
2. `S01.png`、`S02.png`……：保留为方案板各卡的**当前房源真实源图**，不是公开示意图、纯文字表或别的房源图片；
3. `plan_vN.md`：图文脚本正文，使用相对路径嵌入 PNG；
4. `review.jsonl`：实际会话中的助手展示事件与用户批准事件；
5. `record.json`：生产范围、输入SHA、脚本SHA、展示事件ID和批准事件ID。

章节可以对应连续镜头中的叙事段，不能把章节标题误写成剪辑切点。若某段没有可用真实源图，写明 `BLOCKED` 及补证入口，不拿抽象图卡冒充源证据。

## 每张章节卡必须包含

图像用途分为真实源参考、动作图示、布局预览。动作须有图形＋短说明；首镜必须实际画出当前获审方案的背景/户型/标题，不能只引用原室内截图。标题显式按叙事角色填写，详见[版式合同](storyboard-layout.md)。

- 段落ID（如 `S01`）、起止时间与总时长；
- 推进/转向动作、画面主体与观众应读懂的空间关系；
- 白色正文字幕、黄色事实锚点及 `verbatim_voiceover`/`editorial_keywords` 模式；
- 已批准素材库BGM方向、配音/音效状态；
- 事实来源、图像来源与SHA、实际现象/风险、用户视觉参考/原话/SHA及比较结论、连续性证据索引；
- 首镜户型图、尾镜室内引流等整体要求在对应卡和总览图中明确；
- `OPEN` / `BLOCKED` 状态，不能用“看起来可以”替代证据。

## 版式与文件检查分开

设计、组件和标准内容结构以[设计系统](../design-system/SPEC.md)为准，本协议只维护提交/批准证据。新包使用v3，scope.storyboard_layout绑定board/source/review路径，assets角色分别为overview/storyboard_source/layout_review。

layout-review.json使用vr-storyboard-layout-review/v1，记录board_sha256、source_sha256、segment_ids、all_images_loaded、no_overflow、reference_structure_matches、motion_diagrams_reviewed、opening_composite_reviewed和review_basis。必须基于实际浏览器及PNG检查填写；尾镜预览有CTA时一并核验并在review_basis留证。机器核字段和SHA，不认证审美、身份或用户接受。

## 实际呈现

提交时必须在同一可审事件中展示：完整 Markdown 正文（包含可解析图片语法）、正文SHA256、范围 `BUNDLE_SHA256`、版本和待确认项。以下不算提交：

- 只给 `plan_vN.md` 的路径；
- 只给纯文字技术表、JSON或镜头编号；
- 只给公开示意图、接触表或截图而不绑定真实源图；
- 用户批准后静默修改正文、PNG、范围、输入或CTA。

工具 `scripts/check_shooting_plan.py` 可检查图片、SHA、卡片、时间轴、提交事件、批准绑定、探索预算、当前成像方法预检及一次capture claim；仅后期新版还可绑定原母版且拒绝采集。成像方法/配置/源身份及报告路径必须在正文可审；预检合同与完整动态证据见 [连续规范](continuous-take.md#拍前成像证据合同)。检查器核报告声明与SHA，不观看画面，不认证报告作者、用户身份、事实/房况或拦截绕过入口。

## 一次审核与版本状态

- `DRAFT`：只可编辑，不可拍；
- `IN_REVIEW`：已提交，等待用户决定；
- `SCRIPT_APPROVED_ONCE`：指定版本/范围已批准，且当前动态预检/入口检查通过后可进行一次正式采集及列明后期；
- `SUPERSEDED`：新版本替代，历史保留；
- `BLOCKED`：事实、权利、素材或关键证据未解决。

批准文本必须明确批准该版及制作范围；单独说“批准”只有在实际提交事件紧邻且无歧义时才可作为会话语言，但记录中仍要保存完整引用和绑定事件。检查器不把任意孤立的“批准”升级成脚本批准。

批准后任何以下变化必须新版本、新展示、新批准：事实、覆盖/顺序、路线、首尾、字幕口径、BGM来源/权利、时长、成本、付费服务、CTA、输出范围或任何输入SHA。只改同母版内、已批准范围中的编码/字幕排版/混音不消费新的拍摄次数，但必须留独立后期版本和原件。

## 拍前检查与入口调用

Python 3.10+，仅标准库，无网络调用。路径相对 `record.json`（正文图路径相对Markdown），全部源文件SHA逐个回核；不覆盖原件。复制模板后填写真实值，模板本身必然失败，不能当生产许可。

```bash
# 只读：验证可审内容，取得正文SHA和范围BUNDLE_SHA256；草案未完成预检不授执行
python3 /path/to/vr-production-gates/scripts/check_shooting_plan.py \
  --record /path/to/private/plan_v1/record.json --phase review

# 实际呈现图文内容和摘要，保存真实review.jsonl事件；填写批准记录后：
# 仅退出码0才启动正式录制；先占用新的take目录并写capture-claim.json
python3 /path/to/vr-production-gates/scripts/check_shooting_plan.py \
  --record /path/to/private/plan_v1/record.json --phase capture --claim

# 已批准后期：核原批准与claim，不再消费拍摄次数
python3 /path/to/vr-production-gates/scripts/check_shooting_plan.py \
  --record /path/to/private/plan_v1/record.json --phase post
```

后续经新审核批准的**仅后期修订**：新记录设`scope.execution_mode=post_only`，`authorized_actions`移除`capture`，`scope.base_media={path,sha256}`绑定原始母版并将它列为`assets`的`role=master`；输出新目录，用`--phase post`核新版实际提交/批准和原母版SHA。该分支不要求/不创建旧拍摄claim，也不追认旧脚本批准；`--phase capture`一律拒绝。只授后期、不重拍；超出原范围的事实/CTA仍须新审核，原件不覆盖。

`review.jsonl`从真实会话导出两个事件，不自己编造：`id`、`parentId`、`message.role`、`message.content`文本保留。提交事件是assistant，含完整正文、正文SHA及字面`BUNDLE_SHA256: <hash>`；用户事件是user，回复该提交事件且有明确批准文字。工具检查相对顺序、reply绑定及引用一致，不认证事件作者身份；必须同时保留原会话位置以便回溯。

`BUNDLE_SHA256`仍由plan/assets/segments/scope/exploration的规范化JSON计算；当前预检报告及四类证据必须在assets绑定，方法/配置/报告摘要在scope绑定。因此改变正文/图片/输入/方法/预检/范围而仅刷新SHA不能沿用旧展示或旧批准。导出审阅片段后计算其SHA，不使用持续追加的整会话文件SHA作为冻结值。已批准记录不添加可变运行状态；运行结果另存证据。

旧v2只作历史读取/批准兼容，新制作包使用v3版式绑定，成像合同保持不变；3.2.0按[用户视觉标准](visual-acceptance.md)允许`PASS_WITH_LIMITATIONS`，需要已声明参考/真实决定/SHA、当前比较与正文披露，不需额外再批同类现象。有参考的PASS同样比较，不暗中按零重影收紧。用户改变标准时用原媒体另出报告，保留旧FAIL，不能仅刷新SHA沿用旧展示。`review`可审草案，capture/同次post核当前完整证据/三项控制技术PASS与有效视觉结果；post_only继续只做母版后期，不新增预检/claim或采集。

入口必须直接调用检查器并按退出码启动，不能提前读一次就绕过。`--claim`原子创建take目录，两个并发入口只能一个成功；错误/崩溃留目录，**不删除claim以重拍**。采集器向该新目录写入不存在的原始文件；后期版本新路径不可覆盖。现存历史take不自动接入新门禁，不改其旧脚本/批准，也不为补claim重新采集。

检查器不认证画面/参考相似度、方案可见性或用户身份；它核文件/字段，不作全局拦截。视觉决定文件复用已明确的用户原话，不用Agent重写或额外要求再批准参考；标准及限制入正文和BUNDLE后，只保留原来一次整包批准。真实展示还需会话/附件界面核对；完整视觉QC与最终实播另做。

## 公开仓库与私有房源

公开 Skill 只放抽象规则、PNG示意图和脱敏示例；真实房源图、视频、音频、模型和可识别信息留私有项目。私有项目不得覆盖 `AST-*` 原始资产、冻结合同或历史批准；新版本使用新路径，运行记录 append-only。
