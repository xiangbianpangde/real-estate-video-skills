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
      └── references/
          ├── trigger-design.md       触发机制设计与正负向样例
          ├── acceptance-matrix.md    证据门禁矩阵与拒绝条件
          ├── subtitle-style.md       参考片样式、口播覆盖模式与字幕 QC
          ├── overall-plan.md         整体方案冻结细则
          ├── freeze-record-template.json
          └── examples/               图文笔记（示意图 + 判据）

wiki/     判断层：真实踩坑与有效做法的知识条目
  ├── index.md            模式索引
  ├── patterns/           P001–P007
  ├── logs.md             演化日志
  └── skill-impact.md     模式 → Skill 段落映射与回归检查

raw/      留痕层：不可变的原始执行记录（只追加、已脱敏）
```

## 核心流程

**默认：脚本先审，一体化执行**

1. AI 交完整脚本（分镜 + 逐句台本 + 字幕时间码 + 音乐方向 + CTA + 事实来源）。
2. 用户一次批准，状态 `SCRIPT_APPROVED_ONCE`。
3. AI 在合同范围内一次跑完：镜头 → 整编 → 配音 → 音乐 → 字幕 → 混音 → 编码 → QC。
4. 用户按脚本观看完整视频，接受或提出按段落映射的修改。

**备用：逐镜门禁**

事实不清、点位未核证、源面或位移风险、权利不明，或用户要求逐镜确认时启用。

两种模式都不跳过：技术 QC、浏览器验证、事实边界、最终用户验收。

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

## 重新生成示例图

```bash
python3 tools/make_example_figures.py
```

## 维护约定

1. 只有真实发生过的经验才写入 `wiki/patterns/`。
2. 新模式必须指向至少一个 Skill 段落，或明确写"暂不影响 Skill"。
3. 改动 Skill 后对照 `wiki/skill-impact.md` 做回归检查。
4. `raw/` 只追加、不修改、不放媒体。
5. 行为变更才递增 Skill 版本号，纯文档修正记 patch。
