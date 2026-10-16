# 可运行技术示范

本页把已用过的技术整理为可复用实现，按需要选读，不增加审批层级或尝试次数限制。代码在 [technical_examples](../../scripts/technical_examples/)。当前房源及其版本、路线、批准和画面问题仍以项目交接为准；运行示范不操作该房源。

| 示例 | 提供什么 | 本次验证与限制 |
|---|---|---|
| [panorama.mjs](../../scripts/technical_examples/panorama.mjs) | 注入当前SDK实例，预加载、实际姿态检查、导航回调、可选原生时戳录制、finally恢复 | 4组离线模拟；未在真实SDK执行抽取后的适配器 |
| [retime.py](../../scripts/technical_examples/retime.py) | 单原件完整时间映射，局部加速，不硬切或删除时间区间 | 实际FFmpeg：6秒→约5秒；输入未变。分段恒速，不含速度渐变或补帧 |
| [align_voice.py](../../scripts/technical_examples/align_voice.py) | 本地既有mlx-whisper模型，无台本提示的词级识别时码 | CLI入口检查；本次未执行模型识别，不自动下载模型 |
| [postprocess.py](../../scripts/technical_examples/postprocess.py) | 已有旁白落位、真实时码字幕、Pillow烧录、音乐交叉淡化延展、旁白侧链压低、导出 | 实际FFmpeg/Pillow合成信号检查；未作真实配音试听或音乐审美验收 |
| [demo.py](../../scripts/technical_examples/demo.py) | 一条命令生成完整离线演示、输入清单、回执和审看页 | 测试画面、正弦音及人工测试时码，绝不冒充房源或配音 |

来源：SDK结构提炼自私有v10预检02；初始化归位候选来自v12准备代码；音频处理提炼自v5后期。历史原件与脚本保留私有，没有复制房源ID、点位表、配音文案、凭据或素材。历史实际运行不能证明抽取后适配器已通过真实SDK验证。

## 先运行离线演示

依赖：已有FFmpeg/ffprobe、Python及Pillow；SDK示范另用Node/浏览器。字体显式传入，不写死某台电脑路径。以下从仓库根目录运行，`python3`须指向含Pillow的环境：

```bash
python3 skills/vr-production-gates/scripts/technical_examples/demo.py \
  --font /path/to/existing-font.ttf --out /tmp/vr-technical-demo
```

打开输出的`review.html`，观看`post/final.mp4`。新目录用于防覆盖输入，不代表“一次机会”。生成后的技术回执保留输入身份、实际命令、时长与未验证项；它不是用户验收。

## SDK预加载、连续运动与恢复

由当前宿主取得已登录房源的实际SDK实例`f`，在浏览器模块中导入后主动调用。模块导入本身不导航、不录制、不上传。下列点位和尺寸只说明格式，必须替换为当前已核实拓扑与视口：

```javascript
import {runRoute} from './panorama.mjs';
const recipe = {
  workCode: 'REPLACE_WITH_CURRENT_WORK',
  start: {pano: 0, yawRad: 1, fovDeg: 80},
  width: 320, height: 568, dpr: 1,
  tolerance: {fovDeg: 0.02, position: 0.001},
  timeoutMs: 15000,
  steps: [
    {kind: 'hold', ms: 500},
    {kind: 'pan', yawRad: 1.2, ms: 1000},
    {kind: 'move', pano: 1, yawRad: 1.2, ms: 2000}
  ]
};
const result = await runRoute(f, recipe, {record: false});
// 当前制作已含录制授权且适配已验证时才选择record:true。
// result.media为Blob，保存媒体与JSON遥测时分开处理。
```

这个适配器依赖源代码中同款SDK接口，不是所有全景SDK的通用驱动。宿主提供实际视口布局；容差按当前尺度选取。先检查实际主相机、邻接关系、画面与状态恢复，再据本次任务使用。等待ready不等于实际FOV和位置已归位；适配器显式归位并回读。原生requestFrame保留实际录制节奏，不自动消除SDK过渡重影或导航停留，也不证明恒定帧率。

导航等待实际moveEnd/moveCancel，不能靠超时Promise假装已取消运动。若SDK挂起，宿主应使用其真实取消接口停止运动再恢复；本例未猜测取消API。录制停止后回收轨道；恢复同步函数时保留原有属性描述符或继承关系。控制/恢复检查与画面接受分开记录，未实际观看仍是PENDING。

