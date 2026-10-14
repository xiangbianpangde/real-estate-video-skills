# 整体图文方案板版式合同

用户提供格式参考时，先读取真实参考图并提取信息层次。当前约定是一张可横向比较整片节奏的方案板；相似排版不要求沿用参考的房源、方法ID、章节数量、硬切或逐镜审批。

## 交付结构

- 顶部：房源/版本/状态、整片目标、章节顺序、时长及一次制作范围。
- 中部：按顺序横向排列章节卡片。每卡有S-ID、起止时码/时长、章节目的与标题、当前房源真实源图、运镜动作/方法、观看重点、口播及字幕口径/黄标、画面限制。图与字段必须同卡排版。
- 下部：真实户型及其用途、此次调整、与参考或旧版本的差异、待审核项、首尾/声音/字幕方案和一次整包审核范围。
- 章节较多可加宽画布或分成有明确顺序的行，不缩成不可读的接触表。给出可放大原图/HTML；具体尺寸与字号按内容和参考决定，不强制七章或固定配色。

**原始截图只是卡片的图像素材。** Markdown标题＋原截图＋外置文字列表、缩略图总览、JSON字段齐全均不能单独作为版式达标。完整正文为取证和详细阅读的附文，不替代成图。

## 三种图像用途与首镜

真实源参考只证明素材来自当前房源；动作示意用相机/视锥/方向箭头或静态/FOV符号表达拍法，并附短标签；成片布局预览把真实源与计划中的标题、户型浮层实际排在同一画面。三者分别标注，不能相互代替。

每卡的镜头动作区域必须有图示＋短说明，不能仅输出action文字。示意箭头只表达拍法，不证明现场路线。每段显式填写`visual.title`、`visual.layout`及`visual.motion={kind,label}`；kind支持static/pan/travel/orbit/fov，不从房间名或文字猜动作。标题按叙事角色填写，不按coverage数组索引自动命名。

首镜按当前首尾合同制作布局预览：真实室内背景＋真实户型图浮层＋两行已核证标题。`visual.layout=opening_composite`并填写两行`headline_lines`；户型图保比例、不裁墙线。卡片标明“布局预览，非已录成片”，保留源图索引。正文说先看户型，首镜预览就必须能看到户型；整张板下方的户型资料不能替首镜浮层。用户明确批准其他首镜结构时按其结构另画，不机械套默认。

## 生成与实际检查

已有合适模板优先复用。也可从同版record生成代码图源：

```bash
python3 scripts/build_storyboard.py --record /private/new-version/record.json \
  --floorplan /private/new-version/floorplan.png \
  --output /private/new-version/storyboard.html
```

生成器将源PNG嵌入HTML，核源图SHA并转义文案，拒绝覆盖输出。事实/音频/变更/限制说明可通过`board_content`的`fact_caption`、`audio_caption`、`text_changes`、`limitations`填写；它们进入HTML后由图源SHA绑定。不要沿用其他房源文字。生成HTML不是已完成成图。

用浏览器真实加载图源，等待字体和全部图片，核章节数量/顺序、图片加载、文字及元素溢出；逐卡对照动作图示和文字一致，并核首镜户型/标题/背景三层可见；导出完整PNG，放大查看标题、各卡、底部说明。将实际观察写入回读记录，不从文件存在或门禁exit0推断格式合格。

新包`vr-production-plan/v3`在`scope.storyboard_layout`声明：

```json
{"kind":"overview_board","board":"overview.png","source":"storyboard.html","review":"layout-review.json"}
```

三项均列assets：`overview`、`storyboard_source`、`layout_review`。回读记录：

```json
{
  "schema":"vr-storyboard-layout-review/v1",
  "board_sha256":"实际PNG摘要",
  "source_sha256":"实际HTML摘要",
  "segment_ids":["S01","S02"],
  "all_images_loaded":true,
  "no_overflow":true,
  "reference_structure_matches":true,
  "motion_diagrams_reviewed":true,
  "opening_composite_reviewed":true,
  "review_basis":"浏览器实际加载/布局测量和导出PNG目视记录位置"
}
```

只有实际检查后才写true；参考结构匹配是执行者目视判断，用户是否接受仍独立。检查器核字段/摘要/章节，不能自动识别卡片审美或保证证据作者可信。旧v2只历史兼容；新包不降级schema以绕过版式证据，不把用户退回的版式当已批准。

最终展示整张成图、可放大附件、同版正文及摘要。版式修订只更新审核包，不重开探索或启动拍摄。
