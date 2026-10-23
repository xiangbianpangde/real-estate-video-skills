# 图文剧本填写入口

当前模板采用标准record.json，不再手工维护一份重复的Markdown台本。

1. 复制[生产记录模板](../assets/templates/record.json)到私有项目新版本；按事实及来源填写，保留旧版本。
2. 定稿前提供“室外（默认）／室内”展示重点，已有选择直接沿用；填写scope.showcase.primary_content/selection_source。按[三空间与展示规则](short-route-motion.md#展示选择与三空间范围)只展示客厅→阳台→主卧，每章标space_ids及content_mode，转场单列；所选主体展示时间占优。模板不是可直接拍摄的剧本，空缺须用当前素材填写。
3. 按[设计系统](design-system.md)填时间/动作/完整口播/风险与visual，首尾画出布局；按当前转场倍率核时窗。用video_script_prepare(build)调用现有生成器，源PNG在assets逐一绑定。草稿不列尚未产生的precheck资产或render_validation，不虚填动态PASS；真实房源不能用合成示例。
4. 请用户自行打开生成的审核HTML，再按[浏览器要求](../SKILL.md#浏览器工具)用Chrome DevTools MCP只读截图导出overview.png，核首尾/动作/口播、文字和控制台；模型未批准不导航。不可用时标为未验证，不伪填layout-review。生成正文已按overview资产相对路径嵌图，导出图后核引用。
5. 保留输入record在原目录：plan.path/SHA绑定生成的正文，presentation.document_path与storyboard_layout.source绑定同一生成HTML，其资产role=storyboard_source；review_route_layout.source同步HTML锚点。核overview与layout-review实际SHA、章ID及目视结果。生成器只输出HTML/正文/generation，不输出已批准record；各路径相对record、正文图片相对正文。内容不变的SHA/输出路径回填不重生成HTML；内容变化则新版本重新生成。
6. 用video_script_prepare(review)检查，再video_script_submit；在聊天交付返回的本版完整链接，结束本轮等待真实用户确认。确认后按[宿主协议](script-approval-gate.md)完成所需动态预检，追加真实precheck/precheck_report资产与scope.render_validation，再用video_production_check核capture/post。status/approval不由模型填写通过，维护也不授权生产。

[可运行示例](../assets/design-system/examples/valid.json)仅演示结构，无房源事实、生产许可或用户接受。原始图片、冻结合同、已审记录和正式母版均不覆盖。
