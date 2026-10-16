# Skill影响与验证索引

本文按4.3.0实际入口整理模式与Skill的关系，只用于定位和追溯，不建立另一套门禁。行为以[Skill](../skills/vr-production-gates/SKILL.md)及其专项参考为准。旧段号/探索配额等历史映射可从提交`147a3ac`的本文件追溯；不作为当前约束。

## 当前映射

| 模式 | 当前落点 | 需要核对的行为与边界 |
|---|---|---|
| [P001](patterns/P001-shot-ok-assembly-bad.md) · 完整交付 | [图文提交](../skills/vr-production-gates/references/illustrated-script.md)、[设计系统](../skills/vr-production-gates/design-system/SPEC.md) | 当前完整方案板、独立路线板、正文、动作与首尾实际交付；单镜/结构通过不等于整片接受 |
| [P002](patterns/P002-subtitle-glyph-fallback.md) · 字形 | [字幕](../skills/vr-production-gates/references/subtitle-style.md) | 实际烧录字形可读，缺滤镜/字体时按当前环境处理 |
| [P003](patterns/P003-music-bed-length-and-level.md) · 音乐来源与时长 | [声音制作](../skills/vr-production-gates/references/audio-production.md)、[素材位置](../skills/vr-production-gates/assets/README.md) | 指定版本优先；完整曲源与快捷片段分别保留；新长度从原曲重裁，最终混音另核 |
| [P004](patterns/P004-acceptance-does-not-unlock-next-stage.md) · 授权/接受 | [Skill](../skills/vr-production-gates/SKILL.md)、[提交协议](../skills/vr-production-gates/references/illustrated-script.md) | 沿用实际已批准范围，技术检查、人审和发布分别记录；范围内纠错不逐层索权 |
| [P005](patterns/P005-narration-timeline-fit.md) · 声音落位 | [声音制作](../skills/vr-production-gates/references/audio-production.md) | 实际音频/词时码、完整句与尾音；强制对齐不能认证发音正确 |
| [P006](patterns/P006-render-filter-capability-gap.md) · 环境能力 | [技术示范](../skills/vr-production-gates/references/examples/technical-examples.md) | 核当前工具能力；替代实现实际产物检查，不把加载/模拟当成真实制作 |
| [P007](patterns/P007-reference-subtitle-style.md) · 字幕与首尾 | [字幕](../skills/vr-production-gates/references/subtitle-style.md)、[首尾](../skills/vr-production-gates/references/opening-ending-layout.md) | 完整口播覆盖与卖点模式分开；用户所需首尾布局实际可见 |
| [P008](patterns/P008-vertical-fov-two-axis-focal-split.md) · 成像/FOV | [连续技术](../skills/vr-production-gates/references/continuous-take.md) | 当前成像方法与配置核证；历史FOV/画质数值不是所有方法阈值 |
| [P009](patterns/P009-retiming-keeps-narration-and-script-aligned.md) · 变速与衍生物 | [路线与运动](../skills/vr-production-gates/references/short-route-motion.md)、[图文提交](../skills/vr-production-gates/references/illustrated-script.md) | 连续完整源映射；重新落位原声/词字幕/BGM/首尾，同步当前完整剧本 |

## 本轮实际使用、检查与限制

详见[CASE004](cases/CASE-20261016-004-skill-production-finalization.md)；下表只索引证据，不再次判定事实。

| 使用/修改范围 | 已有证据 | 实际验证边界 |
|---|---|---|
| 同版图文、正向回程、门口扫视 | [v14剧本](../raw/R20261015-v14-forward-exit-script.json)、[4.1.1批准记录](../raw/R20261015-skill411-approval.json) | 剧本/批准与后续动态分别记录 |
| 七句mcode、词时码与指定音乐 | [制作](../raw/R20261016-v14-production.json)、[指定音乐混音](../raw/R20261016-v14-final-mix.json) | 批量逐项核对/实际音轨/浏览器播放；专名听感不代签 |
| 单源推进提速及声音同步 | [v15](../raw/R20261016-v15-speed-revision.json) | 全源单调映射、25.333秒、技术/浏览器检查；源SDK形变未消除 |
| 完整原曲与开头片段 | [备料](../raw/R20261016-skill420-bgm-library.json)、[完整原曲](../raw/R20261016-bgm-full-originals.json) | 5首源SHA不变、10份衍生文件；版本差异/缺曲保留 |
| Skill4.3.0目录 | [迁移与验证](../raw/R20261016-release-layout.json) | 147项回归、72项门禁、SDK离线/5组设计CLI及目标加载；全局无关重名/新模型触发边界另记 |

## 已删除约束不得从Wiki回流

4.0已审计的具体取舍见[约束审计](cases/CASE-20261015-003-constraint-audit.md)。不再用“局部最多两组”“全路线只准一次”“初始化失败永久消费授权”阻断修复；仅用户明确限制次数时生效。一镜到底约束连续源时间线，不是执行次数。

新的尝试按实际问题、进展和用户预算判断。无需为Wiki归纳增加审批或把本片角度、片长、响度、倍率强加未来任务。旧claim实现、历史许可和合成fixture不等于当前画面合格。

公开SDK示范ISSUE039与源画面形变仍独立保留；文档整理不冒称已修复、模型触发已通过或人工已经试听。
