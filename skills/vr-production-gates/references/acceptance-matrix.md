# 验收证据矩阵

| 门禁 | 必须具备的证据 | 阻断什么 |
|---|---|---|
| Script approval | 完整脚本/分镜表、逐句事实与来源、时间轴、权利与范围 SHA；显式 `SCRIPT_APPROVED_ONCE` | 一体化执行 |
| Integrated execution | 已批准脚本 SHA、全部输入 SHA、逐镜 QC 索引、无覆盖保护、单一输出 take | 成片审看 |
| Contract | `DRAFT` → `APPROVED_ONCE`，一次性范围，无覆盖保护 | 渲染 |
| Preflight | 只读边界检查、源/方案/事实 SHA、输出不存在 | 渲染 |
| Render | 只产生一个新 take、无合成像素、无批量/重试 | 下一环节 |
| Technical | 编码、尺寸、帧率、帧数、时长、CFR、全解码、音轨 | 审看 |
| Playback | 浏览器完整播放至结束、无媒体错误、console/page errors 为 0 | 接受 |
| Human acceptance | 确切输出 SHA 写入记录、用户明确决定 | 下一阶段 |
| Assembly | 全部输入已接受、顺序与切点明确、静默内部范围 | 声音/发布 |
| Post design | 已批准脚本与时间轴、CTA 边界、provider/来源与权利方案 | 资产生成 |
| TTS/BGM/SFX assets | provider/model/voice 或来源许可、文件 SHA、格式/采样率/码率、候选 QC | 混音 |
| Post mix | 单一新 take、旁白优先、音乐/音效电平、无削波、时长固定 | 字幕/成片 |
| Subtitle style | 正文单行居中、白字粗黑描边、1–2 处黄色事实锚点、无底框；标题卡另行设计 | 烧录 |
| Subtitle burn-in | 目标语言字形可读、对比与位置可读、时间码不越界、字体路径与 SHA；中心位置默认约 0.61H，需实帧核对安全区 | 成片审看 |
| Post playback | 浏览器加载与全解码、无 console/page error、确切最终 SHA | 人工接受 |

## 状态必须拆开

- `technical_passed` 不是 `ACCEPTED`。
- 接受一个 SHA 不等于接受另一个 take、整体方案、声音、字幕、CTA、付费生成或发布。
- `APPROVED_ONCE` 只授权一次输出尝试；已存在 take 时必须失败关闭。
- 脚本批准可跳过中间逐镜批准，但不能跳过逐镜证据、技术 QC、浏览器播放与最终用户审看。
- 交付后的用户意见必须映射到脚本段落 ID；超出已批准脚本的改动需要新的脚本审阅与批准。

## 最小接受记录

```json
{
  "decision": "ACCEPTED",
  "scope": { "output": "...mp4", "output_sha256": "..." },
  "accepted_at": "YYYY-MM-DD",
  "notes": "范围限制；不自动解锁发布或新版本"
}
```

## 负向测试

- 房源命名空间、源面或源 SHA 不匹配 → 拒绝。
- 点位、FOV、yaw、位移、时长、音频、成本或输出路径与合同不符 → 拒绝。
- 输出目录已存在 → 拒绝，不覆盖、不重试。
- 缺少浏览器播放、媒体错误、解码失败或 SHA 不匹配 → 不得接受。
- 使用旧 take、未接受输入、生成填充或无依据的房间/指标主张 → 永远不得纳入。
- 字形缺失、字幕方框、时间码越界、音乐权利不明、削波或音乐盖住旁白 → 拒绝。
- 正文字幕擅自加底框、整行标黄、超过两处高亮、自动换行，或未按批准脚本与事实压缩 → 拒绝；用户明确批准的独立版式例外须写入脚本合同。
- 已接受的静默母版不接受后期成片；后期 SHA 需要新的明确决定。
