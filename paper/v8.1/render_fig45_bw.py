#!/usr/bin/env python3
"""
TILE 论文 v8.0 — 图 4 / 图 5 黑白重渲染（修复标题下移 + 不挡横坐标）
- 图标题在 axes 内、xlabel 下方（labelpad + bottom margin 加大）
- 均值参考线 + 一行合并说明（避免标签压柱体）
"""
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['axes.unicode_minus'] = False
try:
    matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanZen Hei', 'SimHei', 'DejaVu Sans']
except Exception:
    pass

OUT_DIR = '/home/ubuntu/.openclaw/workspace/knowledge-base/论文图表/'
os.makedirs(OUT_DIR, exist_ok=True)

GREY_DARK = '#222222'
GREY_MID = '#666666'
GREY_LINE = '#888888'
BLACK = '#000000'

# =============================================================
# 图 4：15 条 query 质量分对比柱状图
# =============================================================
queries = [f'Q{i}' for i in range(1, 16)]
v0  = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
v0p = [2,2,2,2,2,2,3,3,3,3,2,2,2,3,3]
v3  = [5,5,5,4,5,5,5,5,5,5,5,5,5,5,5]

x = np.arange(len(queries))
w = 0.27

fig, ax = plt.subplots(figsize=(13, 6.5), dpi=160)
b1 = ax.bar(x - w, v0,  width=w, label='V0  (350 tok)',
            color='#dcdcdc', edgecolor=BLACK, linewidth=1.2)
b2 = ax.bar(x,     v0p, width=w, label="V0' (950 tok)",
            color='#9a9a9a', edgecolor=BLACK, linewidth=0.7, hatch='...')
b3 = ax.bar(x + w, v3,  width=w, label='V3  (1,181 tok)',
            color='#2a2a2a', edgecolor=BLACK, linewidth=0.7)

ax.set_xlabel('Query 编号', color=BLACK, fontsize=11, labelpad=14)
ax.set_ylabel('质量分（1-5，李克特量表）', color=BLACK, fontsize=11, labelpad=8)
ax.set_xticks(x)
ax.set_xticklabels(queries)
ax.set_ylim(0, 5.6)
ax.set_yticks([0, 1, 2, 3, 4, 5])
ax.legend(loc='lower right', frameon=True, fontsize=10, framealpha=0.95,
          edgecolor=GREY_LINE)
ax.grid(axis='y', linestyle=':', alpha=0.35, color=GREY_LINE, linewidth=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(BLACK)
ax.spines['bottom'].set_color(BLACK)
ax.tick_params(colors=BLACK)

# 均值参考线（细虚线）
ax.axhline(4.93, color=GREY_MID, linestyle=(0, (3, 2)), alpha=0.6, linewidth=0.9)
ax.axhline(2.40, color=GREY_MID, linestyle=(0, (3, 2)), alpha=0.6, linewidth=0.9)
ax.axhline(1.00, color=GREY_MID, linestyle=(0, (3, 2)), alpha=0.6, linewidth=0.9)

# 均值说明（放在图顶部右下方，不压柱体）
ax.text(0.99, 0.97, '均值参考线：V3 = 4.93     V0\' = 2.40     V0 = 1.00',
        transform=ax.transAxes, fontsize=9, color=BLACK,
        ha='right', va='top', style='italic',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#fafafa',
                  edgecolor=GREY_LINE, linewidth=0.6, alpha=0.95))

# 图标题（axes 内、xlabel 下方，足够间距）
ax.text(0.5, -0.32, '图 4  15 条 query 质量分对比',
        transform=ax.transAxes,
        ha='center', va='top', fontsize=12, fontweight='bold', color=BLACK)

# 留足底部空间
plt.subplots_adjust(bottom=0.24, top=0.94, left=0.07, right=0.97)
fig.savefig(os.path.join(OUT_DIR, 'fig4_quality_bars.png'), bbox_inches='tight',
            facecolor='white')
plt.close(fig)
print('[OK] fig4 (灰度 + 标题下移)')


# =============================================================
# 图 5：帕累托边界
# =============================================================
fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=160)

points = [
    ('V0',  350, 1.00, '#d9d9d9'),
    ("V0'", 950, 2.40, '#888888'),
    ('V3',  1181, 4.93, '#2a2a2a'),
]
for name, tok, qual, c in points:
    ax.scatter(tok, qual, s=380, color=c, zorder=3, edgecolors=BLACK, linewidth=1.5)
    ax.annotate(f'{name}  ({tok} tok)\n质量 {qual:.2f}',
                xy=(tok, qual), xytext=(tok+50, qual-0.45),
                fontsize=11, color=BLACK,
                arrowprops=dict(arrowstyle='->', color=BLACK, lw=1))

xs = [p[1] for p in points]
ys = [p[2] for p in points]
ax.plot(xs, ys, '--', color=GREY_DARK, linewidth=1.2, zorder=2, alpha=0.9)
ax.text(700, 0.55, '帕累托前沿', color=GREY_DARK, fontsize=9, style='italic')

# 反事实点：浅灰填充 + 黑色粗虚边
ax.scatter(1181, 2.40, s=220, color='#bcbcbc', zorder=2,
           edgecolors=BLACK, linewidth=2.0, linestyle='--')
ax.annotate('同等 token\n若仅 V0\' 质量', xy=(1181, 2.40),
            xytext=(820, 3.6), fontsize=9, color=GREY_DARK,
            arrowprops=dict(arrowstyle='->', color=GREY_DARK, lw=0.9))

ax.set_xlabel('单次查询加载 token 数', color=BLACK, fontsize=11, labelpad=12)
ax.set_ylabel('质量分（均值）', color=BLACK, fontsize=11, labelpad=8)
ax.set_xlim(0, 1500)
ax.set_ylim(0, 5.6)
ax.set_xticks([350, 700, 950, 1181, 1500])
ax.set_xticklabels(['350', '700', '950', '1181', '1500'])
ax.grid(linestyle=':', alpha=0.35, color=GREY_LINE, linewidth=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(BLACK)
ax.spines['bottom'].set_color(BLACK)
ax.tick_params(colors=BLACK)

# 图标题下移
ax.text(0.5, -0.30, '图 5  三模式 token-质量 帕累托边界',
        transform=ax.transAxes,
        ha='center', va='top', fontsize=12, fontweight='bold', color=BLACK)

plt.subplots_adjust(bottom=0.24, top=0.96, left=0.10, right=0.97)
fig.savefig(os.path.join(OUT_DIR, 'fig5_pareto.png'), bbox_inches='tight',
            facecolor='white')
plt.close(fig)
print('[OK] fig5 (灰度 + 标题下移)')

print('done')
