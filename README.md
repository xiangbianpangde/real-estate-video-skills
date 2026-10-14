# 房产介绍视频 Skills

面向真实房产素材的图文剧本、一次完整制作和成片验收。当前技能版本以[SKILL.md](skills/vr-production-gates/SKILL.md)为准。

## 从哪里开始

| 需要做什么 | 唯一入口 |
|---|---|
| 继续当前项目 | [交接导航](skills/vr-production-gates/HANDOFF.md) |
| 执行制作流程 | [制作技能](skills/vr-production-gates/SKILL.md) |
| 设计图文剧本 | [设计系统 v1.1](skills/vr-production-gates/design-system/SPEC.md) |
| 看完整正反示例 | [设计系统示例](skills/vr-production-gates/design-system/examples/README.md) |
| 提交与绑定拍前审核 | [提交协议](skills/vr-production-gates/references/illustrated-script.md) |
| 查问题与复盘 | [Wiki导航](wiki/index.md)、[Bug台账](wiki/issues.md) |

## 结构与职责

```text
skills/vr-production-gates/
  SKILL.md                 执行入口
  design-system/           设计规范、tokens/CSS、标准结构、正反示例
  scripts/storyboard/       共享数据校验、组件和两种输出
  scripts/build_script_package.py  record -> 总板HTML + 独立路线板HTML + 正文
  scripts/check_shooting_plan.py   审核/来源/一次采集门禁
  references/              提交、成像、字幕和首尾的专项合同
  tests/                   现有门禁与生成器回归
wiki/                      脱敏问题、模式、案例与演化日志
raw/                       不可变脱敏原始记录
local/                     本地会话导出与整理回执；Git忽略
```

设计信息只维护在record.json；方案板和详细正文由同一输入生成。读者图片采用PNG，HTML保留为可放大图源。完整制作的默认流程、用户视觉标准及授权以技能和专项合同为准，本页只导航。

## 生成与验证

```bash
python3 skills/vr-production-gates/scripts/build_script_package.py \
  --record /private/version/record.json --floorplan floorplan.png \
  --output-dir /private/version/generated

python3 skills/vr-production-gates/tests/run.py
python3 skills/vr-production-gates/tests/test_storyboard.py
python3 tools/verify_design_system.py --evidence-out /path/to/evidence.json
python3 tools/check_project.py
```

生成命令不导出PNG、不授生产权限。需真实浏览器加载、导出PNG和目视，再按提交协议绑定来源与批准。通用JSON Schema引擎、新上下文模型触发和真实房源端到端制作的验证状态见交接记录。

Pi安装：沿用一个canonical目录，使用项目`.pi/skills`符号链接，或`pi --skill /path/to/skills/vr-production-gates`加载；不要维护同名副本。

## 内容与历史保护

公开仓库只放代码、规范、抽象图和脱敏证据；真实房源素材、身份与完整会话留私有。重组保留旧交接字节及本地会话SHA；当前入口只指向权威合同。历史记录不等于当前批准、用户接受或发布许可。
