# 图文剧本与提交

## 完整可审内容

按[设计系统](design-system.md)用同一record生成单一中文HTML，内含总方案板、完整户型路线板和详细正文。真实源参考、动作图示、首尾排版预览分别标明；不能用旧截图加长文替代当前完整方案。

定稿前完成[室内/室外展示选择](short-route-motion.md#展示选择与三空间范围)，未另选默认室外；提交页标明只展示客厅→阳台→主卧、有效选择及转场倍率。选择变更须同步主体、口播与展示时间后生成新版本，不能仅改页头。

每章说明S-ID、时窗、动作/主体、展示内容（室内/室外/转场移动）、口播及字幕；有配乐/风险时列明，无旁白或音乐可写无。图源来自当前房源，来源索引放内部。首镜户型、室内背景/标题与尾镜引流按本次要求实际画出；路线图只用于审核，不自动加入成片。

路线、朝向或章节时码修改后，同步重绘同版完整剧本再交付，在同一中文审核页保留总板、完整户型路线板与正文。交新审看片也要附对应剧本；不能只交视频页、漏掉完整方案板，或拿已退回的旧剧本代替当前版。构图或动作未动态验证时在同版剧本标明，不冒充已拍成片。

未批准时请用户自行打开本版审核页，再通过[Chrome DevTools MCP](../SKILL.md#浏览器工具)只读核图像加载、文字可读、图文对应及控制台错误，保存当前截图；模型不导航或执行页面脚本。MCP未接通时将浏览器验证记为未验证，不能用HTML生成成功或旧工具截图代替。一次提交说明制作范围、已知限制和待决事项；可以交完整HTML/Markdown文档链接，不要求在聊天重复全部正文或展示技术哈希。

## 一次批准与内部绑定

先按[MCode脚本确认流程](script-approval-gate.md)运行 `minimax.py review` 检查并取得本版指纹、完整链接及确认卡参数；在assistant聊天实际交付链接/文件及范围，再调用原生 `ask_user`，`requiresExplicitResponse=true`，一个单选步骤和批准/保持暂停两个选项。返回 `waiting_for_user` 后立即结束本轮。没有后续真实用户明确确认时，采集、配音、变速、混音、烧字和导出均不得开始；打印卡片JSON、截图成功、状态字段或工具执行权限都不能代签。此为流程门禁，不提供全部工具的硬拦截。

确认卡应独立说明本房源、本版完整脚本及主要范围。核本次真实卡片答复的requestId、步骤与选项；明确自然语言批准本版也可，不要求固定口令、紧邻parentId、浏览器Current URL或读哈希。孤立的同意、否定答复或其他版本不算批准；卡片工具不可用时交付完整脚本并结束等待真实明确答复，不虚报卡片已提交。

当前记录使用presentation.mode=linked_document，document_path指完整Markdown或已绑定的自包含HTML；MCode流程保持DRAFT/空approval，不从status/approval/transcript取授权。真实决定依据当前会话，在制作前用 `minimax.py check` 和**该次审核的原指纹**核内容及技术条件；CLI不验证用户身份或授权。模板见[record](../assets/templates/record.json)。独立旧CLI仅在已有真实历史转录时使用transcript_path/assistant_event_id、approval.user_event_id/explicit_text和plan/bundle快照；保存原事件，不让模型补造批准或为技术检查重复索权。

linked_document的BUNDLE只绑定可审核内容与范围，忽略探索计数、预检回执、framing_status验证状态、渲染配置及输出目录等运行细节；用户明定预算仍绑定。素材/正文静默漂移被拒绝，范围内参数纠错与换新输出目录不要求第二次内容批准。历史inline_cards/rendered_document及原claim保留读取兼容，不要求重写旧批准。

SCRIPT_APPROVED_ONCE是历史CLI状态标识，不能单独授予制作权限；其含义是完整范围已获批，不是只准尝试一次。获批后自主完成采集和列明后期；仅改变事实/承诺、覆盖、用户硬要求、来源权利或费用时回审。发布另核，用户明确不重拍仍生效。

## 工具

Python 3.10+，标准库。路径相对record；Markdown图路径相对正文。SHA用于防错源/静默漂移，由工具计算，不给用户增加阅读任务。

```bash
# MCode：review → 实际交付 → 原生ask_user暂停 → 真实批准 → 技术检查
python3 scripts/approval/minimax.py review --record /project/v1/record.json
# 以下只在本版真实批准后执行；原指纹不是批准凭据：
python3 scripts/approval/minimax.py check --record /project/v1/record.json \
  --fingerprint "<审核时指纹>" --phase capture --claim
python3 scripts/approval/minimax.py check --record /project/v1/record.json \
  --fingerprint "<同一审核指纹>" --phase post
# 旧check_shooting_plan.py CLI保留真实历史转录检查，不认证身份。
```

--claim只预留新的输出目录，避免并发覆盖；技术失败可保留记录后换新目录重试，不设全局次数。post_only绑定base_media与master资产，只做后期，不能启动capture；已有工作目录可恢复，调用方保留成功媒体并以新文件输出改动。

请求动作按scope.requested_actions与authorized_actions核对，不强制所有任务都配BGM或CTA。预检按[连续技术](continuous-take.md)记录相关画面；只查字段与SHA不等于画面通过。

新图文板保留scope.storyboard_layout及review_route_layout的内容/图源/实际检查绑定，以发现缺整板、漏章、旧时码和未嵌入路线图；这项来自本项目反复发生的交付遗漏，不作为额外用户审批。
