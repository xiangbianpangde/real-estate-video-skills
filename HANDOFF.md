# 当前项目交接

这是本仓库唯一当前交接。通用执行入口为[Skill](skills/vr-production-gates/SKILL.md)，知识入口为[Wiki](wiki/index.md)，旧交接见[归档](wiki/archive/handoffs/index.md)。本页导航当前状态，不复制制作规则。

## 当前状态与入口

- 本轮按用户确认的计划整理为4.4.0结构：项目HANDOFF移出Skill，历史交接归档；设计规范与设计资产分别放入references和assets，脚本/测试引用同步。目录与文档整理已完成：Pi严格0错误/警告，147项回归、72项门禁、SDK离线检查、5组设计CLI及独立Skill复制生成通过；140份素材及清单SHA不变。用户已授权提交推送，实际提交及远端状态以Git记录为准。
- 已推送基线为`48087e7368276b46e042907fa78ba6582e5001ca`，包含Wiki及141个实际素材文件。完整BGM实体位于materials/library/bgm，local/material-library及Downloads/BGM为兼容入口。
- 当前房源交付为[完整v15成片与剧本](materials/productions/house-002/production/speed-v15/成片与完整剧本_v15_推进加快.html)，25.333秒。用户回复“可以”后进入整理；不据此代签专名/字母B人工核听或其他未提供的接受。
- 素材包见[materials总入口](materials/index.html)：5首完整原曲、10份35秒片段及房源原件/配音/剧本/成片。35秒不是后续上限；DJ阿狸与DJ小辞版本区别、缺黑神话记录仍保留。

## 已知限制

源SDK跨点重影/门框变形、转向柜台和公开SDK示范ISSUE039仍独立保留；速度接受不等于形变消除。当前完整复盘见[CASE004](wiki/cases/CASE-20261016-004-skill-production-finalization.md)，问题与后续证据见[台账](wiki/issues.md)。

本轮只整理目录、文档和路径调用，不重拍、不生成声音、不移动或改写音视频、原始回执或批准快照。其他全局Office/Morph Skill重名不在本仓库修复范围。

## 本轮证据及后续

- 迁移前工作区干净，回滚基线为48087e7；本地迁移前文本位于local/validation/structure-4.4.0/before。失败时按迁移清单原路恢复，只恢复本次改动，不reset或清除无关工作。
- 本轮迁移与最终检查写入raw/R20261016-skill44-structure.json；历史raw不修改。
- 结构检查的6组正反场景通过，48份Markdown/16处图片引用无断链；目标Skill连续加载两次零诊断。浏览器回读受已有配置占用及file://URL策略限制，本轮未完成页面目视检查，未绕过策略。
- 本轮目录整理已交付，用户已明确要求提交推送；完成后按后续任务继续，不将该指令扩展为新制作或发布许可。
