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

## 回归检查

修改 Skill 后逐条确认：

- [ ] P001：脚本先审门仍在，且仍保留逐镜备用模式
- [ ] P002：后期 QC 仍要求字幕字形可读与抽帧目视
- [ ] P003：BGM/SFX 仍需记录来源、许可、SHA 与响度
- [ ] P004：`technical_passed` 与 `ACCEPTED` 仍未合并
- [ ] P005：字幕末条仍要求不越界
- [ ] P006：预检仍先于生成

任一项丢失视为回归，不得发布新版本。

## 未被 Skill 吸收的经验

当前无。若某条模式长期找不到落点，说明 Skill 缺少对应行为，应补 Skill 而不是长期挂起。
