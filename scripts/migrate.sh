#!/usr/bin/env bash
# migrate.sh - 一键迁移脚本（示例）
# 把混乱的 workspace/ 重构为分层结构
# 用法：bash migrate.sh

set -e

WORKSPACE="${1:-.}"
BACKUP_DIR="$WORKSPACE/backups/migration_$(date +%Y%m%d_%H%M%S)"

echo "📦 工作区：$WORKSPACE"
echo "📁 备份目录：$BACKUP_DIR"
echo ""

# Step 1: 备份旧的 MEMORY.md
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    mkdir -p "$BACKUP_DIR"
    cp "$WORKSPACE/MEMORY.md" "$BACKUP_DIR/MEMORY.md.bak"
    echo "✅ 已备份 MEMORY.md → $BACKUP_DIR/MEMORY.md.bak"
fi

# Step 2: 创建业务目录骨架
mkdir -p "$WORKSPACE/memory"
mkdir -p "$WORKSPACE/tmp"
mkdir -p "$WORKSPACE/work_records"
echo "✅ 已创建 memory/ tmp/ work_records/ 骨架"

# Step 3: 检查每个业务目录是否有 _index.md
echo ""
echo "🔍 检查业务目录的 _index.md："
for dir in "$WORKSPACE"/*/; do
    dirname=$(basename "$dir")
    # 跳过系统目录
    case "$dirname" in
        backups|skills|memory|tmp|work_records|examples|scripts|.git)
            continue
            ;;
    esac
    if [ -d "$dir" ] && [ ! -f "$dir/_index.md" ]; then
        echo "  ⚠️  $dirname/ 缺少 _index.md"
    elif [ -d "$dir" ] && [ -f "$dir/_index.md" ]; then
        echo "  ✅ $dirname/_index.md"
    fi
done

echo ""
echo "📋 迁移检查清单："
echo "  [ ] MEMORY.md ≤ 100 行"
echo "  [ ] 每个业务目录有 _index.md"
echo "  [ ] memory/_index.md 存在"
echo "  [ ] tmp/ 内容是否可清理"
echo "  [ ] work_records/_index.md 存在"
echo ""
echo "💡 建议：手动审查 MEMORY.md 内容，删除过时规则"
echo "💡 完成后参考 examples/ 目录填充 _index.md 模板"