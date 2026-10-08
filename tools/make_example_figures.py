#!/usr/bin/env python3
"""生成示例图文笔记使用的示意图。

只画抽象流程与时间轴，不使用任何真实房源画面、素材或标识，
保证公开仓库中不含可识别的客户内容。

用法：
    python3 tools/make_example_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "skills/vr-production-gates/references/examples"

plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "Heiti TC", "PingFang HK", "Songti SC"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#1f2933"
MUTED = "#7b8794"
ACCENT = "#2f6f9f"
WARN = "#b4530a"
BAD = "#a12a2a"
OK = "#2f7d4f"
LINE = "#cbd2d9"


def box(ax, x, y, w, h, text, edge=LINE, fill="#ffffff", color=INK, size=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                linewidth=1.4, edgecolor=edge, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, color=color, weight=weight, linespacing=1.5)


def arrow(ax, p1, p2, color=MUTED, style="-|>", lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13,
                                 linewidth=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}"))


def canvas(w=11, h=6.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=160)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def fig_modes():
    """两种生产模式的门禁差异。"""
    fig, ax = canvas(11, 6.6)

    ax.text(0.02, 0.955, "默认模式：脚本先审，一体化执行", fontsize=13, color=INK, weight="bold")
    y = 0.79
    steps = ["写脚本包\n分镜 + 台本 + 时间码", "用户批准脚本\nSCRIPT_APPROVED_ONCE",
             "AI 一次跑完\n镜头 / 整片 / 配音 / 音乐 / 字幕", "技术 QC\n抽帧 / 解码 / 浏览器",
             "用户按脚本验收\n接受或提修改"]
    w, gap = 0.168, 0.037
    x = 0.02
    for i, s in enumerate(steps):
        last = i == len(steps) - 1
        box(ax, x, y, w, 0.125, s, edge=ACCENT if not last else OK,
            fill="#f4f8fc" if not last else "#f1f8f3", size=9.5)
        if i < len(steps) - 1:
            arrow(ax, (x + w, y + 0.062), (x + w + gap, y + 0.062))
        x += w + gap
    ax.text(0.02, 0.70, "用户只在两端出现：批准脚本、验收成片",
            fontsize=9.5, color=MUTED, style="italic")

    ax.plot([0.02, 0.98], [0.63, 0.63], color=LINE, lw=1)

    ax.text(0.02, 0.565, "备用模式：逐镜门禁", fontsize=13, color=INK, weight="bold")
    ax.text(0.02, 0.50, "事实不清、点位未核证、源面或位移风险、权利不明，或用户明确要求逐镜确认时启用",
            fontsize=9.5, color=MUTED)
    y2 = 0.30
    steps2 = ["单镜设计", "一次性许可", "只出一个 take", "镜头 QC", "SHA 人工接受"]
    x = 0.02
    for i, s in enumerate(steps2):
        box(ax, x, y2, w, 0.115, s, edge=WARN, fill="#fdf6ef", size=9.5)
        if i < len(steps2) - 1:
            arrow(ax, (x + w, y2 + 0.057), (x + w + gap, y2 + 0.057), color=WARN)
        x += w + gap
    ax.text(0.02, 0.20, "每一镜都必须停下来等用户：代价是往返多，收益是问题不会堆积到成片",
            fontsize=9.5, color=MUTED, style="italic")

    ax.text(0.02, 0.09, "两种模式都不跳过：技术 QC · 浏览器验证 · 事实边界 · 最终用户验收",
            fontsize=10, color=BAD, weight="bold")
    save(fig, "01-two-modes.png")


def fig_states():
    """状态阶梯：接受不可跨级。"""
    fig, ax = canvas(10.4, 6.0)
    ax.text(0.03, 0.94, "接受状态阶梯：每一级只承认自己那一级的证据", fontsize=13, color=INK, weight="bold")

    levels = [
        ("脚本批准", "SCRIPT_APPROVED_ONCE", "脚本版本 SHA + 批准范围", "#eef4fa"),
        ("执行许可", "APPROVED_ONCE", "合同范围 + 一次性许可", "#eef4fa"),
        ("机器检查", "technical_passed", "技术 / QC 凭据", "#f5f6f7"),
        ("用户接受", "ACCEPTED", "用户对确切 SHA 的明确决定", "#eef7f0"),
        ("对外发布", "RELEASED", "独立的发布授权与审核", "#fdf1f1"),
    ]
    x0, w, h, gap = 0.06, 0.30, 0.115, 0.035
    for i, (cn, code, ev, fill) in enumerate(levels):
        y = 0.70 - i * (h + gap)
        edge = OK if code == "ACCEPTED" else (BAD if code == "RELEASED" else LINE)
        box(ax, x0, y, w, h, f"{cn}\n{code}", edge=edge, fill=fill, size=10, weight="bold")
        ax.text(x0 + w + 0.03, y + h / 2, f"证据：{ev}", fontsize=9.5, color=INK, va="center")
        if i < len(levels) - 1:
            arrow(ax, (x0 + w / 2, y), (x0 + w / 2, y - gap), color=LINE)
        ax.add_patch(FancyArrowPatch((x0 + w + 0.02, y + h / 2), (x0 + w + 0.005, y + h / 2),
                                     arrowstyle="<|-|>", mutation_scale=10, lw=1.2,
                                     color=BAD, linestyle=(0, (3, 2))))

    ax.text(0.03, 0.11,
            "红色双向箭头 = 不可跳级：接受任一级都不自动解锁其上一级",
            fontsize=10, color=BAD, weight="bold")
    ax.text(0.03, 0.045,
            "例：静默母版被接受，不等于后期成片被接受，更不等于可以对外发布",
            fontsize=9.5, color=MUTED)
    save(fig, "02-acceptance-ladder.png")


def fig_timeline():
    """配音、字幕、音乐与镜头切点的对齐。"""
    fig, ax = canvas(11, 5.6)
    ax.text(0.03, 0.94, "时间轴对齐：字幕与旁白落在镜头切点上，音乐按需延展",
            fontsize=13, color=INK, weight="bold")

    cuts = [0, 3, 11, 16, 20, 24, 28, 32, 35]
    labels = ["A", "B", "C", "D1", "D2", "E1", "F1", "G", ""]

    def x_of(t):
        return 0.06 + (t / 35.0) * 0.90

    for i, c in enumerate(cuts):
        if c < 35:
            ax.plot([x_of(c), x_of(c)], [0.20, 0.86], color=LINE, lw=1, zorder=1)
            if labels[i]:
                ax.text(x_of(c), 0.885, labels[i], ha="center", fontsize=9, color=MUTED)

    bars = [
        (0.00, 2.63, "旁白句 1", 0.74, ACCENT),
        (3.00, 3.60, "句 2", 0.74, ACCENT),
        (11.00, 3.05, "句 3", 0.74, ACCENT),
        (16.00, 2.41, "句 4", 0.74, ACCENT),
        (20.00, 3.31, "句 5", 0.74, ACCENT),
        (24.00, 2.76, "句 6", 0.74, ACCENT),
        (28.00, 3.17, "句 7", 0.74, ACCENT),
        (32.00, 3.00, "句 8", 0.74, ACCENT),
    ]
    for s, e, name, y, c in bars:
        ax.add_patch(FancyBboxPatch((x_of(s), y), x_of(e) - x_of(s), 0.055,
                                    boxstyle="round,pad=0.0,rounding_size=0.006",
                                    linewidth=0, facecolor=c, alpha=0.85))
        ax.text((x_of(s) + x_of(e)) / 2, y + 0.028, name, ha="center", va="center",
                fontsize=8, color="white")

    ax.add_patch(FancyBboxPatch((x_of(0), 0.56), x_of(26.2) - x_of(0), 0.05,
                                boxstyle="round,pad=0.0,rounding_size=0.006",
                                linewidth=0, facecolor=OK, alpha=0.85))
    ax.text(x_of(26.2) + 0.012, 0.585, "音乐候选 26.2s", fontsize=9, color=OK, va="center")
    ax.add_patch(FancyBboxPatch((x_of(26.2), 0.56), x_of(35) - x_of(26.2), 0.05,
                                boxstyle="round,pad=0.0,rounding_size=0.006",
                                linewidth=0, facecolor=OK, alpha=0.35, hatch="///"))
    ax.text(x_of(26.2) + 0.012, 0.50, "循环延展段（须记录）", fontsize=8.5, color=OK, va="center")

    ax.add_patch(FancyBboxPatch((x_of(0), 0.36), x_of(35) - x_of(0), 0.05,
                                boxstyle="round,pad=0.0,rounding_size=0.006",
                                linewidth=0, facecolor=WARN, alpha=0.55))
    ax.text(x_of(35) + 0.012, 0.385, "旁白轨 0–35s", fontsize=9, color=WARN, va="center")

    for i in range(8):
        pass
    ax.text(0.06, 0.27, "硬门禁：字幕最后一条结束时间必须 ≤ 35.0s；越界要裁断并记录裁掉多少秒",
            fontsize=9.5, color=BAD)
    ax.text(0.06, 0.20, "硬门禁：音乐必须压在旁白之下，记录综合响度、平均电平与真峰值",
            fontsize=9.5, color=BAD)
    ax.text(0.06, 0.13, "硬门禁：末句若超出总时长，裁到边界并在 QC 写明，不得无声截断",
            fontsize=9.5, color=BAD)

    for t in [0, 5, 10, 15, 20, 25, 30, 35]:
        ax.text(x_of(t), 0.30, f"{t}s", ha="center", fontsize=8.5, color=MUTED)

    save(fig, "03-timeline-fit.png")


def fig_subtitle_check():
    """字幕可读性检查链。"""
    fig, ax = canvas(10.6, 5.4)
    ax.text(0.03, 0.94, "字幕可读性检查：技术全绿也可能一个字都读不出来",
            fontsize=13, color=INK, weight="bold")

    passes = ["编码参数正确", "时长与帧数正确", "全解码通过", "浏览器能播放"]
    ax.text(0.03, 0.80, "机器 QC 能证明的", fontsize=11, color=INK, weight="bold")
    for i, p in enumerate(passes):
        box(ax, 0.03 + i * 0.245, 0.68, 0.22, 0.09, p, edge=OK, fill="#f1f8f3", size=9)
        ax.text(0.14 + i * 0.245, 0.645, "PASS", ha="center", fontsize=9, color=OK, weight="bold")

    ax.text(0.03, 0.53, "机器 QC 证明不了的", fontsize=11, color=BAD, weight="bold")
    fails = ["字体是否含简体中文字形", "字幕是否被 BGM 盖住", "字幕位置是否挡关键画面"]
    for i, p in enumerate(fails):
        box(ax, 0.03 + i * 0.325, 0.40, 0.30, 0.09, p, edge=BAD, fill="#fdf1f1", size=9)
        ax.text(0.18 + i * 0.325, 0.365, "FAIL", ha="center", fontsize=9, color=BAD, weight="bold")

    ax.plot([0.03, 0.97], [0.28, 0.28], color=LINE, lw=1)
    ax.text(0.03, 0.20, "因此：烧录前验证字形，烧录后必须抽帧目视检查。",
            fontsize=11, color=INK, weight="bold")
    ax.text(0.03, 0.11,
            "记录字体文件路径与 SHA，避免换机器复现同样的方框字。",
            fontsize=9.5, color=MUTED)
    save(fig, "04-subtitle-check.png")


if __name__ == "__main__":
    fig_modes()
    fig_states()
    fig_timeline()
    fig_subtitle_check()
