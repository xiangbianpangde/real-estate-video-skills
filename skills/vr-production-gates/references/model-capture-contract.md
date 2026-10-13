# 模型内拍摄合同

适用于用户明确选择使用当前房源3D模型完成视频拍摄，且验收范围为 `model_only` 的任务。

## 必填字段

```yaml
capture_medium: model_render
render_method: model_mesh
render_config: <renderer/version, viewport/DPR, FOV axis/value and camera settings>
render_validation: {path: <current precheck report>, sha256: <SHA>}
validation_scope: model_only
source_namespace: <listing/work>
source_bindings: <all model and texture files as assets.role=source with path/SHA>
continuity_class: cross_room_travel | same_point_rotation
coverage: [客厅, 厨房, 阳台, 卧室A, 卧室B, 卧室C, 卫生间A, 卫生间B]
route: <连续相机轨迹>
model_checks: [trajectory_continuity, no_obvious_penetration, framing, occlusion, texture_integrity]
```

## 来源绑定

当前模型路径、Work身份、模型/贴图SHA保存在私有项目现行合同；公开Skill不保存房源资产或私有路径。执行记录统一把模型及全部贴图逐项列入`assets.role=source`，预检的`source_sha256`与该集合完全一致，不维护第二套必填model_sha256/texture_sha256字段。每次运行验证输入与合同一致，在线加载也必须核对资源身份。

## 通过含义

按[当前动态证据](continuous-take.md#成像方法与动态预检)及[用户视觉基准](visual-acceptance.md)审看；旧照片/原点清楚不证明Model动态可用。碎片/重影/错接先记观察，再按用户实际接受标准判断，不自动FAIL或自设零伪影。Model目标与Panorama参考明显不同时展示差异，依据不足待审，不自动等同也不逆向到精确机制才允许审稿。

`model_only`通过表示当前轨迹/覆盖与已批准模型摄影范围可核，画面按用户标准可用，实际遮挡/纹理现象如实披露；`PASS_WITH_LIMITATIONS`是有效结果，不称无瑕疵或最终用户已接受。它不认证现场安全、公制或真人行走。

## 有限探索与批准范围

先规划完整候选路线，再核关键连接与高风险段；一次关键点预检、每个台账问题最多两组局部单变量对照、一次全路线预检。无改善/定位源限制/预算耗尽即停止，局部修改不重跑全屋。缺面、UV/纹理拉伸、新视角伪影、真实遮挡与视口投影错误分别登记；证据不足时写机制未确定，不把所有扭曲统称已证实源缺面。

`model_only`不要求现实米制眼高/净空；按用户标准检查画面/空间表达。现象在已声明接受范围内就披露并用有效带限制分支，不再另索同类缺陷许可或要求修到无瑕疵。超范围/未决仍不采集，用户改变标准用原媒体另版比较，不伪写PASS/改历史。换Panorama属新方法，不称模型已修或原片post_only；源身份、真实覆盖和授权不随审美标准失效。

## 仍保留的生产门禁

真实源图文脚本须实际展示并绑定正文/图片/输入/范围SHA；一次 `SCRIPT_APPROVED_ONCE`可包含原 `APPROVED_ONCE`采集含义及列明后期，不再额外请求第二次批准。入口检查并消费一次capture claim，只一个正式采集take；技术QC、完整浏览器实播、输出SHA和最终用户接受保留。

首尾、配音、字幕、BGM和CTA已明确列入本次批准时自主执行；未列付费、新事实/CTA和商业发布仍不自动授权。后期纠错独立输出、原母版不覆盖，不算第二次拍摄。历史批准/旧take不追认为这一完整范围。
