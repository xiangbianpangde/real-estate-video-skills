# 当前项目交接导航

行为与版本以[SKILL.md](SKILL.md)为准，目录分工见[模板与素材位置](assets/README.md)，当前证据见仓库raw与Wiki。本页不重复生产规则。

- **当前版本：4.3.0目录定版**。通用模板位于assets/templates/record.json；原规范/脚本/设计系统入口稳定，历史交接保留原路径。当前工作区、素材库和制作入口均已建立；4.3.0目录提交147a3ac已推送；用户随后要求Wiki与全部BGM等资料一同提交推送，本轮将实际素材纳入materials，状态以本次Git结果为准。
- **本机入口**：仓库local/index.html。素材实体按用户追加授权提交至materials/library/bgm，local/material-library为兼容链接，Downloads/BGM是兼容符号链接，只有一份媒体。5首完整原曲与10份35秒WAV/M4A片段SHA核同；索引同时提供完整原曲。DJ阿狸版不等于DJ小辞版，缺黑神话未补造；40秒等版本从原曲重裁。
- **当前制作**：local/productions/current导航materials/productions/house-002/production/speed-v15内的v15交付。该片25.33秒，静止片头1.80秒、去阳台4.50秒、回卧室6.10秒；单原件完整区间平滑变速、mcode七句原声/真实词时码、指定喜剧之王与首尾包装。用户已回复“可以”并要求整理；不据此代签独立人工实听。此前v14批准原话/快照与所有原件保持不变。
- **保留要求**：禁止倒着移动拍摄；先转向再正向回程。卧室B一般在P15门口扫床窗；不拍卫生间，一镜到底，不硬切/删中间源区间。当前房源范围、曲目与倍率是项目事实，不变成所有任务默认值。
- **已知限制**：源SDK跨点重影/门框变形与转向扫过柜台仍在；速度接受不表示形变消除。公开SDK示范ISSUE039未在本轮修复，私有适配结果不冒充公开示范真实通过。专名/字母B语音识别差异与最终听感未代签。
- **目录检查**：Pi严格校验0错误/警告，目标实际加载两次零诊断；147项回归、72项门禁、SDK离线检查、5组设计系统CLI检查通过。真实浏览器从新入口到素材索引/当前成片通过，5首时长、5个完整原曲链接、成片25.33秒及全部图像加载正常。此轮不重拍、不重新生成音频。
- **验证边界**：本机完整技能发现仍有既存其他Office/Morph重名诊断；Codex简验器不支持既有Pi字段。未修改无关全局配置，未做新上下文模型触发验证。
- **迁移/回滚**：raw/R20261016-release-layout.json记录原路径、SHA和检查；local/validation/layout-backup保留迁移前文本。回滚为移除Downloads兼容链接、将BGM树原路移回，模板移回原位置并恢复引用；不回退既有未提交工作。
- **证据**：raw/R20261016-release-layout.json为本轮；Skill4.2.0/4.2.1与BGM实作见raw/R20261016-skill420-bgm-library.json、raw/R20261016-bgm-full-originals.json；制作见raw/R20261016-v15-speed-revision.json，实际过程见仓库wiki/cases/CASE-20261014-002-review-package.md。
- **后续**：按用户下一次制作或发布要求继续；目录定版不是发布许可，提交代码按本轮用户明确授权执行。旧版方案/删段试剪不能作为当前输入或当前接受。

本轮Skill使用的可检索复盘见仓库[CASE004](../../wiki/cases/CASE-20261016-004-skill-production-finalization.md)，包括要求、问题/解决、验证与遗留；当前模式映射见[Skill影响表](../../wiki/skill-impact.md)。

历史按需查[截至3.8.1的交接](HANDOFF-history-through-3.8.1.md)及[更早交接](HANDOFF-history-through-3.4.0.md)；历史状态不覆盖当前要求。
