# 图文笔记示例

本目录只放**图文笔记**：抽象示意图 + 判据说明。

不提供视频或音频素材。原因是这类素材在文档环境中基本无法被阅读与检索：
无法逐帧核对字幕、无法比对响度、也无法在文本里定位问题。真正有用的交付物是
"该看哪里、该判什么、什么条件下拒绝"。

| 笔记 | 覆盖内容 |
|---|---|
| [example-01-integrated-run.md](example-01-integrated-run.md) | 有限探索、真实源图文脚本结构、一次完整制作批准、验收阶梯、后期版本与采集次数分离 |
| [example-02-post-audio-subtitle.md](example-02-post-audio-subtitle.md) | 时间轴对齐、配音重排、音乐延展与响度、字幕覆盖模式、参考片版式与可读性 |

## 图片生成

示意图由 `../../../../tools/make_example_figures.py` 生成，可重复执行：

```bash
python3 tools/make_example_figures.py
```

图中不含任何真实房源画面、素材、标识或个人信息。`05-subtitle-style.png` 是虚构室内字幕示意，不是真实截帧；`06-illustrated-script.png`只有格式占位，**不可通过实际拍摄检查**。真实参考PNG留私有项目。

只更新指定图可用 `--only modes states timeline subtitle-check storyboard`；保持未改变的旧图不重写。图文脚本协议与可复用模板见上级 `illustrated-script.md` / `illustrated-script-template.md`。
