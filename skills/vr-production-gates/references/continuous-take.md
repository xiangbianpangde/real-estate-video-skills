# 连续镜头技术

跨房间规划先读[一镜到底采集风险](continuous-capture-risk.md)：登记house-002已发生的SDK重影/门框形变及不同采集方法限制，按基础能力→候选路线→高风险连接→完整路线验证推进。

## 表达与来源

拍法由本次目标决定。一镜到底使用单一连续源，可有叙事章节与局部变速；同点回转不提供跨点视差，多个take硬拼不能称连续。用户当前不允许硬切时保留完整源区间，详见[路线与后期](short-route-motion.md)。

| 方法 | 可用表达 |
|---|---|
| panorama_same_point / panorama_reprojection | 同一采集点真实全景回转 |
| panorama_sdk_navigation / panorama_navigation | 当前房源官方跨点导航，实际检查过渡 |
| model_mesh / model_render | 当前已采集模型与贴图中的相机运动 |
| physical_camera / physical_capture | 真实实拍，按项目实拍范围执行 |

当前源/方法的相关动态证据才说明其效果。复用有效媒体和已检查区间；换方法后的不同限制如实说明。一般实现优化在已授权范围内自主进行，实质改变交付表达或来源权利时再对齐。

## SDK与渲染检查

使用实际主相机，记录必要的视口/DPR、FOV轴、姿态、点位和源身份。先等加载与实际姿态稳定；ready不保证动画精确归位。容差依据最终成像误差和浮点精度，不从个案复制极小数值。

临时改state、helper、同步函数或view offset时，保存并在finally恢复；属性原先继承时恢复继承关系。停止录制轨道并回读实际状态。只看辅助相机矩阵、端点或回调不能证明沿程正确。

竖屏射线的水平/垂直尺度分离：kx=tan(h_fov/2)，ky=kx*H/W。角度、分辨率和帧率以本项目为准，历史55°/720×1280/30fps是技术样例。

## 预检记录

检查器兼容vr-render-precheck/v1：当前source_namespace/capture_medium/validation_scope/render_method/render_config/continuity_class/route/coverage及source_sha256，与本次输入对应。scope.render_validation绑定报告；相关媒体/审看资产进入文件索引。

报告包含连续媒体media与实际审看review，记录complete_interval_reviewed及checks.control/visual/playback。需要控制定位时附telemetry，实际改浏览器状态时记录恢复，可合并在同一文件；不强制拆成四个独立文件。存在明确恢复失败不能报告通过。

技术与观看分别记录PASS/PENDING/FAIL；按用户要求可PASS_WITH_LIMITATIONS并披露具体区间。带限制通过不强制额外建立参考批准文件；已有用户参考时复用，不另请示同类现象。最终用户接受独立于机器检查。

技术失败保留证据并修复重试。目录预留用于防覆盖/并发冲突，不代表失败永久耗尽许可；不改旧claim，重试使用新路径。只有用户明确限次或不重拍时才按其边界处理。

## 实拍与模型的范围

model_only只评价模型内的轨迹、构图、遮挡与纹理，不认证真人路径、公制或现场安全。physical_verified仅在项目确需现实测量主张时使用实际标准与证据，本技能不设通用眼高或净空值。

实现参考：[可运行技术示范：SDK预加载、录制及恢复](examples/technical-examples.md)。输入、输出与本次未验证项见示范对应章节；不增加审批或次数规则。
