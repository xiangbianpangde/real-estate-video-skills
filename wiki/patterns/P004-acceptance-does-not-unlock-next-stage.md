# P004 · 上一阶段接受不自动解锁下一阶段

**状态**：active ｜ **首次记录**：2026-10 ｜ **来源**：多次边界争议

> **3.0.0兼容说明（2026-10-12）**：保留下文历史正文。真实图文脚本的一次完整制作批准可覆盖列明采集与首尾/配音/字幕/BGM/导出/QC，不再等待母版接受或逐层索权；旧局部批准、路径-only批准仍不追认。“一个输出尝试”对正式采集指一次take，失败也消费；同母版获批后期可另存新版本，不覆盖原件、不重拍。新后期范围按`post_only`绑定原母版回审，不篡改旧claim。技术通过、最终用户接受、发布许可仍独立。当前依据为[Skill](../../skills/vr-production-gates/SKILL.md)与[验收矩阵](../../skills/vr-production-gates/references/acceptance-matrix.md)。

## 现象

真实案例里反复出现同一类误解风险：

- 用户说"继续"被当作下一镜的执行许可；
- 某个镜头被接受，被当作整片剪辑的许可；
- 静默母版被接受，被当作后期成片的许可；
- 脚本被批准，被当作商业发布的许可。

这些跨阶段推断一旦成立，真实性门禁就形同虚设。

## 有效做法

把状态拆开记录，每一步只承认自己那一步的证据：

| 层级 | 状态 | 证据 |
|---|---|---|
| 脚本 | `SCRIPT_APPROVED_ONCE` | 脚本版本 SHA + 批准范围 |
| 镜头/整片/后期 | `APPROVED_ONCE` | 合同范围 + 一次性许可 |
| 技术检查 | `technical_passed` | 技术/QC 凭据 |
| 用户接受 | `ACCEPTED` | 用户对确切 SHA 的明确决定 |

关键规则：

1. `technical_passed` 不是 `ACCEPTED`。
2. 接受一个 SHA 不等于接受另一个 take、整片方案、声音、字幕、CTA、付费或发布。
3. 一次许可只允许一个输出尝试；输出目录已存在时必须失败而不是覆盖。
4. 脚本批准允许一体化执行合同内范围，但用户仍须在成片交付后验收。
5. 保留旧 take 与凭据；退回不触发自动重试。

## 影响

- `skills/vr-production-gates/SKILL.md` 触发边界与工作流第 0 步
- `skills/vr-production-gates/references/acceptance-matrix.md` Required state split
