# 当前项目交接导航

当前技能：3.5.0；设计系统：v1.0。版本真值见[技能入口](SKILL.md)，不在本页复制行为规则。

- 用户任务：交付设计规范、共享组件、标准剧本数据、正反示例，并在完成后整理项目。
- 已实现入口：[设计系统](design-system/SPEC.md)、[标准结构](design-system/schema.json)、[正反示例](design-system/examples/README.md)。
- 生成：一份record生成方案板与详细正文；旧build_storyboard命令兼容，共用实现。
- 验证：既有72门禁＋5生成器回归，5个真实CLI正反流程；浏览器正例图片/组合动作/首尾图层可见且无横向溢出，PNG已目视。
- 整理：README与本页只导航，旧版式页改指针；本地会话移入local/session-exports并逐个SHA核对；旧交接原文[完整保留](HANDOFF-history-through-3.4.0.md)。
- 生产状态：未拍摄、未批准新房源剧本，未发布。合成示例不作为房源证据。
- 未验证：新上下文模型自动触发稳定性、真实房源端到端制作、通用JSON Schema引擎执行。
- 收尾验证：链接/嵌图/strict/loader检查通过；仓库raw/R20261014-design-system-validation.json与wiki/cases/CASE-20261014-003-design-system.md可复核。等待用户验收设计系统；提交及推送状态以Git历史和远程为准。
- 回滚：本轮增量对照上次提交e05c4a4；文件移动按local/organization-receipt.json逆向恢复，不reset用户工作。
