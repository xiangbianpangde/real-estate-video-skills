# 房产介绍视频Skills

本仓库分开维护可复用Skill、项目交接、Wiki和实际素材。当前Skill版本以[SKILL.md](skills/vr-production-gates/SKILL.md)为准；当前项目只从根目录[HANDOFF.md](HANDOFF.md)继续。

## 从哪里开始

| 任务 | 唯一入口 |
|---|---|
| 当前项目状态与下一步 | [HANDOFF.md](HANDOFF.md) |
| 通用制作行为 | [Skill](skills/vr-production-gates/SKILL.md) |
| 本轮使用复盘 | [Wiki索引](wiki/index.md)、[CASE004](wiki/cases/CASE-20261016-004-skill-production-finalization.md) |
| 归档与历史交接 | [归档索引](wiki/archive/handoffs/index.md) |
| 图文设计 | [设计系统规范](skills/vr-production-gates/references/design-system.md) |
| 填写剧本 | [记录模板](skills/vr-production-gates/assets/templates/record.json)、[填写说明](skills/vr-production-gates/references/illustrated-script-template.md) |
| SDK、变速、声音与BGM整理 | [技术示范](skills/vr-production-gates/references/examples/technical-examples.md) |
| 完整BGM、视频及剧本 | [materials素材总入口](materials/index.html) |
| 问题与证据 | [Bug台账](wiki/issues.md)、[影响映射](wiki/skill-impact.md)、[raw说明](raw/README.md) |

本机兼容工作台为local/index.html，其他机器直接打开materials/index.html。BGM与全部本轮资料已按用户明确要求提交；local会话/缓存/验证备份仍忽略。当前正文、归档、证据、媒体不通过互相复制来维护多份状态。

## 目录职责

```text
HANDOFF.md                         唯一当前项目交接
README.md                          仓库导航
skills/vr-production-gates/
  SKILL.md                         通用技能入口
  CHANGELOG.md                     包版本记录（现有Pi校验要求）
  references/                      工作规范、设计说明与技术示例
    design-system.md               设计规范说明
  scripts/                         可复用工具与组件实现
  assets/
    templates/record.json          可复制记录模板
    design-system/                 tokens、CSS、schema、合成示例
  tests/                           既有回归；保留位置以减少无关迁移
wiki/
  index.md                         知识导航
  cases/                           实际使用复盘
  patterns/                        已有证据的可复用经验
  archive/handoffs/                 历史交接及归档索引
  issues.md                        问题与追加验证
raw/                               不可变原始回执
materials/                         实际素材与交付，不属通用Skill包
local/                             本机兼容入口、会话、缓存与验证证据
```

设计说明属于references，渲染器使用的样式与结构属于assets；不另建design-system包根。项目PURPOSE的通用目的已合入SKILL，项目状态只在根交接导航。历史移出技能发现范围，原件与批准快照保持原位置及字节。

## 生成与验证

```bash
python3 skills/vr-production-gates/scripts/build_script_package.py \
  --record /private/version/record.json --floorplan floorplan.png \
  --output-dir /private/version/generated

python3 -m unittest discover -s skills/vr-production-gates/tests -p 'test_*.py'
python3 skills/vr-production-gates/tests/run.py
python3 tools/verify_design_system.py --evidence-out /path/to/new-evidence.json
python3 tools/check_project.py
```

音频/字幕检查使用含Pillow的Python及FFmpeg/ffprobe；Skill加载另用现有Pi严格校验与实际资源加载。结构检查不替代画面实看/声音试听。Pi独立加载可用 `pi --skill /path/to/skills/vr-production-gates`，不维护同名副本。包根CHANGELOG和tests是现有工具约定，不是项目状态入口。

历史归档沿用Wiki归档索引，阶段被替代时标明原因、日期、原位置、内容身份和当前入口；不定期复制快照，不从历史配额恢复当前约束。
