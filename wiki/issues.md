# Bug 与问题台账

保存使用、维护 `vr-production-gates` 时实际发生的问题及修复进展。**本页是问题登记，不是运行证据，也不代表原视频已修复。** 与 [演化日志](logs.md)（版本变化）、[模式条目](index.md#模式条目)（可复用经验）分开；生产项目的当前状态仍以该项目指定入口为准。

## 登记方式

1. 遇到异常先检索本页；同一根因复发追加证据并重新打开原ID，不重复编号。
2. 新问题在下方新增条目，并更新总表：现象、预期、影响版本、最小复现/观察、证据、处理、验证和下一步。
3. 修复后写文件/提交引用；实际回归后才标 `verified`，写清验证范围。未运行、只给建议或只写规则，不算真实执行器/画质验证。
4. 详情的状态历史**只追加**，历史错误追加更正；总表只作为当前状态导航。代码/Skill回滚不删除bug记录，重新标记状态。
5. 公开只放脱敏描述、相对代码路径、测试名、事件ID与证据SHA。媒体、模型、房源身份、凭证和完整会话留私有，不复制进台账。

没有自动登记器、数据库或GitHub Issues同步；当前是人工/Agent按此格式维护的Markdown。

### 字段与状态

- ID：`ISSUE-YYYYMMDD-NNN`，编号唯一且稳定；首次发现日期与登记日期分别写，不能补造历史登记。
- 状态：`open`（待调查）→ `triaged`（已定位范围）→ `fixing` → `fixed`（改动已落盘，待回归）→ `verified`（约定范围实际回归通过）。`wontfix`须理由，`duplicate`须指向原ID；复发可回到`open`。
- 严重度：`critical`（数据损坏/系统不可用）、`high`（核心流程失败或越权）、`medium`（局部行为/维护问题）、`low`（文案/一致性）。
- 类型：`behavior` / `contract` / `evidence` / `environment`。
- 证据：至少可解析源码/测试/原始记录定位；私有证据注明其归档标识和SHA。摘要和台账本身不是独立证据。

## 当前总表

001–005为2026-10-13补登记的历史问题，状态以现有源码、已留存回归与原始观察为准；006–014来自[当前新房源制作案例](cases/CASE-20261013-001-current-skill-production.md)的实际执行，按发生时及时登记。状态只在明列范围内成立，不代表原视频已修复或完整新片已通过。

| ID | 现象 | 严重度 | 类型 | 状态 | 状态适用范围 |
|---|---|---|---|---|---|
| [ISSUE-20261013-001](#issue-20261013-001) | 只给脚本路径的批准曾被当成实际内容审核 | high | contract | verified | 新图文提交/批准检查器；不追认旧批准 |
| [ISSUE-20261013-002](#issue-20261013-002) | 拍前门禁未核当前方法动态证据，失败预检仍可能放行 | high | contract | verified | 3.1.0报告结构/SHA与拒绝逻辑；非自动视觉识别 |
| [ISSUE-20261013-003](#issue-20261013-003) | 修Skill任务被误转成视频修复，并被视频输入缺口阻塞 | medium | behavior | verified | 3.1.0规则及指定新会话场景；非全模型永久保证 |
| [ISSUE-20261013-004](#issue-20261013-004) | 旧采集入口未接新门禁，SDK状态恢复也未迁移 | high | contract | triaged | 已知生产集成缺口，尚未修改/重录旧入口 |
| [ISSUE-20261013-005](#issue-20261013-005) | 交接头的版本/测试计数滞后于当前Skill | low | contract | verified | 当前头与历史快照已分开；后续版本仍需维护 |
| [ISSUE-20261013-006](#issue-20261013-006) | 新案例输入中名为户型图的文件实际是点位接触表 | medium | evidence | verified | 本案例已独立获取并实际读回正确户型图；原资料库错名文件保留未改 |
| [ISSUE-20261013-007](#issue-20261013-007) | 当前SDK像素返回值被误当ImageData导致PNG导出失败 | medium | behavior | verified | 同pose转换后PNG实际读回正常；无录像/新探索预算 |
| [ISSUE-20261013-008](#issue-20261013-008) | 目标方向转经度少了SDK视轴符号，厨房预检实际朝餐区 | medium | behavior | verified | 同P1视轴点积1且实际读回厨房；只修控制，不证画质 |
| [ISSUE-20261013-009](#issue-20261013-009) | 新房源Model厨房目标静态画面已出现挂物/水龙头碎片 | high | evidence | triaged | CASE-20261013-001当前Model候选FAIL并停止；不是所有房源/方法均不可用 |
| [ISSUE-20261013-010](#issue-20261013-010) | 读取浏览器结果遗漏result包装，媒体未提取却继续调用ffmpeg | medium | behavior | verified | 从result提取已录2563729字节，真实全解码0；失败日志保留，不重新录制 |
| [ISSUE-20261013-011](#issue-20261013-011) | 当前全景SDK跨点移动出现窗框/水龙头半透明错位重影 | high | evidence | triaged | 新方法局部动态视觉FAIL，停止，不继承静态清楚或控制PASS |
| [ISSUE-20261013-012](#issue-20261013-012) | 逐帧state.offset浅引用在导出时全部变成末端位置 | medium | evidence | triaged | telemetry位置取actualPosition/clone pose，旧state.offset不作逐帧证据 |
| [ISSUE-20261013-013](#issue-20261013-013) | 连续预检录像媒体PTS短于录像墙钟，计划停留未被认证 | medium | evidence | triaged | WebM138帧/末帧4.512s与墙钟5.7025s分开，非CFR认证，不重录 |
| [ISSUE-20261013-014](#issue-20261013-014) | 单次异步实播表达式超时，媒体仍停在0秒 | medium | environment | verified | 短初始化＋真实点击后0→ended4.512s实际回读；不声称工具内部超时根因已修 |
| [ISSUE-20261013-015](#issue-20261013-015) | Agent用零伪影硬门槛替用户已认可试片的接受范围 | high | contract | verified | 3.2.0规范/CLI/指定新会话已纠正；不称旧媒体已修或当前新片已接受 |

| [ISSUE-20261013-016](#issue-20261013-016) | 核音乐许可时Google grounding拒绝当前用户地区 | medium | environment | triaged | 当前搜索API不可用，改直接读取官方许可；未修服务地区限制 |

| [ISSUE-20261013-017](#issue-20261013-017) | browser code内层另选session被工具拒绝 | low | behavior | verified | 改outer session后只读核查成功，未录制 |
| [ISSUE-20261013-018](#issue-20261013-018) | browser viewport已改但SDK画布仍保留横屏尺寸 | medium | environment | verified | 原生720×1280/无view核回，结束恢复1280×633；仅本次流程 |

| [ISSUE-20261013-019](#issue-20261013-019) | HTTPS页面读取本地transport脚本抛Failed to fetch | medium | behavior | verified | 自建handler方法与headers字段同名；已修HTTP200及媒体SHA，不证跨源上传 |

| [ISSUE-20261013-020](#issue-20261013-020) | 大媒体blob导出遇不可见锚点超时和code IPC上限 | medium | environment | verified | 显示原blob链接后native下载，字节/SHA匹配；仅本次导出修复 |

| [ISSUE-20261014-021](#issue-20261014-021) | 拍前口播超时与逐字字幕/摘要矛盾 | medium | contract | fixed | v2文案修正；实际TTS/成片未验证 |
| [ISSUE-20261014-022](#issue-20261014-022) | 室内引流及音乐/配音合同漏项 | medium | contract | fixed | v2范围补齐；待整包审核 |

| [ISSUE-20261014-023](#issue-20261014-023) | 原截图＋长文被当成参考版式的整体方案板 | high | contract | verified | 3.3.0规则/70项CLI/当前v3实际成图；非用户接受 |

| [ISSUE-20261014-024](#issue-20261014-024) | 动作无图示、首镜无实际合成布局 | high | contract | verified | 3.4.0＋合成渲染验证；非房源制作验收 |

## ISSUE-20261013-001

**现象：只给脚本路径的批准被当成实际内容审核。**

- 首次观察：2026-10-11生产过程；本次登记：2026-10-13。
- 影响/预期：用户未看完整图文内容便进入采集；预期实际展示正文、真实源PNG及摘要后再绑定批准。
- 观察证据：原提交事件 `d55c2888` 只列路径，批准事件 `cc74e24f`；私有过程日志 `PROC-0069` 的审核勘误保留。不能把它倒写成有效审核。
- 根因/修复：[图文协议](../skills/vr-production-gates/references/illustrated-script.md)及 [检查器](../skills/vr-production-gates/scripts/check_shooting_plan.py)核完整正文、SHA、真实提交/用户回复、范围摘要；新增于3.0.0，代码已收在提交 `3a42430`。
- 已运行验证：[CLI回归](../skills/vr-production-gates/tests/run.py)中 `test_path_only_is_not_submission`、`test_text_only`、`test_refreshed_hash_without_resubmission`；已留存44场景PASS。拒绝码 `plan_not_actually_presented` 等。
- 状态历史：2026-10-13补登记为 `verified`，仅限新检查器拒绝逻辑；旧take不补审、原件不变。
- 下一步：未来生产入口必须实际调用检查器；未接入的问题见004。

## ISSUE-20261013-002

**现象：3.0.0检查器只核图文/授权，未核当前成像方法的有效动态证据。**

- 首次观察/登记：2026-10-13；影响版本：3.0.0及未接门禁的旧入口。
- 影响/预期：旧同点全景、静态端点、`loaded/refined`或到达回调可能被当成Model/跨点可用；预期当前源/方法/配置/路线动态证据独立核验，已知FAIL不得放行。
- 复现：合成fixture缺预检报告、填 `static_endpoints` 或 `visual=FAIL`，刷新提交绑定以隔离成像门禁；修前CLI仍可返回0，红日志留私有归档 `技能成像门禁修复_20261013/门禁有效红测试_stderr.log`。不需要再次录房源复现。
- 修复：3.1.0，[检查器](../skills/vr-production-gates/scripts/check_shooting_plan.py)的 `render_precheck`及 [动态证据合同](../skills/vr-production-gates/references/continuous-take.md#拍前成像证据合同)，提交 `3a42430`。
- 已运行验证：`test_missing_render_precheck_blocks_claim`、`test_prior_method_pass_does_not_transfer`、`test_static_endpoints_not_dynamic_proof`、`test_visual_fail_not_overridden_by_control_pass`；最终44 CLI PASS，失败不建claim；新会话“旧方法不得继承”“动态失败”正确拒绝。
- 状态历史：2026-10-13补登记为 `verified`，仅证结构/SHA和规则行为；报告声明不自动证明画质，原视频畸变未修复。
- 下一步：复发时保留输入/错误码，不伪改视觉PASS；生产集成见004。

## ISSUE-20261013-003

**现象：将“修Skill”理解成“修视频”，继而以缺更好模型停止规则任务。**

- 首次观察/登记：2026-10-13。
- 影响/预期：工作对象与用户意图不一致；预期修改canonical及配套并验证，不自动导航/采样/录制，不因视频输入缺口停规则工作。
- 观察证据：用户事件 `0e0bf35c`明确“我的意思是将skils进行修复，并验证”；原对象偏离与纠正留私有会话/日志 `PROC-0073`。
- 修复：3.1.0 [Skill授权边界](../skills/vr-production-gates/SKILL.md#默认与授权边界)与 [触发回归](../skills/vr-production-gates/references/trigger-design.md)的3.1.0场景，提交 `3a42430`。
- 已运行验证：真实新进程 `cc-switch-open-code-go/deepseek-v4.1-flash` 的“对象纠偏”最终场景实际读取canonical并遵守对象边界；只读工具局限如实说明。最终8场景原记录归档，判定报告SHA `0bf9c586c624076f929dacab6ed022a5324727f34a259da125a3f1ce81077242`。
- 状态历史：2026-10-13补登记为 `verified`，仅限上述规则/场景，不宣称未来任何模型都不会偏离。
- 下一步：复发时重开本ID，记录本次用户原话/事件与实际动作。

## ISSUE-20261013-004

**现象：历史采集器直接录制，未调用新检查器；临时同步恢复仍写 `syncState=undefined`。**

- 首次观察：2026-10-12源码核查；本次登记：2026-10-13。
- 影响/预期：文档门禁不能约束直接旧入口；预期未来获准的新入口调用检查器，按返回码启动并正确恢复状态。
- 证据：私有生产脚本脱敏名 `take_v3g_record.js`（只读、未重跑），SHA `5d2154493a9c47d5b40baa3daa0a2896e9421134eb4fee313ef5976e7095d2b4`；有 `captureStream`及 `syncState=undefined`，没有检查器调用。另一次官方SDK连接回调后被旧state拉回的记录SHA `782da06337b971e6ab279c4ab9e5dc9fc92b1787a921e0f9af6b9022d8b371fd`，只支持该次控制失效，不把两者合并成同一录像故障。
- 当前处理：3.1.0 [SDK控制规则](../skills/vr-production-gates/references/continuous-take.md#sdk状态控制与恢复)已写实际主相机/描述符/delete恢复；新会话行为验证通过，**历史采集器没有改写或接入**，详见 [交接限制](../skills/vr-production-gates/HANDOFF.md)第12节。
- 状态历史：2026-10-13补登记为 `triaged`，规则已修与实际入口未修分开；不标生产集成verified。
- 下一步：未来另有新采集器开发范围时先做入口/恢复集成回归；本台账不授权改历史脚本、删除claim或重录。

## ISSUE-20261013-005

**现象：初次验证时Skill为3.1.0/44测试，HANDOFF当前头仍写3.0.0/27。**

- 首次观察/登记：2026-10-13真实新会话只读核对。
- 影响/预期：接手者可能把旧快照当当前结果；预期版本/计数有明确日期范围且以入口/真实验证为准。
- 证据：私有初次“对象纠偏”答复及修前交接字节；历史文本保留，不改成当时就已3.1.0。
- 修复：[HANDOFF](../skills/vr-production-gates/HANDOFF.md)当前头3.1.0，第12节列44，第11节标历史；提交 `3a42430`。
- 已运行验证：最终strict `validated=1/errors=0/warnings=0`、44 CLI；独立新会话读到入口/CHANGELOG/HANDOFF版本一致。
- 状态历史：2026-10-13补登记为 `verified`，本次文档一致性范围；不是长期防漂移保证。
- 下一步：后续修订同步当前头，旧版本/计数只保留为日期快照。

## ISSUE-20261013-006

**现象：本地输入的`VR层级户型图.jpg`实际是17点室内视图接触表。**

- 首次观察 / 登记：2026-10-13，新房源制作案例`CASE-20261013-001`，房源别名`HOUSE-REDACTED-002`。
- 影响 / 预期：不能按文件名自动用于首镜户型图；预期平面房间边界/门窗关系图，实际是Point0–Point16视图。属于外部输入类型/命名问题，不是Skill正确拒绝本身的bug。
- 复现 / 证据：实际读回该JPEG（1600×1080）可见17张室内图；原文件SHA `753a87f0691040793ffa1a096f92df54f3e1d6a71e5ba958636fa6429f380070`，私有案例归档`错误命名图像核验.json`记录原路径和观察。原始`defaultWork.json`有独立`hierarchy_floor_plan`入口。
- 根因：打包/命名环节未查明；已确认文件内容与名称不符，不猜定是谁或何时覆盖。
- 当前处理：保留原文件；只从当前Work配置定位正确户型来源，另存与绑定SHA，禁止改原图/用接触表冒充户型图。
- 状态历史：2026-10-13登记为`triaged`，获取及视觉核验正确图前不标fixed/verified。
- 下一步 / 关闭条件：独立保存当前Work真正户型图并实际读回，核来源和SHA；关闭仅指本案例使用正确素材，不表示资料库错名原件已改。
- 状态历史追加：2026-10-13 `triaged→fixed→verified`（本案例选材范围）。由同Work `hierarchy_floor_plan`取得2400×1800原JPEG，SHA `16eaa5b1a6099352fe11396320b25745533ec91a95f596be221bd0ba05a44544`；PNG SHA `87911a1c6c108445d15c96bc22db5ce7d4150cab9c4540e171aacb695c71771b`。实际读回厨房/客厅/三卧/卫浴/阳台边界及面积标注，私有`正确户型图来源.json`保留来源/转换；原错名文件未改。

## ISSUE-20261013-007

**现象：把当前Five6.6.20 `getPixels`的Uint8Array直接传给`putImageData`，PNG导出抛TypeError。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001`关键点静态预检。
- 影响版本与范围：本次采样适配表达式，不是SDK导航或画质判定；该次无录像、不创建正式claim。
- 预期 / 复现：相机已定位并回读后导出720×1280真实PNG；`putImageData(rawBytes,0,0)`报“parameter 1 is not of type ImageData”。失败表达式/工具错误保留在真实会话，私有`getPixels返回接口只读核对.json`含当前函数源码和控制值。
- 根因：当前函数实际返回`Uint8Array`，沿用旧调用写法未按运行接口转成`ImageData`。
- 当前处理：仅在同pose对长度做`W*H*4`检查后用`new ImageData(new Uint8ClampedArray(bytes),W,H)`转换，不新增机位、不重复连接/录像、没有自动重开预算。
- 状态历史：2026-10-13登记`open→triaged→fixing`；正确PNG读回前不称verified。
- 下一步 / 关闭条件：同pose正确导出、实际读回PNG并核尺寸/控制/状态，保留原失败。
- 状态历史追加：2026-10-13 `fixing→fixed→verified`，同pose实际返回`Uint8Array`长度3686400，转成`ImageData`后720×1280 PNG读回；PNG SHA `6ba2b9dade159421cbe3df9d077fa8ea7d6698dfbad11dd729ca6aea442f067e`。只证明像素导出修复，不证图中房间或画质；视向错误另记008。

## ISSUE-20261013-008

**现象：用`atan2(dx,dz)`计算目标经度，但当前主相机前向是矩阵-Z，得到反向画面。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001`同点静态预检；影响本次候选控制表达式，未改生产Skill。
- 预期 / 实际：从厨房点P1看向P2；位置误差约3.89e-8模型单位、FOV/画布正常，但主相机前向与目标位移相反，实际显示餐桌、桌椅与玄关柜。不能凭坐标有效称厨房画面正确。
- 证据：私有`关键预检_Model厨房P1_像素与控制.json`与对应PNG保留旧名称，SHA `6ba2b9dade159421cbe3df9d077fa8ea7d6698dfbad11dd729ca6aea442f067e`；实际读回餐区。该文件名是计划标签，不是正确房间结论。
- 根因：目标坐标→当前SDK经度转换遗漏相机-Z前向符号。根据实际主矩阵核视轴，不套用旧房源朝向例。
- 当前处理：同P1仅修正为`atan2(-dx,-dz)`并核主矩阵前向点积/真实厨房画面；不换位置/FOV/near/材料，算本问题第1组单变量核验，不录制、不重开关键预检预算。
- 状态历史：2026-10-13 `open→triaged→fixing`；修正样本读回前不称通过。
- 下一步 / 关闭条件：同点修正样本与目标视轴吻合，实际厨房内容可辨识；画质另判，不因控制修复标视觉PASS。
- 状态历史追加：2026-10-13 `fixing→fixed→verified`，`atan2(-dx,-dz)`修正后主视轴与目标点积1、P1位置误差约3.89e-8模型单位；PNG SHA `9dbd8969550f6a6f004fae1c541360bb13787fe2639f577955b2f6b996733321`实际读回厨房。仅限本SDK控制式，Model画质009仍FAIL。

## ISSUE-20261013-009

**现象：新案例当前Model厨房原点画面中水龙头/挂物断裂、碎片错接。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001` / `HOUSE-REDACTED-002`，Five6.6.20、model_mesh静态关键点，未录像。
- 预期 / 实际：真实厨房结构可读且无明显碎片；同P1朝P2的已核视轴画面中挂杆下器具和水龙头有多边形碎片、拉伸与错接。
- 证据：私有`关键预检_Model厨房P1_视轴修正.json`与720×1280 PNG（SHA `9dbd8969550f6a6f004fae1c541360bb13787fe2639f577955b2f6b996733321`）；位置误差3.89e-8模型单位、targetAxisDot=1、FOV85.57°/DPR1/near0.08/far800/view.enabled=false；当前模型+4贴图在线/本地SHA逐项一致、loaded/refined。
- 根因：当前Model表示/渲染链局部伪影，精确重建/纹理/SDK贡献未隔离；不把loaded、坐标或来源一致当画质通过，也不推断全屋或所有方法不可用。
- 当前处理：当前Model候选记静态视觉FAIL并停止，不录动态、不跑全屋、不换near/材质掩盖。新任务未限定唯一Model源，拟在本问题原2组预算内以同pose全景及当前官方连接验证另一方法；方法PASS不迁移。
- 状态历史：2026-10-13 `open→triaged`，尚未修复；拒绝失败采集是Skill正常门禁，不另记“拒绝”bug。
- 下一步 / 关闭条件：分别记录实际对照和新方法可用性，原Model未改则保持triaged，不能因替代方法出片关闭原伪影。
- 2026-10-13接受范围更正：用户`de658a6b`给厨房试片实际效果作基准；上文“无明显碎片”/静态FAIL是3.1.0旧AI门槛，不是用户已规定范围。原观察不变、状态triaged；3.2.0按用户标准另评，Model现象与参考不同不自动等同，也不自设零缺陷或必须换源。

## ISSUE-20261013-010

**现象：误把浏览器JSON包装当录像对象，提取断言失败后shell仍继续ffprobe/ffmpeg。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001`官方连接录像的离线检查。
- 影响 / 预期：尚未提取媒体就读取不存在的WebM，生成了空ffprobe输出和输入不存在错误日志；不能把最后`done`或工具外层exit0说成解码通过。
- 复现 / 证据：原JSON顶层是`lifecycle/origin/result`，录像在`result`；初次直接取顶层`video`触发AssertionError，后续工具错误“No such file or directory”留原会话/私有`对照2_厨房连接_全解码.log`，初次ffprobe JSON为空并保留。
- 根因：未回读实际包装层；shell无失败即停，使失败提取后仍触发依赖命令。
- 当前处理：从实际`result`取原始已录字节，逐命令返回码检查/`set -e`，新命名正式检查报告；不覆盖失败证据、不重录、不称空日志PASS。
- 状态历史：2026-10-13 `open→triaged→fixing`；原始媒体提取/全解码实际成功后才verified。
- 下一步 / 关闭条件：提取字节数与已录bytes相同、SHA固定，全解码真实返回0，失败报告保留且与有效报告区分。
- 状态历史追加：2026-10-13 `fixing→fixed→verified`，修后`set -e`与实际result层读取，提取字节2563729与录像元数据一致，WebM SHA `8350fc754f2273c814f0edd24e2d4f2810b545c7fffe30927a0e25deb0852b5e`；ffprobe有效报告非空、全解码真实返回0、138个解码帧，原失败日志/空报告未覆盖。仅修离线处理，不证画质。

## ISSUE-20261013-011

**现象：静态全景清楚，但当前SDK P1→P2 `fly`中出现半透明多重窗框、挂物、水龙头与抹布错位。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001` / `HOUSE-REDACTED-002`；与009的Model静态伪影分开，不套旧房源结论。
- 预期 / 实际：当前官方全景完整连接有忠实空间推进；实际原WebM070帧（PTS2.245s）窗框/水龙头/勺具及抹布明显重影。静态P1无该重影；两端清楚不证移动可用。
- 证据：原WebM SHA `8350fc754f2273c814f0edd24e2d4f2810b545c7fffe30927a0e25deb0852b5e`，138全部解码帧、4张全帧接触表实际读回及070原图。291实际相机遥测单调无回退、方向/FOV误差0、末端误差0.0004757628模型单位在0.001内；技术全解码0，均不替代视觉。
- 根因：官方当前跨点渲染/融合链中出现视觉伪影，精确子机制未隔离；无需继续逆向才判FAIL，不泛化全部SDK连接。
- 当前处理：本问题2组局部预算已用（同pose对照＋本次完整连接），停止当前连接/全屋预检，不重录、变速、AI补洞、改素材或硬切冒充连续。
- 状态历史：2026-10-13 `open→triaged`，局部动态视觉FAIL，生产入口不放行；不是Skill拒绝失败候选本身的bug。
- 下一步 / 关闭条件：需新有效同房源表示/连续实拍输入，或明确获准其他视频形式；原候选未修则不改verified。
- 2026-10-13接受范围更正：厨房参考SHA `0c08ab62ee3a23437d79657428e2b89cc784ad20f44e695dd0bdd73228855bae`经真实解析也有跨点重影，用户事件`de658a6b`明确其情况即接受范围。上文“需换源或形式”及重影直接FAIL为旧更严门槛，不再作为当前必需条件；3.2.0可用已保存媒体按该参考另评/披露。不修改原流/raw/历史FAIL，也未替用户宣布当前片已接受；现象triaged保留，规范错误另记015。

## ISSUE-20261013-012

**现象：遥测的`state:{...f.state}`仅浅复制，`state.offset`被后续运动写成同一个末端值。**

- 首次观察 / 登记：2026-10-13，读取本次预检导出JSON，`preRecord.state.offset`是P2末端，但`preRecord.actualPosition`与`pose.offset`仍是P1。
- 影响 / 预期：该字段不能证明逐帧state同步；预期采样瞬间独立数值，不是运行结束的可变引用。
- 证据：私有`对照2_厨房官方连接_原始流与遥测.json`、执行脚本`sample`；预检前实际P1与末端P2相距约0.822模型单位，浅state前记录末端值，与深度独立的`getPose()`/数组/主矩阵不同。
- 根因：`{...f.state}`不复制Vector3对象；外层JSON在整个动作结束后序列化。
- 当前处理：原JSON不可变、state.offset字段标不适用；轨迹核验只用已保存actualPosition/clone pose/主矩阵，不补造旧state时间序列。未来采样需offset复制为数值或深拷贝。
- 状态历史：2026-10-13 `open→triaged`；问题已定位但本次已录证据无法回补，不重录。
- 下一步 / 关闭条件：未来授权的新采样在变动前后验证独立snapshot；修建议和弃用字段不等于实际执行器回归。

## ISSUE-20261013-013

**现象：请求600ms起停留＋4000ms移动＋600ms尾停留，墙钟5.7025s，但原始媒体末帧PTS4.512s。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001`当前canvas MediaRecorder VP9连续预检。
- 预期 / 实际：媒体区间能够对应实际墙钟与计划停留；实际138个VFR帧、PTS首0末4.512s，实际导航调用到回调4.498s，墙钟/媒体不一致。最大PTS间隙0.05s只证时间戳无长洞，不证5.7s覆盖或CFR30。
- 证据：私有原WebM、`对照2_媒体时间轴与轨迹核验.json`与原始RAF/事件；media SHA同011。`canvas.captureStream(30)`不是恒定30帧保证。
- 根因：当前浏览器画布流/MediaRecorder时序贡献未隔离，不据静止帧猜定丢帧原因。
- 当前处理：保留原媒体与墙钟，技术/时长字段分别写，计划两端600ms不认证；不重录、插帧、延长、加速/变速或硬写CFR30。
- 状态历史：2026-10-13 `open→triaged`；未修复。视觉011已足够停止当前候选，时序问题不能成为再录一次的理由。
- 下一步 / 关闭条件：未来获准采集入口单独验证媒体PTS/时间基与计划，当前预检如实披露。

## ISSUE-20261013-014

**现象：初始化/等待/播放串在一次eval中超时30s，后续状态readyState=4但paused=true/currentTime=0。**

- 首次观察 / 登记：2026-10-13，`CASE-20261013-001`确切失败原WebM的浏览器技术实播。
- 影响 / 预期：初次调用没有完整播放证据；预期从0以1x到ended，不能把打开视频或工具超时当实播成功。
- 证据：原工具timeoutPartialProgress只确认当前URL、没有结果文件；真实snapshot有“播放”按钮，私有`实播超时_当前媒体状态.json`为duration4.512/readyState4/pausedtrue/time0/errornull。
- 根因：初次async等待链卡住的具体阶段未定位，可能加载/seek事件时序；不写已证实自动播放拦截，页面无media error。
- 当前处理：不盲目重跑原表达式；短调用安装可持久回读监听，再真实点击播放，有限条件等待后导出结果。没有新录像或扩探索。
- 状态历史：2026-10-13 `open→triaged→fixing`，实际ended回读前不标verified。
- 下一步 / 关闭条件：确切源从0到ended的事件/帧回调/错误/累计质量记录实际读回；失败记录保留。
- 状态历史追加：2026-10-13 `fixing→fixed→verified`（本案例实播操作范围）。短初始化后实际点“播放”，1x从0→ended4.512s，wall4525.7ms/136帧回调、media/window error0、waiting/stalled0；累计quality total276/corrupted0/dropped3含初次加载/定位，不称本次精确帧数或零掉帧。有效实播JSON SHA `143725cbad4bac4484b3e7da46185dd4fac76a1829f270cb84c5a4fd8b0cdd82`；视觉011仍FAIL，原超时保留。

## ISSUE-20261013-015

**现象：Agent将“重影/变形即FAIL”固定为执行门槛，覆盖用户已认可厨房试片的实际接受范围。**

- 首次明确纠正 / 登记：2026-10-13，用户真实事件`de658a6b`；影响3.1.0规范/门禁及本次生产判断。
- 预期 / 实际：用户决定观看效果的接受范围；3.1.0要求无明显伪影并无有效带限制执行分支，导致同类过渡重影自动停止、提出必须换源/硬切。指定已接受参考实际也有重影，其整体布局表达/节奏仍获接受，不能用Agent理想替用户标准。
- 证据：参考SHA `0c08ab62ee3a23437d79657428e2b89cc784ad20f44e695dd0bdd73228855bae`与历史V3接受原件一致；私有只读解析/原MP4及WebM5.5s证明跨点伪影，后段同点横扫清楚；用户原话“这个视频的情况就是我的接受范围，现在更新skills相关的规范，不要自认为规定我的接受范围”。修前合法参考内带限制fixture被`render_precheck_not_passed:visual`拒绝，红日志保留。
- 根因：把观察到现象与是否符合用户标准混成一项、缺少用户参考/带限制分支；之前“正常门禁拒绝不记bug”只适用正确标准拒绝，不豁免AI私设门槛。
- 修复引用：`vr-production-gates@3.2.0`，[用户视觉规范](../skills/vr-production-gates/references/visual-acceptance.md)、现有检查器/测试。用户原话/参考SHA及当前比较/正文披露绑定；PASS_WITH_LIMITATIONS有效，不重复索同类缺陷许可、不自设新数值阈值；未知/超范围和控制/身份失败分开。
- 实际验证：64 CLI红→绿；合法带限制capture/同次post通过，缺依据/错用户role/Agent改写/不比较/隐瞒限制/参考漂移/超范围/控制FAIL拒绝。strict0/0、Pi唯一3.2.0隔离加载0诊断；真实新进程按原工具轨迹/语义验证用户基准优先、不重录/强制硬切及不代签最终接受。
- 状态历史：2026-10-13 `open→triaged→fixing→fixed→verified`（规范/检查器/指定规则场景）；合成测试不证画质、真人身份、原片已修或新片用户已接受。
- 下一步 / 关闭条件：后续制作复用媒体按用户基准比较，旧FAIL/raw保留、新评审另存，不因标准修订自动重拍/扩预算/发布；再次擅自收紧则重开本ID。

## ISSUE-20261013-016

**现象：制作案例核音乐许可时，Google grounding返回用户地区不支持。**

- 首次观察 / 登记：2026-10-13，CASE-20261013-002。
- 状态 / 严重度 / 类型：triaged / medium / environment。
- 预期 / 实际：只读查官方许可，实际`User location is not supported for the API use.`；没有授权推断或新付费调用。
- 证据：本次原工具错误留会话；私有归档`Skill320完整制作_20261013/权利搜索服务失败_保留.json`，SHA `c59c8c1b4ff6b1b55dba9cbc72c647849ff8fefded7928b61f3f65eac88a88f5`。
- 当前处理：不重试同服务、不安装搜索器；直接fetch官方Mixkit许可并核已有素材来源。该调用已成功取得官方页，不等于原Google服务被修复。
- 状态历史：2026-10-13 open→triaged；仅定位当前调用环境拒绝。
- 下一步：用直接官方证据继续制作；服务地区问题不阻塞全部任务，不标verified或伪称搜索成功。

## ISSUE-20261013-017

**现象：agent_browser_code内层浏览器命令重复选择session，工具拒绝。**

- 首次观察 / 登记：2026-10-13，CASE-20261013-002，low/behavior。
- 原错误：`A code call uses one browser identity. Set session/namespace on agent_browser_code to choose another browser.`
- 原因 / 处理：session属于outer code工具参数，不应放inner native argv；修正后一条只读同Work检查成功，无录制/预算重开。
- 证据：真实工具失败/随后成功原事件留私有；异常摘要SHA `2dd8e1c4ca29191f4d81b436b4624a7c863e8a1e889a860930ede7d50c924570`。
- 状态历史：open→triaged→fixed→verified，仅本次调用式修复，不称工具内部改动。

## ISSUE-20261013-018

**现象：native viewport设置720×1280成功，SDK renderer仍1280×633。**

- 首次观察 / 登记：2026-10-13，CASE-20261013-002，medium/environment。
- 原始回读：innerWidth/Height=720/1280，canvas=1280/633、aspect=2.0221169，SDK画布CSS仍旧横屏；未运行预检或裁切采样。
- 证据：私有`视口设置与画布异步核查.json`及工具原结果；异常摘要SHA同017。
- 当前处理：原会话状态已存，当前视口重载原页面，复核viewport/canvas/DPR/aspect/view后再开始唯一全路线预检。具体页面resize机制未隔离。
- 状态历史：open→triaged→fixing；没有录制重试/预算消费，不冒称已恢复。
- 下一步：核原生720×1280主相机及结束时恢复旧1280×633；实际回核前不标verified。

- 2026-10-13追加验证：重载后实际720×1280、DPR1、aspect0.5625/view=null且预检未消费；录制后恢复原1280×633/P0/FOV96/主投影/pose逐项一致。状态fixing→fixed→verified，只指本次控制操作。

## ISSUE-20261013-019

**现象：官方HTTPS房源页fetch本地HTTP脚本失败，未启动预检。**

- 首次观察 / 登记：2026-10-13，CASE-20261013-002，medium/environment/triaged。
- 原错误：`TypeError: Failed to fetch`，发生于第一个script fetch，尚未定义/调用录制函数，不消费录制预算。精确CORS/Private Network等机制未隔离。
- 处理：复用已存执行JS由native eval stdin安装；随后同原完整路线仅启动一次。原transport失败留档，不重试录制、不声称服务限制修复。
- 证据：原工具错误，私有摘要`本地transport未开始_失败证据.json` SHA `02eef33cdd2264870359271f9ec0e562248722099166972e2d7f9beccd630657`；确切已执行表达式与存档脚本逐字回核。
- 状态历史：open→triaged；无需本轮解决内部网络机制。
- 下一步：原始媒体通过blob下载保存，遥测独立读取；不据服务器进程存在判上传成功。

- 2026-10-13追加定位 / 修复 / 回归：本地实播同报`ERR_EMPTY_RESPONSE`；原服务stderr实际`TypeError: HTTPMessage object is not callable`，自建handler方法`headers`被BaseHTTPRequestHandler同名字段遮蔽。不是已证浏览器网络隔离。改名`respond`后新的task-owned服务/play与/media真实HTTP200，媒体SHA与原件一致；修复回归SHA `e1994403eb55bbd54878e26ff0f352f11e0d8f66516fd67ecc75a2dd3cd626e4`。状态triaged→fixing→fixed→verified，仅HTTP服务，不称跨源上传验证；初次错误日志/预检均保留。

## ISSUE-20261013-020

**现象：已录原blob第一次native下载超时，code分块提取又撞IPC返回上限。**

- 首次观察 / 登记：2026-10-13，CASE-20261013-002，medium/environment。
- 预期 / 实际：下载已录媒体，不新增采集。原锚点附在长页面末端，native下载30s超时、磁盘文件不存在；code尝试4MiB数据URL首块超过IPC结果上限，0 emit，无完整媒体落盘。
- 当前处理：原blob保留，链接显示成可见控件，再一次native下载并延长传输等待；只有导出，不重录、不重开预检预算。
- 实際回核：62441347字节，与浏览器原blob SHA `bce9c662a51959453f44fa212f6a5b392e119768f191ab71a87cd9b2e840efba`一致；3083原VFR帧/末PTS103.073，全解码0。
- 证据：原工具失败及成功；私有追加异常SHA `139cd96cd0ae5849bac56431947d5e97c46733d3f934c8ade3f74169076b7288`，媒体与实际时间轴报告留完整命令。
- 状态历史：open→triaged→fixed→verified，仅本媒体成功导出，工具IPC/网络限制没有被修改。

## 新条目模板

复制下列块，替换占位ID，并在总表补对应行；模板不是已登记bug。

```markdown
## ISSUE-YYYYMMDD-NNN

**现象：一句具体异常，不写预设解决方案。**

- 首次观察 / 本次登记：
- 状态 / 严重度 / 类型：open / medium / behavior
- 影响版本与范围：
- 预期行为：
- 最小复现/观察：
- 证据：相对源码/测试名、脱敏归档标识、事件ID或SHA
- 根因：已确认内容；未确认写“未知”，不猜定
- 当前处理 / 修复引用：
- 实际验证：执行日期/命令/输入/结果；未运行写未验证
- 状态历史：日期、旧→新状态、依据（只追加）
- 下一步 / 关闭条件：
```


## ISSUE-20261014-021

**现象：拍前脚本声明逐字字幕，但各段烧录字幕只列摘要；开场口播长度超过3.5秒规划。**

- 首次材料：2026-10-14会话导出末尾的v1脚本；本次发现/登记：2026-10-14。
- 状态 / 严重度 / 类型：fixed / medium / contract。
- 影响：CASE-20261013-002拍前包v1；结构门禁通过不代表口播时间或字幕覆盖正确。
- 证据：v1正文SHA `ebd06c425460efde4368bba32e21b27790b368993e0b33d939439d69645f04b6`；S01时间0.001–3.503秒，原口播含完整面积介绍；字幕摘要与口播不一致。
- 处理：私有独立v2保留路线与源图，缩短九段口播，字幕明确逐字覆盖同一口播。正文SHA `8ca2421c65acbe2ead326b8ce84594e48a9db868d9825c42565100d97edf9bcb`。
- 实际验证：按240汉字/分钟估计九段均在时间窗内，结构检查另存私有回执；配音未生成，实听/实帧字幕未验证，故不标运行verified。
- 状态历史：2026-10-14 open→triaged→fixed，限审核包文案一致性。
- 下一步：一次整包批准后验证实际TTS时长和逐字字幕。

## ISSUE-20261014-022

**现象：拍前包v1漏掉已要求的室内引流，且声称音乐字节/许可绑定但record未列音乐资产。**

- 本次发现/登记：2026-10-14；状态 / 严重度 / 类型：fixed / medium / contract。
- 观察：v1 scope.ending只含免责；assets缺实际BGM和许可证据，authorized_actions漏voiceover。
- 处理：新v2列“想了解这套房的更多细节，欢迎留言”及免责；明确配音动作；实际音乐文件、来源核验、既有官方许可快照逐个SHA绑定。CTA作为本次待审核内容，不声称已批准。
- 证据：v2正文SHA同021，BUNDLE_SHA256 `2c5f7995f6a6c5355e2b93d882188998bce95fcfb5787e41008de4e6ebdbc423`；真实房源/音频路径仅保留私有审核包。
- 实际验证：原v1全部绑定文件SHA重新匹配，补绑文件实际存在并散列。没有新音乐采购、配音、正式录制或发布。
- 状态历史：2026-10-14 open→triaged→fixed；仅拍前合同补齐，尚待本次整包审核及成片检查。

## ISSUE-20261014-023

**现象：用户要求参考图的整体方案板，实际交付却是原始截图加分段长文。**

- 首次观察 / 登记：2026-10-14用户退回v2；high / contract。
- 预期：顶部整片说明，中部横向章节图文卡，下部户型/变化/待审范围；图和文字同卡，可横向比较节奏。
- 根因：模板只要求标题下嵌源PNG；生成器把原截图当章节卡；文件/SHA结构检查没有版式证据，Agent未做参考结构对照。
- 修复：3.3.0入口、版式合同、模板、v3记录、结构门禁、抽象示例及HTML生成器同步；旧v2仅历史兼容，不追认用户退回的包。
- 实际验证：70项CLI通过，其中6项新版式正负场景；官方strict 1项/0错误/0警告；实际资源加载目标唯一、diagnostics为空。新v3在Chrome加载十张真实图片、S01–S09顺序正确；一次路线文字溢出修正后横向溢出集合为空；完整PNG已独立目视。
- 成图SHA：`6b26bd192c12591b249d785f6813b68d06464689317b66cf936ada2a41eb45df`；原始图片/房源信息与完整回读证据仅留私有审核包。
- 状态历史：open→triaged→fixed→verified，验证限规则拒绝与当前排版输出；不代表用户已接受格式、全模型自动触发稳定或视频完成。
- 下一步：展示新方案板；一次整包批准后才制作视频，不重开探索或自动采集。

## ISSUE-20261014-024

**现象：整体方案板修复后动作区仍只有文字，首镜仍是室内源图而非户型/标题合成预览。**

- 发现/登记：2026-10-14，用户退回v3；high / contract。
- 根因：真实源参考、动作示意和成片布局预览未分用途；生成器只输出action段落，卡片标题按coverage索引生成；回读只验整体结构。
- 修复：Skill 3.4.0、版式/模板及生成器明确visual.title/layout/motion；五类SVG动作图示＋短标签；首镜实际合成背景/户型/两行标题并标为设计预览。v3回读新增两个独立图像语义检查。
- 实际验证：72项门禁CLI、5项生成器测试通过；官方strict 0错误/0警告。隔离合成素材浏览器渲染：三动作图示、首镜四个图层元素均可见、图片全部加载、无横向溢出；完整PNG目视并保留为公开07示例。
- 状态历史：open→triaged→fixed→verified；只验证技能和合成渲染，不证明当前房源首镜已修、用户接受或视频完成。
- 范围：本轮不改当前房源审核包，不操作房源、不生成配音或视频；后续制作须用当前房源实际来源按新规范另版提交。

### ISSUE-20261014-024 · 3.5.0整合追记

2026-10-14：同类格式补丁统一到设计系统v1.0；清除生成器写死成像标签/字幕模式/变更描述，显式首尾角色和组合动作由同份record驱动。规则/同源CLI/合成界面已验证，真实房源未制作；见CASE-20261014-003。历史状态保留，用户接受不追认。
