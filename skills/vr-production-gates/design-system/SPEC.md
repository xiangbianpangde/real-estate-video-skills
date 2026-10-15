# 房产图文剧本设计系统 v1.1

同一份record生成可审阅的总板、独立完整户型路线板和详细正文；组件不授生产权限。审核入口见[提交协议](../references/illustrated-script.md)。

## 层次与样式

![总板示例：全部为合成测试素材](examples/positive/overview.png)

顶部说明房源/版本、观看顺序与时长；中部章节卡连接真实参考、动作图示、主体与文案；下部给户型、改动和限制。S-ID连接卡片、正文与成片意见。

颜色与间距复用[tokens](tokens.json)和[样式](styles.css)。深青标题、绿色动作、琥珀风险是默认样式，可按阅读宽度与当前目标调整。状态有文字，图片保比例；卡片数量/标题行数/高亮数量不设通用上限。首尾按本次要求实际合成预览。

## 图像与组件

| 组件 | 用途 |
|---|---|
| chapter_card | 时窗、标题、画面/动作、主体、口播与存在的风险同卡 |
| motion_component | static/pan/travel/orbit/fov图示，支持有序steps |
| preview | 源图参考，或室内背景叠标题/户型的首镜，或收束/CTA/声明尾镜 |
| risk_tag | info/limitation/pending，不能代签用户接受 |

源图只证明当前素材，动作图只表达计划，布局预览不是已录成片。当前用户要求首镜实际户型或尾镜引流时，预览中对应内容可见，下部原户型不能替代首镜浮层。无引流需求时CTA可空，无旁白/音乐/额外风险时允许空值。

## 数据与生成

[Schema](schema.json)描述vr-production-plan/v3与设计系统1.0/1.1结构；语义校验在scripts/storyboard/model.py。plan/scope存一次内容与范围，assets存来源/字节身份，segments存章节，visual存标题、图像角色与动作，board_content存实际变更，不维护重复台本。

渲染器当前输入为PNG、有限动作/版式类型和S编号等结构，这是工具格式，不是新审批要求。来源缺失/字节漂移、时间轴不合法、图文对象不一致会失败；字段齐全不证明画面好看。

```bash
python3 skills/vr-production-gates/scripts/build_script_package.py \
  --record /private/version/record.json --floorplan floorplan.png \
  --output-dir /private/version/generated
```

生成storyboard.html、route-board.html（有review_route时）、plan.md和generation.json。生成包使用新输出目录以保护旧文件，实际导出PNG后看图片/图示/文字是否可读。草案可编辑；已批准内容保留，范围内迭代不重复索权。

## 完整路线板与完成标准

设计系统1.1用review_route描述左户型＋箭头/S-ID，右每章标题/时码/动作/路径。chapters与segments逐项对应，同点多章保留全部标签；共享组件生成独立板并嵌入正文。只有总板缩图、P点顺序或旧版截图不满足本项目完整路线板要求。

scope.review_route_layout绑定板与图源；当前版本、时码、点位表及正文嵌图一致。图只用于剧本审核，不进入成片；真实动态仍另核。切镜仅在用户允许时以cuts标明，不画成行走。

交付核同版数据、两板/正文、动作图示、要求的首尾层次、来源图片加载与可读性。用户时长/禁拍空间用shot_constraints及空间分类表达，连续后期用editing_policy/speed_map；见[路线规范](../references/short-route-motion.md)。

[正反示例](examples/README.md)只验证结构。实际浏览器和成片检查、用户接受各自如实记录。
