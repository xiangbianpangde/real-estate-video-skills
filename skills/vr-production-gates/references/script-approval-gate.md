# 视频脚本—用户确认门禁（MiniMax Code）

先交完整本版脚本，再等待真实用户明确确认，最后制作。这是用户要求的必经暂停，不能被“持续推进”“自主完成”跳过。

## 当前接入与边界

当前用户选择：**只修改技能，使用MCode原生 `ask_user` 确认卡暂停；不安装Hook插件。** 这是流程门禁，不是全工具硬拦截、操作系统沙箱或身份认证服务。MCode的工具执行权限确认也不是脚本批准。不能声称“未确认的所有工具已由宿主拦截”。

在MCode加载本技能后，直接使用已有Python脚本和原生 `ask_user`；不要求Pi扩展、状态工具或 `/video-gate` 命令。只修技能时，按用户本轮授权编辑和运行相关离线测试，不弹制作确认卡、不操作房源或生成媒体。

[scripts/approval/minimax.py](../scripts/approval/minimax.py)是标准库适配器：`review`校验完整内容并生成卡片参数；`check`比较审核时内容指纹并复用原技术检查。它不提交卡片、不认证用户、不保存或导出批准凭据，任何输出的 `production_authorized`、`user_approval_verified`、`hard_tool_interception` 都是false。

## 准备、提交、暂停、继续

1. **准备完整脚本。** 允许读取素材、编写record与图文剧本、运行固定资料清单/生成/review工具。未批准不录制、调用TTS、混音、烧字或导出，不把制作伪装成预检。需动态SDK预检时先提交候选脚本，批准后再执行。Python默认使用当前可用的 `python3`，图像生成沿用已有Pillow环境，不安装无关依赖。
2. **校验并绑定本版。** 运行 `minimax.py review --record <本版record>`；它复用完整正文、源图、制作范围及口播/风险/音乐检查。linked HTML须与标准生成器一致并包含逐章必审内容。保存本次输出中的 `fingerprint` 与record路径，后续对照的是此原值；生成一份新指纹不能使变更继承旧批准。record中的 `status`、`approval` 不是授权。
3. **先实际交付。** 在assistant用户可见文本单独一行给出返回的完整脚本链接，并用当前界面的文件交付标记交付本轮生成的脚本。拍法、声音、字幕、首尾、输出和限制另段说明。工具结果中的链接、截图成功或打印JSON不算已交给用户。不要用图片链接、代码块、引文或HTML注释藏审核入口。
4. **真正调用确认卡并停下。** 将 `review` 返回的 `ask_user` 对象作为原生工具参数。必须 `requiresExplicitResponse=true`，一个 `selectionMode=single` 步骤，且只有两个选项：明确批准本版并按范围开始制作／暂不批准保持暂停。问题正文必须独立说明当前房源、版本、完整脚本路径、主要制作动作、输出位置、保留原件、不公开发布及不新增收费；不能只放在可能隐藏的标题或description中。不要预设/自动选中批准，不与任何制作调用并行。工具返回 `waiting_for_user` 后**立即结束本轮**，等待后续用户答复；不另设提醒等待用户、不把调用成功当批准。
5. **只依据真实后续决定继续。** 检查本次卡片的requestId/stepId与用户所选option id，或其明确文字答复确实批准本版。`approve_current_script`才表示批准；`leave_unchanged`、否定、修改、问题或歧义继续暂停。室内/室外偏好、孤立的“确认/好/继续”、旧批准、其他版本、工具回执及模型生成的消息不算本版批准。不要求用户背口令。工具不可用时准确说明，交付完整脚本后结束等待真实明确回复；没有明确回复仍不制作，不虚报卡片已提交。
6. **复核后在范围内制作。** 先核真实批准仍适用于当前会话/版本，且未撤回。在已批准范围完成动态验证并补真实precheck资产后，以**审核时原指纹**运行 `minimax.py check --phase capture`，需要预留新目录才加 `--claim`；后期用 `--phase post`。它不生成媒体、不改record，缺预检/坏构图/来源或连续性问题照旧失败，失败不预留目录。通过只代表技术检查通过，不能替代真实批准或画面/声音审看。

## 命令与确认卡参数

