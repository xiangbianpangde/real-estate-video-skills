# Wiki 索引

本目录是房产介绍视频制作的知识层：每条模式记录一次真实踩坑或有效做法，并注明它约束了 `skills/` 里的哪一段行为。Skill 是执行层，Wiki 是判断层。

架构参考 WikiSkill（*Compiling Agent Experience into Persistent Knowledge for Skill Evolution*）：原始执行记录不可变地留在 `raw/`，经验被编译成 `wiki/patterns/` 下的独立条目，再由 `skills/` 引用。

## 当前入口与历史归档

- [项目当前交接](../HANDOFF.md)：当前版本、制作状态、证据与唯一下一步。
- [Skill当前规范](../skills/vr-production-gates/SKILL.md)：4.10.0执行入口；模式与专项参考的关系见[当前影响映射](skill-impact.md#当前映射)。
- [历史归档](archive/handoffs/index.md)：旧交接与历史路径的入口；仅用于追溯，不覆盖当前规范或项目状态。

## 本轮使用复盘

2026-10-16补充：固定资料适配、错选户型、过密内容及双HTML问题见[ISSUE042](issues.md#issue-20261016-042)；4.5.0修订不代表新房源路线动态已通过。

[CASE-20261016-004 · Skill实作、纠错与目录定版](cases/CASE-20261016-004-skill-production-finalization.md)：需求边界、问题/原因/处理、v14到v15速度实测、配音字幕、指定BGM、完整素材库、目录及验证证据。历史制作长日志继续保留，最新摘要以该案例及对应原始回执定位。

## 模式条目

| ID | 标题 | 影响的 Skill 段落 | 状态 |
|---|---|---|---|
| [P001](patterns/P001-shot-ok-assembly-bad.md) | 单镜合格不等于成片合格 | 图文整包与完整交付 | active |
| [P002](patterns/P002-subtitle-glyph-fallback.md) | 烧录字体缺字形导致整片不可用 | 字幕与字形检查 | active |
| [P003](patterns/P003-music-bed-length-and-level.md) | 音乐候选短于成片，循环与响度策略 | 声音制作与来源/时长管理 | active |
| [P004](patterns/P004-acceptance-does-not-unlock-next-stage.md) | 上一阶段接受不自动解锁下一阶段 | 触发边界 | active |
| [P005](patterns/P005-narration-timeline-fit.md) | 配音时长与镜头时间轴错配 | 声音制作与来源/时长管理 | active |
| [P006](patterns/P006-render-filter-capability-gap.md) | 渲染器缺少字幕滤镜时的替代路径 | 当前工具能力与技术示范 | active |
| [P007](patterns/P007-reference-subtitle-style.md) | 区分卖点字幕样式与完整口播覆盖 | 脚本包、后期时间轴与字幕 QC | active |
| [P008](patterns/P008-vertical-fov-two-axis-focal-split.md) | 竖屏六面重投影的 FOV 约定：两轴必须分离焦距 | 当前工具能力与技术示范 | active |
| [P009](patterns/P009-retiming-keeps-narration-and-script-aligned.md) | 画面提速后同步重排声音与完整剧本 | 路线运动、声音后期及同版图文交付 | active |

## 参考案例

| ID | 实际流程 | 记录范围 |
|---|---|---|
| [CASE-20261013-001](cases/CASE-20261013-001-current-skill-production.md) | 3.1.0新房源选材/预检/问题/停止快照，追加3.2.0用户视觉范围更正 | 原历史保留，旧零伪影门槛不覆盖用户范围；完整视频未做，非出片成功案例 |
| [CASE-20261013-002](cases/CASE-20261014-002-review-package.md) | 3.2.0起的历史图文、制作及历次纠错长日志 | 各节保留当时状态；后续v15制作与当前摘要见CASE004，不再把页首拍前状态当作现状 |
| [CASE-20261014-003](cases/CASE-20261014-003-design-system.md) | 设计系统v1.0四项交付、同源生成、正反验证及项目整理 | 已实现/测试；合成界面验证，不是房源生产或用户验收 |
| [CASE-20261015-003](cases/CASE-20261015-003-constraint-audit.md) | 62类约束逐项量化、清理规则与执行检查 | 评分是工程判断；不执行视频 |
| [CASE-20261016-004](cases/CASE-20261016-004-skill-production-finalization.md) | 制作至v15、4.3.0资料推送及4.4.0目录整理 | 已推送的48087e7与尚未提交的本轮整理分开；技术检查、用户回复和人工实听分别记录 |

## 配套

- [Bug与问题台账](issues.md) — 具体异常、复现/观察证据、处理状态及实际回归；新条目按页内模板登记
- [演化日志](logs.md) — 每次模式增删改与 Skill 版本变化
- [Skill 影响表](skill-impact.md) — 模式到 Skill 段落的映射与回归检查
- [原始记录](../raw/README.md) — 不可变执行留痕的写法

## 使用约定

1. 只有真实发生过的经验才写入 `patterns/`，不写设想。
2. 每个模式必须指向至少一个 Skill 段落或明确写"暂不影响 Skill"。
3. 模式被 Skill 吸收后不再删除；只在 `logs.md` 记录状态迁移。
4. 写入新模式时同步更新本索引、`skill-impact.md` 和 `CHANGELOG.md`。
5. 具体bug先登记到`issues.md`，同因复发更新原ID；仅登记不自动升级模式或更改Skill生产规则。实际修Skill仍按原验证/版本流程。