离线生命周期检查：

```bash
node skills/vr-production-gates/tests/test_panorama_example.mjs
```

## 单原件完整时间线局部变速

先用实际文件SHA及ffprobe时长填写映射；数值应来自当前原件，不复制示例片长。6秒示例：

```json
{
  "schema": "vr-continuous-edit/v1",
  "source_sha256": "REPLACE_WITH_ACTUAL_SHA256",
  "source_duration_s": 6,
  "speed_map": [
    {"source_start_s": 0, "source_end_s": 2, "speed": 1},
    {"source_start_s": 2, "source_end_s": 4, "speed": 2},
    {"source_start_s": 4, "source_end_s": 6, "speed": 1}
  ]
}
```

```bash
python3 skills/vr-production-gates/scripts/technical_examples/retime.py \
  --source /path/to/source.mp4 --map /path/to/map.json --out /path/to/new-edit
```

SHA或时长不符、时间线缺口/重叠/倒序、非法速度会拒绝。源有声音时先明确处理：本示例仅支持显式`--discard-audio`后另配旁白，不用于让原声自动跟随变速。变速复用现有`storyboard.model.validate_editing`，没有另造一套连续性规则。

实现用一个连续时间戳函数，不按段截断拼接。加速会采样掉部分帧；完整的是源时间区间映射，不是保留全部帧。恒速分段边界可能突变，不能据此宣称丝滑；渐变速度、源卡顿/重影和主观运动观感需要另行设计与实际观看。输出`continuous-edit.json`记录这些限制。

## mcode配音、对齐与后期

mcode作为当前宿主上的服务入口，不把旧工具schema或认证信息写入Skill。先用本机`mcode exec --help`核实入口；在当前制作已包含所需生成授权时，通过已登录宿主发现当前配音/音乐工具并执行。可把以下文字放入`voice-task.txt`，再运行：

```bash
mcode exec --cwd /path/to/private-production --input - \
  --prompt-mode work --output-format json < voice-task.txt
```

任务文字示例：先发现当前可用的配音与音乐工具及完整schema；按当前方案的完整语义句生成旁白，字幕cue不拆成逐字配音请求。使用明确音色与互不覆盖的输出文件，保留实际请求、资产ID及逐项成功失败回执。只补确认失败项；未知状态先查任务，不重复计费。音乐按当前方案生成或复用已有合法资产。不得把凭据或临时签名URL写入公开仓库。

本次只核对CLI入口，没有调用mcode发现工具、生成配音或音乐；上面是操作模板，不宣称当前具体服务已可用。批量回执沿用[check_media_batch.py](../../scripts/check_media_batch.py)，具体用法看其`--help`：code=0不代表每项成功，不另实现批处理器。

取得实际音频后，使用已安装的本地模型进行词级识别：

```bash
python3 skills/vr-production-gates/scripts/technical_examples/align_voice.py \
  --audio /path/to/S01.mp3 --model-dir /path/to/existing-local-model \
  --out /path/to/S01-alignment.json
```

对齐输出绑定音频SHA，保留实际识别文字；不使用台本提示或均分时码。需另核听漏字、专名和重音，词级识别本身不保证内容正确。此可选适配器本次未运行实际模型。

后期输入`post.json`示例，路径相对该JSON，`start_s`是**变速完成后的最终时间轴**：

```json
{
  "video": "edited/retimed.mp4",
  "font": "/path/to/font.ttf",
  "music": "music.wav",
  "music_gain": 0.12,
  "narration": [
    {"id": "S01", "text": "实际完整识别文字", "audio": "S01.mp3",
     "alignment": "S01-alignment.json", "start_s": 0.5}
  ]
}
```

```bash
python3 skills/vr-production-gates/scripts/technical_examples/postprocess.py \
  --plan /path/to/post.json --out /path/to/new-post
```

`music`可省略。字幕保留词级时码，默认整句显示；不等于逐字高亮效果。识别字词拼接与期望文本不符、时码越界/重叠、音频身份不符时停止并暴露差异，不拿期望文案覆盖错误。标点或同音差异也要核对后显式修订输入。

