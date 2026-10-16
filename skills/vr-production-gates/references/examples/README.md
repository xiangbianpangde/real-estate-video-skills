# 图文笔记与技术示范

本目录保存历史**图文笔记**：抽象示意图 + 判据说明。旧文与图中的固定次数、claim消费和像素门槛已由4.0撤销，只作历史示意；执行以当前SKILL与专项参考为准。

[可运行技术示范](technical-examples.md)提供SDK生命周期、完整时间线变速、mcode入口及音频字幕后期；附离线合成视频演示。媒体用于实际播放和烧录检查，说明与回执用于定位问题，两者配套。实际房源素材由调用方提供，按本次用户授权管理；通用Skill不固定其存储位置或分发权限。

| 笔记 | 覆盖内容 |
|---|---|
| [example-01-integrated-run.md](example-01-integrated-run.md) | 有限探索、真实源图文脚本结构、一次完整制作批准、验收阶梯、后期版本与采集次数分离 |
| [example-02-post-audio-subtitle.md](example-02-post-audio-subtitle.md) | 时间轴对齐、配音重排、音乐延展与响度、字幕覆盖模式、参考片版式与可读性 |

## 图片生成

这些是完整仓库维护命令，需在仓库根目录执行；独立安装Skill不包含包外tools，复用现有示意PNG即可。

示意图由仓库 `tools/make_example_figures.py` 生成，可重复执行：

```bash
python3 tools/make_example_figures.py
```

图中不含任何真实房源画面、素材、标识或个人信息。`05-subtitle-style.png` 是虚构室内字幕示意，不是真实截帧；`06-illustrated-script.png`按整体方案板结构提供格式占位，**不可通过实际拍摄检查**。真实参考PNG留私有项目。

只更新指定图可用 `--only modes states timeline subtitle-check storyboard`；保持未改变的旧图不重写。图文脚本协议与可复用模板见上级 `illustrated-script.md` / `illustrated-script-template.md`。

`07-visual-semantics.png`是3.4.0生成器在隔离虚构素材上实际浏览器渲染的验证图，不是真实房源；不由旧make_example_figures覆盖。动作图示和首镜合成布局按上级版式合同检查。
