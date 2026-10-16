# 模板与素材位置

`assets/`只放可随Skill分发、可直接复制使用的通用资产。当前[生产记录模板](templates/record.json)是填写剧本的起点；章节卡、动作图示和首尾组件继续由[设计系统](../design-system/SPEC.md)与既有生成器维护，不复制第二套。

真实房源、完整音乐、配音、字体授权文件及制作原件不打进通用Skill包。默认保存在用户指定私有目录；本次用户明确要求全部素材提交推送，已将这些实际文件置于仓库平级的materials目录，保留原始/衍生与来源清单。该授权只覆盖本次资料，不自动用于未来私人内容。仓库本地工作区采用下面的边界；独立安装Skill时，由用户提供实际素材位置，不推测安装目录外的固定路径。

```text
local/
  index.html                  本机工作区入口
  material-library/           兼容链接至materials/library（当前实体）
    index.html                素材库入口
    catalog.json              只索引子库，不重复逐曲测量数据
    bgm/
      原曲/                    唯一完整曲源
      可用开头片段/
        音频/                  WAV剪辑版与M4A试听版
        清单.json              来源、区间、SHA、参数与实际检查
        试听索引.html           每首短片段与完整原曲入口
  productions/
    index.html                当前交付入口
    current/                  既有交付的导航链接
  validation/                 执行证据、迁移备份与可复现检查
  session-exports/             历史会话资料
```

素材库与制作输出分开：完整BGM不因某次成片长度而截断，衍生片段另存；35秒只是一种现有版本，40秒等长度从原曲裁剪。当前制作仍引用实际原件及批准快照，不把素材存在视作制作或发布许可。

原曲移动后更新当前清单和入口，保留历史处理路径和校验记录。兼容入口只指向唯一目录，不复制媒体。新增类别有真实素材时再落目录，不预建空的照片/音效/字体分类。

工具：[BGM整理器](../scripts/technical_examples/prepare_bgm.py)；流程和示例见[声音制作](../references/audio-production.md)。当前项目状态继续由既有HANDOFF/Wiki与原始证据维护，本页只说明分工和位置。

本轮可分发素材实际在materials/library、materials/productions/house-002与materials/references，入口materials/index.html。local会话和缓存仍不提交；历史来源绝对路径保留，跨机器入口均使用包内相对路径。