输出包含`final.mp4`、`mixed.wav`、`subtitles.srt`、词级时码与后期回执。Pillow字幕路径适用于本机FFmpeg缺libass的情况；排版参数只是示范值，正式样式仍按本次剧本。音乐交叉淡化循环、语音侧链压低和限幅只是技术处理，不代替试听、响度检查与用户接受。片头户型、标题和片尾引流层使用现有设计系统；本音频/字幕示例不假装已完成这些包装。

## 正反检查与完成边界

```bash
# 使用含Pillow的Python环境
python3 skills/vr-production-gates/tests/test_technical_examples.py
```

既有实际媒体检查覆盖：完整变速及源保护、映射缺口拒绝、混音及字幕真正烧录、错误音频SHA拒绝、台本差异拒绝。另有四项SDK离线模拟检查恢复与失败路径。

“已完成技术示范”是可复现代码、明确输入输出、正反检查和限制说明齐全；不是当前房源画面获批、真实SDK运行、mcode生成、模型识别或真人试听完成。后续真实制作继续沿用当前任务授权和审看流程，不从示例衍生新的固定次数门槛。

## 已有BGM的开头片段

先核用户给出的音频目录与曲目版本，再运行；Python标准库、FFmpeg/ffprobe即可，不调用生成服务或网络。输出使用新目录，已存在目录拒绝覆盖，原曲不移动。

```bash
python3 skills/vr-production-gates/scripts/technical_examples/prepare_bgm.py \
  --source-dir /path/to/BGM --out /path/to/BGM/opening-excerpts --seconds 35
```

读取目录顶层真实音轨（忽略嵌入封面作为视频的情况），取0至所选秒数或原曲实际结尾。两遍测量/处理统一响度，48kHz/24-bit立体声WAV供剪辑、AAC M4A供试听，含短入点与末尾淡化；参数和实际值写清单。声床与旁白的最终相对响度仍需混音，不把−18 LUFS素材目标作为通用BGM混音标准。

`试听索引.html`链接实际文件，`清单.json`留源路径/标签/SHA、源时长/截取区间、处理命令与输出解码/响度结果。工具保留原曲和未完成输出供检查，不下载、改曲名、推定版本相同或证明发布权利。输出少于源时长不代表漏曲；静音、解码失败或编码后削波会报错。

项目实作说明：曾用单调PCHIP把完整连续源时间映射到新章节时间，保持方向和全部区间；画面提速后复用原语音及词级时码、重排落位，指定歌曲单独裁剪混音。该方法需验证导数为正及端点/实际输出，分段常速CLI不能冒称已实现相同渐变。具体房源、曲目和倍率留案例记录，不固化为其他任务默认值。

开头整理器另核短源不循环/不补静音、既有输出不覆盖、纯静音不冒称可用；使用合成音调验证这些行为，不将合成数据当作曲目听感。

## 实作问题的定位入口

| 现象 | 原因与处理入口 |
|---|---|
| 为避墙而倒退离开阳台 | 局部避墙目标压过整体运动方向；先转向再正向移动，见[路线与运动](../short-route-motion.md) |
| 推进慢，片头/到点停留拖节奏 | 未分开移动与展示时间；对照参考端点、压缩无信息停留并平缓变速，见[参考片与推进节奏](../short-route-motion.md#参考片与推进节奏) |
| 新视频仍用旧时码字幕/旧方案板 | 改了画面时间轴却未更新衍生物；重排原声词时码并同版交付，见[图文剧本](../illustrated-script.md) |
| 指定歌曲却用了相似生成曲 | 混淆生成声音与复用用户素材；核实际文件和版本，按[声音制作](../audio-production.md)完成混音 |
| 批量配音返回成功却缺音频，或字幕只有关键词 | 顶层成功不等于逐项成功、对齐不等于内容核听；核逐项回执与实际词时码，保留独立识别差异，见[声音制作](../audio-production.md) |
| 视频全解码/CFR通过，仍见SDK重影 | 源画面投影问题与后期技术通过不是同一件事；保留源限制，不伪称变速或插帧已修复 |

曲目清单、房源路线和本片倍率仍归项目案例；上述入口归纳如何判断和修复，不给未来任务新增配额或审批。
