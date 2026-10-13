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

先按 [成像方法与动态预检](continuous-take.md#成像方法与动态预检) 绑定当前方法及完整动态证据；同源全景原点清楚/旧回转接受不证明Model可用。Model在原采集点也可能出现畸变；发现碎片、重影、错接或拉伸先判FAIL并停，不以已记录缺陷冒充画质通过。报告/图片/沿程实际画面不是精确内部归因的替代品，也不要求用户未请求的几何/贴图/SDK逐块逆向。

`model_only` 通过表示：相机轨迹在当前模型坐标中连续，沿程没有明显穿墙/穿家具，画面构图可用，遮挡和纹理缺陷已记录，覆盖空间与顺序符合脚本。它不表示现场安全、现实尺度、真人行走或物理碰撞认证。

## 有限探索与批准范围

先规划完整候选路线，再核关键连接与高风险段；一次关键点预检、每个台账问题最多两组局部单变量对照、一次全路线预检。无改善/定位源限制/预算耗尽即停止，局部修改不重跑全屋。缺面、UV/纹理拉伸、新视角伪影、真实遮挡与视口投影错误分别登记；证据不足时写机制未确定，不把所有扭曲统称已证实源缺面。

`model_only`不要求现实1.5–1.6m眼高及0.5m米制净空，但仍检查模型中明显穿模和画面可用性。模型缺陷可以在拍前经明确同意登记为披露限制，不能写成无缺陷PASS，不能删除必要房间或修补不存在的房况；当前检查器仅放行四项PASS的预检，没有视觉FAIL例外自动执行分支。改为真实Panorama导航属于新成像方法/范围，不是模型缺陷已修复或原片post_only。

## 仍保留的生产门禁

真实源图文脚本须实际展示并绑定正文/图片/输入/范围SHA；一次 `SCRIPT_APPROVED_ONCE`可包含原 `APPROVED_ONCE`采集含义及列明后期，不再额外请求第二次批准。入口检查并消费一次capture claim，只一个正式采集take；技术QC、完整浏览器实播、输出SHA和最终用户接受保留。

首尾、配音、字幕、BGM和CTA已明确列入本次批准时自主执行；未列付费、新事实/CTA和商业发布仍不自动授权。后期纠错独立输出、原母版不覆盖，不算第二次拍摄。历史批准/旧take不追认为这一完整范围。
