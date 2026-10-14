# 图文剧本填写入口

当前模板采用标准record.json，不再手工维护一份重复的Markdown台本。

1. 复制[生产记录模板](freeze-record-template.json)到私有项目新版本；按事实及来源填写，保留旧版本。
2. 按[设计系统](../design-system/SPEC.md)填写每章时间/动作/完整口播/风险与visual；首尾必须展示对应布局预览。
3. 用build_script_package.py从同一record生成方案板HTML和详细正文；源PNG在assets逐一绑定。真实房源不能使用合成示例素材。
4. 浏览器实际渲染并导出overview.png，核图像用途、首尾/动作/口播对应及文字边界。
5. 按[提交协议](illustrated-script.md)填写新版本的plan/图片/图源/回读摘要，实际展示后取得一次整包批准。

[可运行示例](../design-system/examples/valid.json)仅演示结构，无房源事实、生产许可或用户接受。原始图片、冻结合同、已审记录和正式母版均不覆盖。
