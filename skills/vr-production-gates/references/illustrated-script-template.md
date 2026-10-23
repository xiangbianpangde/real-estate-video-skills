# 图文剧本填写入口

当前模板采用标准record.json，不再手工维护一份重复的Markdown台本。

1. 复制[生产记录模板](../assets/templates/record.json)到私有项目新版本；按事实及来源填写，保留旧版本。
2. 定稿前提供“室外（默认）／室内”展示重点，已有选择直接沿用；填写scope.showcase.primary_content/selection_source。按[三空间与展示规则](short-route-motion.md#展示选择与三空间范围)只展示客厅→阳台→主卧，每章标space_ids及content_mode，转场单列；所选主体展示时间占优。模板不是可直接拍摄的剧本，空缺须用当前素材填写。
3. 按[设计系统](design-system.md)填时间/动作/完整口播/风险与visual，首尾展示布局预览；按当前转场倍率核新时窗。用build_script_package.py从同一record生成HTML、正文及含展示选择的回执；源PNG在assets逐一绑定，真实房源不能用合成示例。
4. 按[浏览器工具要求](../SKILL.md#浏览器工具)使用Chrome DevTools MCP实际渲染并截图导出overview.png，核图像用途、首尾/动作/口播对应、文字边界及控制台错误；不可用时标明本步未验证。
5. 按[提交协议](illustrated-script.md)填写新版本的plan/图片/图源/回读摘要，实际展示后取得一次整包批准。

[可运行示例](../assets/design-system/examples/valid.json)仅演示结构，无房源事实、生产许可或用户接受。原始图片、冻结合同、已审记录和正式母版均不覆盖。
