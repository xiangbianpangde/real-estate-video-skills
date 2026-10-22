# 图文剧本与提交

## 完整可审内容

按[设计系统](design-system.md)用同一record生成单一中文HTML，内含总方案板、完整户型路线板和详细正文。真实源参考、动作图示、首尾排版预览分别标明；不能用旧截图加长文替代当前完整方案。

定稿前完成[室内/室外展示选择](short-route-motion.md#展示选择与三空间范围)，未另选默认室外；提交页标明只展示客厅→阳台→主卧、有效选择及转场倍率。选择变更须同步主体、口播与展示时间后生成新版本，不能仅改页头。

每章说明S-ID、时窗、动作/主体、展示内容（室内/室外/转场移动）、口播及字幕；有配乐/风险时列明，无旁白或音乐可写无。图源来自当前房源，来源索引放内部。首镜户型、室内背景/标题与尾镜引流按本次要求实际画出；路线图只用于审核，不自动加入成片。

路线、朝向或章节时码修改后，同步重绘同版完整剧本再交付，在同一中文审核页保留总板、完整户型路线板与正文。交新审看片也要附对应剧本；不能只交视频页、漏掉完整方案板，或拿已退回的旧剧本代替当前版。构图或动作未动态验证时在同版剧本标明，不冒充已拍成片。

实际打开并核对图像加载、文字可读与图文对应。一次提交说明制作范围、已知限制和待决事项；可以交完整HTML/Markdown文档链接，不要求在聊天重复全部正文或展示技术哈希。

## 一次批准与内部绑定

用户对清晰版本/范围自然回复批准或“接受，现在开始”即可；不要求固定口令、紧邻parentId、浏览器Current URL或事先工具回执。孤立的同意、否定答复或指向其他版本的回复不算本版批准。

新记录默认presentation.mode=linked_document，document_path指完整Markdown或已绑定的自包含HTML，transcript_path/assistant_event_id定位真实展示，approval.user_event_id/explicit_text定位实际回复；approval.plan_sha256/bundle_sha256由工具在收到批准时存内部快照。模板见[record](../assets/templates/record.json)。保存真实原事件，不自造批准；结构检查不认证人类身份。

linked_document的BUNDLE只绑定可审核内容与范围，忽略探索计数、预检回执、渲染配置及输出目录等运行细节；用户明定预算仍绑定。素材/正文静默漂移被拒绝，范围内参数纠错与换新输出目录不要求第二次内容批准。历史inline_cards/rendered_document及原claim保留读取兼容，不要求重写旧批准。

SCRIPT_APPROVED_ONCE是历史状态标识，表示完整范围已获批，不是只准尝试一次。获批后自主完成采集和列明后期；仅改变事实/承诺、覆盖、用户硬要求、来源权利或费用时回审。发布另核，用户明确不重拍仍生效。

## 工具

Python 3.10+，标准库。路径相对record；Markdown图路径相对正文。SHA用于防错源/静默漂移，由工具计算，不给用户增加阅读任务。

```bash
python3 scripts/check_shooting_plan.py --record /private/version/record.json --phase review
python3 scripts/check_shooting_plan.py --record /private/version/record.json --phase capture --claim
python3 scripts/check_shooting_plan.py --record /private/version/record.json --phase post
```

--claim只预留新的输出目录，避免并发覆盖；技术失败可保留记录后换新目录重试，不设全局次数。post_only绑定base_media与master资产，只做后期，不能启动capture；已有工作目录可恢复，调用方保留成功媒体并以新文件输出改动。

请求动作按scope.requested_actions与authorized_actions核对，不强制所有任务都配BGM或CTA。预检按[连续技术](continuous-take.md)记录相关画面；只查字段与SHA不等于画面通过。

新图文板保留scope.storyboard_layout及review_route_layout的内容/图源/实际检查绑定，以发现缺整板、漏章、旧时码和未嵌入路线图；这项来自本项目反复发生的交付遗漏，不作为额外用户审批。