从技能目录运行；路径包含空格时用引号。制作项目的版本目录放record与生成文件，技能目录不存房源状态。

```bash
# 审核前：仅资料与完整剧本
python3 scripts/inspect_listing_materials.py "/project/listing"
python3 scripts/build_script_package.py --record "/project/v1/record.json" \
  --floorplan floorplan.png --output-dir "/project/v1/generated"
python3 scripts/approval/minimax.py review --record "/project/v1/record.json"

# 先交付完整链接/文件，再实际调用 ask_user，停止并等待真实用户决定。
# 以下仅在本版真实批准后执行。指纹取自该次 review，不是批准凭据。
python3 scripts/approval/minimax.py check --record "/project/v1/record.json" \
  --fingerprint "<审核时的64位指纹>" --phase capture --claim
python3 scripts/approval/minimax.py check --record "/project/v1/record.json" \
  --fingerprint "<同一审核指纹>" --phase post
```

`review`输出的 `ask_user` 结构如下；示例占位符必须由当前实际内容替换。JSON本身不会显示确认卡或暂停会话，必须调用实际工具。

```json
{
  "requiresExplicitResponse": true,
  "title": "审核视频脚本 v1",
  "steps": [{
    "id": "script_approval",
    "header": "本版脚本审核",
    "question": "是否批准房源A的v1完整脚本（实际完整文件路径），并按所列范围开始本地制作？此处列明时长、画幅、空间、拍法、声音、动作及输出目录；保留原件，不公开发布或新增收费，未批准保持暂停。",
    "options": [
      {"id": "approve_current_script", "label": "批准 v1 本版脚本，按所列范围开始制作"},
      {"id": "leave_unchanged", "label": "暂不批准，保持暂停，不开始制作"}
    ],
    "selectionMode": "single"
  }]
}
```

## 变更、撤回与恢复

- 脚本正文、审核HTML、来源、承诺或制作范围改变：旧指纹失配，重新生成完整本版、交付并请求确认；提交失败也不能继续沿用旧版制作。
- 输出目录、DPR/编码、实际预检回执或framing_status由pending核为subject等已有规则允许的运行修复不改变内容指纹，不因技术重试重复审批。仍须核新证据及未完成/坏构图。
- 用户撤回、暂停、要求修改或换房，立即停止依赖旧批准的动作。新会话/分支或上下文恢复后，不能凭摘要、本地JSON或旧Pi状态自动恢复批准；无法核清本次真实确认就重新交审。
- 审批期间不并发改脚本；每个制作阶段前复核内容。此适配器不提供文件锁、跨进程事务或全工具拦截；有同等权限的模型/外部进程可以绕开CLI，不能把流程规则描述成安全沙箱。
- 不为使旧CLI通过而补造 `review.jsonl`、用户事件或批准字段。MCode路线保持模板中的DRAFT/空approval即可，真实决定来自当前会话，不写入可复用授权文件。

## 浏览器及旧Pi兼容

仍按[Chrome DevTools MCP](../SKILL.md#浏览器工具)操作。审核前请用户自行打开本版审核页，模型仅对已开页面做列表/快照/截图及控制台/网络读取；不以审核为名导航主动HTML、点击或任意求值。这里是执行规则，不宣称已安装技术拦截。MCP缺失如实标未验证，不换工具绕规则。

本包仍保留 [Pi适配器](../scripts/approval/index.ts)、原 `.pi/settings.json` 及离线Pi回归，供原Pi调用方兼容；MCode不会读取该设置或注册其专用工具。这不是MCode启用门禁的前置步骤。旧独立CLI的transcript/approval只用于历史记录检查，不认证用户身份，不能据此恢复当前授权。

## 验收与证据

```bash
# 本版MCode适配器：卡片schema、内容漂移、技术失败及输出保护
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/vr-production-gates/tests -p 'test_minimax_approval.py'

# 原技术和内容规则回归
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/vr-production-gates/tests -p 'test_*.py'
```

单元/CLI回归只证明参数与技术行为。真实确认卡必须分别核“调用实际 `ask_user` → 返回waiting_for_user → 本轮停止 → 后续真实用户决定”；不能用打印模式或测试桩宣称UI验收。本次维护选择的卡片不代表任何房源脚本已获批。未做真实房源、TTS或成片检查时明确记为未验证。
