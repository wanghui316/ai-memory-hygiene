#!/usr/bin/env python3
"""
TILE 论文 v8.0 图 1 / 图 2 重渲染
图 1：现有路径总览（树状 + 总结框）
图 2：三层架构总览（堆叠带指针箭头）
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib

matplotlib.rcParams['axes.unicode_minus'] = False
try:
    matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanZen Hei', 'SimHei', 'DejaVu Sans']
except Exception:
    pass

OUT_DIR = '/home/ubuntu/.openclaw/workspace/knowledge-base/论文图表/'
os.makedirs(OUT_DIR, exist_ok=True)

# =============================================================
# 图 1：现有路径总览
# =============================================================
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=160)
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')

# 顶部总框
top_box = FancyBboxPatch((3, 6.6), 6, 1.0,
                         boxstyle="round,pad=0.04",
                         linewidth=1.5, edgecolor='#333',
                         facecolor='#e8eaed')
ax.add_patch(top_box)
ax.text(6, 7.1, '大模型专业化开发现有路径总览\n（以优化对象维度划分）',
        ha='center', va='center', fontsize=12, fontweight='bold', color='#333')

# 主连线（向下分叉）
ax.plot([6, 6], [6.5, 5.7], color='#666', lw=1.5)
ax.plot([2, 10], [5.7, 5.7], color='#666', lw=1.5)
ax.plot([2, 2], [5.7, 5.0], color='#666', lw=1.5)
ax.plot([6, 6], [5.7, 5.0], color='#666', lw=1.5)
ax.plot([10, 10], [5.7, 5.0], color='#666', lw=1.5)

# 三个分块标题
def sub_block(x, y, w, h, title, body, ref, color):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.03",
                         linewidth=1.2, edgecolor='#333',
                         facecolor=color)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.30, title,
            ha='center', va='center', fontsize=10.5, fontweight='bold')
    ax.text(x + w/2, y + h/2 + 0.1, body,
            ha='center', va='center', fontsize=8.5)
    ax.text(x + w/2, y + 0.30, ref,
            ha='center', va='center', fontsize=8, color='#666', style='italic')

sub_block(0.3, 3.4, 3.4, 1.6,
          '路径一：模型蒸馏 (Distillation)',
          '优化对象：参数\n核心：教师→学生\n规模：缩参数',
          '代表工作：[8][9][10][11]',
          '#fce8e6')
sub_block(4.3, 3.4, 3.4, 1.6,
          '路径二：参数高效微调 (PEFT)',
          '优化对象：参数\n核心：冻结+适配器\n规模：加适配',
          '代表工作：[7][12][13]',
          '#e6f4ea')
sub_block(8.3, 3.4, 3.4, 1.6,
          '路径三：检索增强 (RAG)',
          '优化对象：知识源\n核心：检索+生成\n规模：扩知识',
          '代表工作：[5][6][19]',
          '#e8f0fe')

# 三个分块向"共性局限"汇聚
for x in [2, 6, 10]:
    ax.plot([x, 6], [3.4, 2.7], color='#666', lw=1.5)
ax.plot([6, 6], [2.4, 1.7], color='#666', lw=1.5)

# 底层共性局限
bottom_box = FancyBboxPatch((2.5, 0.4), 7, 1.3,
                            boxstyle="round,pad=0.04",
                            linewidth=1.5, edgecolor='#d93025',
                            facecolor='#fef7e0')
ax.add_patch(bottom_box)
ax.text(6, 1.4, '共性局限',
        ha='center', va='center', fontsize=11, fontweight='bold', color='#d93025')
ax.text(6, 0.85,
        '① 适用性受限（专业背景与算力门槛）  '
        '② 训练信号稀释（语料未结构化）  '
        '③ 时效性保障缺失',
        ha='center', va='center', fontsize=9, color='#333')

ax.text(6, 0.15, '图 1  大模型专业化开发现有路径总体视图',
        ha='center', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig1_paths_overview.png'), bbox_inches='tight')
plt.close(fig)
print('[OK] fig1 ->', os.path.join(OUT_DIR, 'fig1_paths_overview.png'))


# =============================================================
# 图 2：三层架构总览
# =============================================================
fig, ax = plt.subplots(figsize=(11, 7), dpi=160)
ax.set_xlim(0, 11)
ax.set_ylim(0, 9)
ax.axis('off')

# 用户查询入口
query_box = FancyBboxPatch((4.0, 8.0), 3, 0.7,
                           boxstyle="round,pad=0.04",
                           linewidth=1.2, edgecolor='#333',
                           facecolor='#fff3e0')
ax.add_patch(query_box)
ax.text(5.5, 8.35, '用户查询 Q',
        ha='center', va='center', fontsize=11, fontweight='bold')
ax.annotate('', xy=(5.5, 7.5), xytext=(5.5, 8.0),
            arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))

# Layer 1: RIL
l1 = FancyBboxPatch((0.8, 5.7), 9.4, 1.6,
                    boxstyle="round,pad=0.05",
                    linewidth=1.3, edgecolor='#1a73e8',
                    facecolor='#e8f0fe')
ax.add_patch(l1)
ax.text(0.8, 7.05, 'Layer 1: RIL — 常驻索引层 (≤ 400 tokens)',
        ha='left', va='center', fontsize=11.5, fontweight='bold', color='#1a73e8')
ril_lines = [
    '· 身份与长期规则元组',
    '· 领域路由表：B = RouteToDomain(Q)',
    '· 全局策略：时效阈值、加载阈值',
]
for i, line in enumerate(ril_lines):
    ax.text(1.2, 6.65 - i*0.3, line, ha='left', va='center', fontsize=9.5)

ax.annotate('', xy=(5.5, 4.95), xytext=(5.5, 5.7),
            arrowprops=dict(arrowstyle='->', color='#1a73e8', lw=1.8))
ax.text(5.7, 5.30, '一次指针解引用 (O(1))', ha='left', va='center',
        fontsize=9, color='#1a73e8', style='italic')

# Layer 2: DCL
l2 = FancyBboxPatch((0.8, 3.0), 9.4, 1.9,
                    boxstyle="round,pad=0.05",
                    linewidth=1.3, edgecolor='#1a73e8',
                    facecolor='#e6f4ea')
ax.add_patch(l2)
ax.text(0.8, 4.65, 'Layer 2: DCL — 领域内容层',
        ha='left', va='center', fontsize=11.5, fontweight='bold', color='#1a73e8')

# DCL 三块子域
for x, name in [(1.2, '领域 A'), (4.6, '领域 B'), (8.0, '领域 A')]:
    sb = FancyBboxPatch((x, 3.15), 2.0, 1.20,
                        boxstyle="round,pad=0.03",
                        linewidth=1, edgecolor='#666',
                        facecolor='white')
    ax.add_patch(sb)
    ax.text(x + 1.0, 4.10, name, ha='center', va='center',
            fontsize=9.5, fontweight='bold')
    ax.text(x + 1.0, 3.78, '_index.md', ha='center', va='center',
            fontsize=8.5, fontfamily='monospace', color='#1a73e8')
    ax.text(x + 1.0, 3.42, '📁 📁 📁', ha='center', va='center', fontsize=10)

ax.annotate('', xy=(5.5, 2.25), xytext=(5.5, 3.0),
            arrowprops=dict(arrowstyle='->', color='#1a73e8', lw=1.8))
ax.text(5.7, 2.60, '二次指针解引用 (O(1))', ha='left', va='center',
        fontsize=9, color='#1a73e8', style='italic')

# Layer 3: EBL
l3 = FancyBboxPatch((0.8, 0.4), 9.4, 1.6,
                    boxstyle="round,pad=0.05",
                    linewidth=1.3, edgecolor='#9aa0a6',
                    facecolor='#f8f9fa')
ax.add_patch(l3)
ax.text(0.8, 1.75, 'Layer 3: EBL — 临时缓冲层',
        ha='left', va='center', fontsize=11.5, fontweight='bold', color='#5f6368')
ebl_lines = [
    '· 时间戳驱动自动清理',
    '· 与上层隔离，避免污染',
    '· 生命周期 ≤ 阈值 τ_ebl',
]
for i, line in enumerate(ebl_lines):
    ax.text(1.2, 1.35 - i*0.3, line, ha='left', va='center', fontsize=9.5, color='#5f6368')

ax.text(5.5, -0.05, '图 2  TILE 三层架构总体视图',
        ha='center', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'fig2_three_layers.png'), bbox_inches='tight')
plt.close(fig)
print('[OK] fig2 ->', os.path.join(OUT_DIR, 'fig2_three_layers.png'))

print('done')
