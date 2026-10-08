# Wiki 索引

本目录是房产介绍视频制作的知识层：每条模式记录一次真实踩坑或有效做法，并注明它约束了 `skills/` 里的哪一段行为。Skill 是执行层，Wiki 是判断层。

架构参考 WikiSkill（*Compiling Agent Experience into Persistent Knowledge for Skill Evolution*）：原始执行记录不可变地留在 `raw/`，经验被编译成 `wiki/patterns/` 下的独立条目，再由 `skills/` 引用。

## 模式条目

| ID | 标题 | 影响的 Skill 段落 | 状态 |
|---|---|---|---|
| [P001](patterns/P001-shot-ok-assembly-bad.md) | 单镜合格不等于成片合格 | 工作流第 0 步 · 脚本先审门 | active |
| [P002](patterns/P002-subtitle-glyph-fallback.md) | 烧录字体缺字形导致整片不可用 | 第 B 步 10 · 后期 QC | active |
| [P003](patterns/P003-music-bed-length-and-level.md) | 音乐候选短于成片，循环与响度策略 | 第 B 步 9 · 后期单 take | active |
| [P004](patterns/P004-acceptance-does-not-unlock-next-stage.md) | 上一阶段接受不自动解锁下一阶段 | 触发边界 | active |
| [P005](patterns/P005-narration-timeline-fit.md) | 配音时长与镜头时间轴错配 | 第 B 步 9 · 后期单 take | active |
| [P006](patterns/P006-render-filter-capability-gap.md) | 渲染器缺少字幕滤镜时的替代路径 | 第 B 步 4 · 先测后写 | active |
| [P007](patterns/P007-reference-subtitle-style.md) | 区分卖点字幕样式与完整口播覆盖 | 脚本包、后期时间轴与字幕 QC | active |

## 配套

- [演化日志](logs.md) — 每次模式增删改与 Skill 版本变化
- [Skill 影响表](skill-impact.md) — 模式到 Skill 段落的映射与回归检查
- [原始记录](../raw/README.md) — 不可变执行留痕的写法

## 使用约定

1. 只有真实发生过的经验才写入 `patterns/`，不写设想。
2. 每个模式必须指向至少一个 Skill 段落或明确写"暂不影响 Skill"。
3. 模式被 Skill 吸收后不再删除；只在 `logs.md` 记录状态迁移。
4. 写入新模式时同步更新本索引、`skill-impact.md` 和 `CHANGELOG.md`。
