# 房产介绍视频 Skills

面向房产介绍视频（VR / 全景 / 数字人）制作的 Agent Skill 与知识库。

结构参考 WikiSkill（*Compiling Agent Experience into Persistent Knowledge for
Skill Evolution*, arXiv:2608.27454）：把执行经验从散落的优化历史里抽出来，
编译成可检索、可引用、能持续演化的知识条目，再由 Skill 引用执行。

## 三层结构

```
skills/   执行层：Agent 实际遵守的行为
  └── vr-production-gates/
      ├── SKILL.md            入口，模式与工作流
      ├── PURPOSE.md          为什么存在、对应哪些 wiki 模式
      ├── CHANGELOG.md
      ├── scripts/check_shooting_plan.py  图文/提交/SHA/一次采集检查
      ├── tests/run.py                  门禁正负与并发回归
      └── references/
          ├── visual-acceptance.md    用户认可参考、带限制通过与接受边界
          ├── trigger-design.md       触发机制设计与正负向样例
          ├── acceptance-matrix.md    证据门禁矩阵与拒绝条件
          ├── subtitle-style.md       参考片样式、口播覆盖模式与字幕 QC
          ├── overall-plan.md         设计冻结/完整制作批准分流
          ├── illustrated-script.md    真实源图文脚本及实际提交协议
          ├── illustrated-script-template.md
          ├── freeze-record-template.json
          └── examples/               图文笔记（示意图 + 判据）

wiki/     判断层：真实踩坑与有效做法的知识条目
  ├── index.md            模式索引
  ├── patterns/           P001–P008
  ├── cases/              实际制作流程参考（标明完成阶段与限制）
  ├── logs.md             演化日志
  ├── issues.md           Bug现象、证据、修复状态与回归结果
  └── skill-impact.md     模式 → Skill 段落映射与回归检查

raw/      留痕层：不可变的原始执行记录（只追加、已脱敏）
```

## 核心流程

**默认：一镜到底优先，脚本先审后执行**

先确认空间覆盖/顺序/时长；同点回转归 MOV-006，跨房间行进归 MOV-007。跨房间证据不足即阻塞，不用单点回转或拼接冒充。硬切只限明确批准的非连续例外，详见 `skills/vr-production-gates/references/continuous-take.md`。

当前行为版本 **3.2.0**：

1. 先读[用户视觉基准](skills/vr-production-gates/references/visual-acceptance.md)，再有限预检当前方法/源/路线。参考内过渡重影可带限制通过，不自设零伪影或额外容忍阈值；旧动态PASS/端点/回调不替当前证据。默认关键预检1、每问题局部对照最多2、全路线1，不为AI更高标准反复录制。
2. **实际呈现图文脚本**：整体PNG、真实源章节图卡、S-ID时间/动作/字幕黄标/BGM/风险，以及首镜户型图、室内尾镜和完整制作范围；纯文字表或只报路径不算提交。
3. 用户一次批准正文/PNG/输入/范围SHA绑定对象，`SCRIPT_APPROVED_ONCE`含一次正式采集与列明后期。入口调用检查器并原子消费capture claim。
4. AI自主完成连续母版（或获批非连续例外）、首尾、获批配音、素材库BGM、字幕/混音/导出/QC，不默认逐镜、等母版接受或逐层索权。
5. 用户按S-ID审完整成片；同母版范围内字幕/混音/编码纠错是独立后期版本，不再次拍摄。商业发布另行授权。

**逐镜节奏仅用户明确要求时启用**。事实/权利不清集中澄清并阻塞未决范围，不自动切逐镜。`model_only`检查模型轨迹/明显穿模/遮挡/纹理，不因缺现场米制眼高/净空阻塞、不宣称现实安全。

两种节奏保留：真实性、技术QC、完整浏览器实播/音轨实听、最终用户验收与发布分离。新规则不追认旧批准、不消除旧视频伪影。

## 公开仓库的内容边界

- 只放图文笔记与抽象示意图，不放视频、音频或真实房源画面。
- 房源标识一律脱敏为 `HOUSE-REDACTED-NNN`。
- 媒体留在私有项目内，本仓库只以 SHA 引用。

## 安装

把 `skills/vr-production-gates` 放入 Pi 的技能目录：

- 项目级：`<project>/.pi/skills/vr-production-gates`
- 用户级：`~/.pi/agent/skills/vr-production-gates`

或直接指定路径加载：

```bash
pi --skill /path/to/房产介绍视频skills/skills/vr-production-gates
```

## 校验

```bash
python3 ~/.pi/agent/skills/task/skill-authoring/scripts/validate.py \
  --strict --root-mode pi skills/vr-production-gates
```

[图文协议](skills/vr-production-gates/references/illustrated-script.md)/[预检合同](skills/vr-production-gates/references/continuous-take.md#拍前成像证据合同)沿用v2；3.2.0允许绑定用户参考/真实原话及当前比较、披露的`PASS_WITH_LIMITATIONS`，不是伪写无瑕疵或增加第二次缺陷审批。旧记录/claim保留，post_only仍仅后期。检查器核结构/SHA，不看片、认证作者/身份或拦截绕过；Agent不能代签最终用户接受。

**修复/验证本Skill只改canonical及必要配套并运行测试，不自动打开房源、导航或录制，也不以缺真实新模型阻塞规则修复。** 规则通过不等于现有片畸变已修复。

```bash
python3 skills/vr-production-gates/tests/run.py
python3 ~/.pi/agent/skills/task/wendang/scripts/check_embeds.py \
  skills/vr-production-gates/references/examples
```

## 重新生成示例图

```bash
python3 tools/make_example_figures.py
```

## Bug记录

具体异常登记在 [Bug与问题台账](wiki/issues.md)，包括影响版本、最小复现/观察、证据、处理和实际验证；同一问题复发时更新原ID并追加状态历史。`fixed`表示改动已落盘，`verified`表示约定范围实际回归通过，两者不等于原视频已修复或用户验收。

`wiki/logs.md`继续记录版本/经验演化，`wiki/patterns/`归纳稳定模式，不代替具体bug台账。台账带模板，当前手动维护，没有自动采集或外部issue同步；私有媒体/房源/凭证不入公开记录。

## 实际流程参考

[CASE-20261013-001](wiki/cases/CASE-20261013-001-current-skill-production.md)保留3.1.0选材/预检/问题/恢复快照。用户随后明确视觉基准，3.2.0不再用旧更严门槛替其接受范围；旧媒体可另评，不改raw或自动称通过。完整视频未生成，非出片成功案例；真实媒体留私有。

## 维护约定

1. 只有真实发生过的经验才写入 `wiki/patterns/`。
2. 新模式必须指向至少一个 Skill 段落，或明确写"暂不影响 Skill"。
3. 改动 Skill 后对照 `wiki/skill-impact.md` 做回归检查。
4. `raw/` 只追加、不修改、不放媒体。
5. 行为变更才递增 Skill 版本号，纯文档修正记 patch。
