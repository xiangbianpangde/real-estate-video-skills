# 房产介绍视频 Skills

制作真实房源图文剧本与视频。目录定版版本为4.3.0，当前行为及版本以[SKILL.md](skills/vr-production-gates/SKILL.md)为准。

## 工作入口

| 任务 | 入口 |
|---|---|
| 继续当前房源 | [交接导航](skills/vr-production-gates/HANDOFF.md) |
| 执行制作 | [制作技能](skills/vr-production-gates/SKILL.md) |
| 填写新剧本 | [生产记录模板](skills/vr-production-gates/assets/templates/record.json)、[填写说明](skills/vr-production-gates/references/illustrated-script-template.md) |
| 图文设计与组件 | [设计系统](skills/vr-production-gates/design-system/SPEC.md) |
| 素材库与文件分工 | [模板与素材位置](skills/vr-production-gates/assets/README.md) |
| 变速、SDK、音频与BGM整理 | [技术示范](skills/vr-production-gates/references/examples/technical-examples.md) |
| 图文正反示例 | [示例](skills/vr-production-gates/design-system/examples/README.md) |
| 问题与过程记录 | [Wiki](wiki/index.md)、[Bug台账](wiki/issues.md)、[约束审计](wiki/cases/CASE-20261015-003-constraint-audit.md) |

完整素材已按用户本轮明确要求纳入[materials素材包](materials/index.html)：BGM完整原曲与全部片段、当前房源剧本/成片/连续原件/配音对齐素材及参考片。克隆仓库后直接打开materials/index.html，不依赖原机器路径。素材位于Skill包之外，不改变独立安装包的职责。

本机 `local/index.html` 继续可用；local/material-library与旧Downloads/BGM只指向materials/library，current交付也指向已提交素材。local中的会话、验证日志和缓存仍忽略。该次上传来自用户明确授权，不把未来所有私人素材默认公开。

## 定版目录

```text
skills/vr-production-gates/
  SKILL.md                         行为入口
  PURPOSE.md                       用途与边界
  CHANGELOG.md                     版本演化
  HANDOFF*.md                      既有项目导航与历史，保留路径
  assets/
    README.md                      模板/素材目录职责
    templates/record.json          唯一生产记录模板
  design-system/                   SPEC、tokens/CSS、schema、图文正反例
  references/                      图文审核、运动、声音、字幕、首尾专项说明
    examples/                      技术过程示例与问题定位入口
  scripts/
    storyboard/                    同一record的数据校验、组件和生成
    technical_examples/            SDK、连续变速、音频字幕、BGM整理工具
    build_script_package.py        方案板HTML＋路线板HTML＋正文
    check_shooting_plan.py          来源/审核/输出保护
  tests/                           行为与真实媒体回归
wiki/                              问题、案例和演化日志
raw/                               不可变原始回执
materials/                         本轮用户授权提交的真实资料
  library/bgm/                     完整BGM、开头片段与清单
  productions/house-002/            剧本、连续原件、配音及后期版本
  references/                      用户提供的推进参考片
local/                             私有素材、制作入口、会话与验证证据
  material-library/                兼容链接至materials/library
  productions/                     当前成片/剧本入口，原媒体不搬动
  validation/                      验证证据与本轮迁移备份
  session-exports/                  既有会话导出
```

章节卡、动作图示、首尾组件和风险标签仍由设计系统与生成器维护；方案板、路线板及正文使用同一record。真实房源及音乐保持在独立materials包，不复制进通用Skill资产。目录定版不冻结素材时长、拍法参数或后续正常迭代。

## 生成与检查

```bash
python3 skills/vr-production-gates/scripts/build_script_package.py \
  --record /private/version/record.json --floorplan floorplan.png \
  --output-dir /private/version/generated

python3 -m unittest discover -s skills/vr-production-gates/tests -p 'test_*.py'
python3 skills/vr-production-gates/tests/run.py
python3 tools/verify_design_system.py --evidence-out /path/to/new-evidence.json
python3 tools/check_project.py
```

音频/字幕测试使用含Pillow的Python环境；FFmpeg/ffprobe需可用。生成不等于目视/实听或用户接受。实际检查、已知限制与批准对象见交接及原始回执。

Pi沿用唯一canonical目录，可用 `pi --skill /path/to/skills/vr-production-gates` 加载；不维护同名副本。当前交接和历史路径保留，便于追溯已有引用；原始回执不因目录定版重写。
