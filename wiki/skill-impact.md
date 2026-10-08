# Skill 影响表

记录每条 wiki 模式约束了 Skill 的哪一段，便于回归检查：改 Skill 时对照本表确认没有把某条经验改丢。

## 映射

| 模式 | Skill 文件 | 段落 | 门禁编号 |
|---|---|---|---|
| P001 | `SKILL.md` | 工作流 · 第 0 步 脚本先审门 | Script approval / Integrated execution |
| P002 | `SKILL.md` | 第 B 步 10 后期 QC 与接受 | Subtitle burn-in |
| P002 | `references/acceptance-matrix.md` | Subtitle burn-in 行 + 负向测试 | — |
| P003 | `SKILL.md` | 第 B 步 8 后期资产 / 第 B 步 9 后期单 take | TTS/BGM/SFX assets / Post mix |
| P004 | `SKILL.md` | 触发边界、第 0 步、第 B 步 6 人工门禁 | Human acceptance |
| P004 | `references/acceptance-matrix.md` | Required state split | — |
| P005 | `SKILL.md` | 第 B 步 9 后期单 take | Post mix |
| P006 | `SKILL.md` | 第 B 步 4 先测后写 | Render / Preflight |
| P007 | `SKILL.md` | 第 0 步脚本包、第 B 步 9 后期时间轴、第 B 步 10 后期 QC 与接受 | Subtitle intent / coverage / style / burn-in |
| P007 | `references/subtitle-style.md` | 完整口播与卖点压缩模式、首/中/尾角色、背景与标题/CTA授权边界、视觉版式、时间同步及拒收条件 | — |
| P007 | `references/opening-ending-layout.md` | 2.5.0 首尾目标优先级、三层开场/室内尾镜、源时间与布局合同、结构与覆盖分项验收 | Opening/ending match |

## 回归检查

修改 Skill 后逐条确认：

- [ ] P001：脚本先审门仍在，且仍保留逐镜备用模式
- [ ] P002：后期 QC 仍要求字幕字形可读与抽帧目视
- [ ] P003：BGM/SFX 仍需记录来源、许可、SHA 与响度
- [ ] P004：`technical_passed` 与 `ACCEPTED` 仍未合并
- [ ] P005：字幕末条仍要求不越界
- [ ] P006：预检仍先于生成
- [ ] P007：字幕仍保留单行居中、白字黑描边、少量标黄、无底框；标题卡独立；完整口播覆盖不得被卖点压缩误替代，内容模式与交付方式须入合同；首/尾结构必须分别对比，超范围先审脚本

任一项丢失视为回归，不得发布新版本。

### 2.5.0 首尾专项回归

- `reference_match` 不以资料卡获批代替匹配；目标截图优先于历史排版模板。
- 新室内浮层重测主体 bbox，不继承旧卡片区域守卫；开场标题不套正文小字号。
- 完整口播/免责声明冲突先交决策；CTA 不复制参考事实，生产仍需一次性许可。
- 技术/首结构/尾结构/口播/人审分开，正文与音轨回归不省略。

## 未被 Skill 吸收的经验

已登记模式均有落点。本轮分色字形擦除、失效阈值、空缓冲音频检查等案例细节见 `skills/vr-production-gates/HANDOFF.md` 第8节；现有字形/回归/阻塞规则已约束其处置，但案例启发式和数值尚非通用门禁或新自动化。若后续要将具体检测算法固化为行为，应另做适用性回归与版本修订，不从本次摘要推断已实现。
