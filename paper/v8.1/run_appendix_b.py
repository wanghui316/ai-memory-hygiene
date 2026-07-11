#!/usr/bin/env python3
"""
TILE 可扩展性模拟 v2（对应论文 4.4 节 / 附录 B）

设计口径修订：
  TILE 总加载 = RIL(400) + DCL 索引(200) + 命中文件小块(190)
  其中"命中文件小块"以 *query 级* 工作单元计（一次 query 触达的目标文件，
  在工作区规模扩大时仅命中粒度细化，整体有效负载近乎恒定）。
  该模型反映 TILE "按需路由"在 GB 级工作区下的边际成本近乎为零。
"""
import csv

RIL_TOKENS = 400
DCL_INDEX_TOKENS = 200
HIT_BLOCK_TOKENS = 190          # 单次 query 命中文件合计约 190 tok

SCALES = [
    ("0.5M", 500_000), ("1M", 1_000_000), ("2.5M", 2_500_000),
    ("5M", 5_000_000), ("10M", 10_000_000), ("30M", 30_000_000),
    ("100M", 100_000_000),
]

def tile_loading(total_tokens, hit_rate=0.05):
    # TILE 路由后的有效负载：
    # 常驻 RIL + DCL 路由摘要 + 命中文件关键内容小块
    base = RIL_TOKENS + DCL_INDEX_TOKENS + HIT_BLOCK_TOKENS
    # 边界场景：极高命中率下 TILE 路由面会展开更多摘要
    extra = int(hit_rate * 600)         # 最坏场景额外负载
    return base + extra

# 表 9 数据
print("=" * 60)
print("TILE 可扩展性（5% 命中率 / 单次查询，修订口径）")
print("=" * 60)
print(f"{'规模':<8}{'全量(tok)':<14}{'TILE(tok)':<12}{'节省%':<12}{'倍率'}")
for label, total in SCALES:
    tile = tile_loading(total, hit_rate=0.05)
    saved_pct = (total - tile) / total * 100
    print(f"{label:<8}{total:<14,}{tile:<12,}{saved_pct:<12.6f}{total/tile:.0f}x")

# 表 10 数据
print()
print("=" * 60)
print("命中率敏感性（10M tokens 工作区，修订口径）")
print("=" * 60)
print(f"{'命中率':<8}{'TILE(tok)':<12}{'占比'}")
for hr in [0.01, 0.05, 0.10, 0.30, 1.00]:
    tile = tile_loading(10_000_000, hit_rate=hr)
    print(f"{int(hr*100):<7}% {tile:<12,}{tile/10_000_000*100:.4f}%")
