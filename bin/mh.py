#!/usr/bin/env python3
"""
mh (memory-hygiene) — AI 记忆管理 CLI 工具

核心算法：Context Budget Analysis（上下文预算分析算法）
通过扫描工作区文件，量化评估记忆管理健康状况，给出优化建议。

用法:
  mh.py init      初始化工作区目录结构
  mh.py status    分析工作区健康状况
  mh.py check     检查约束违例
  mh.py index     更新 _index.md 导航文件
  mh.py prune     列出可清理的过期文件

规则参考: https://github.com/wanghui316/ai-memory-hygiene
"""

import os
import sys
import re
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# ============================================================
# 核心算法：Context Budget Analyzer
# ============================================================

class ContextBudgetAnalyzer:
    """
    上下文预算分析算法

    算法目标：
    量化评估 AI 工作区的记忆管理健康状况，在超出预设预算前预警。

    算法输入：
    - workspace_path: 工作区根目录路径

    算法输出：
    - TokenBudget: 各文件 token 估算值
    - ConstraintReport: 约束违例报告
    - OptimizationSuggestion: 优化建议列表
    - HealthScore: 0-100 的健康评分
    """

    # Token 估算系数
    CJK_CHAR_TOKENS = 1.8       # 中文字符平均 token 数
    ASCII_WORD_TOKENS = 1.3     # 英文单词平均 token 数
    CODE_LINE_TOKENS = 2.5      # 代码行平均 token 数
    TABLE_LINE_TOKENS = 4.0     # 表格行平均 token 数

    # 约束阈值（来自 ai-memory-hygiene 铁律）
    CONSTRAINTS = {
        'MEMORY.md_max_lines': 100,
        'MEMORY.md_max_tokens': 3000,
        'memory_file_max_lines': 30,
        'memory_file_max_tokens': 500,
        'index_md_max_lines': 50,
        'tmp_max_files': 20,
        'business_dir_max_depth': 4,
    }

    # 文件过期时间（天）
    EXPIRY_THRESHOLDS = {
        'tmp': 7,
        'memory': 30,
        'daily': 90,
    }

    # 优化建议权重
    SUGGESTION_WEIGHTS = {
        'MEMORY_OVERFLOW': 0.30,
        'MISSING_INDEX': 0.25,
        'TMP_OVERFLOW': 0.15,
        'EXPIRED_FILES': 0.15,
        'DEEP_NESTING': 0.10,
        'DUPLICATE_CONTENT': 0.05,
    }

    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path).resolve()
        if not self.workspace.exists():
            raise FileNotFoundError(f"工作区不存在: {workspace_path}")

    def scan(self):
        """执行全量扫描，返回分析报告"""
        report = {
            'workspace': str(self.workspace),
            'scan_time': datetime.now().isoformat(),
            'files': [],
            'constraints': [],
            'suggestions': [],
            'health_score': 0,
            'token_budget': {
                'total_tokens': 0,
                'mem_md_tokens': 0,
                'memory_dir_tokens': 0,
                'index_files_tokens': 0,
                'other_tokens': 0,
            },
            'directory_structure': {},
        }

        # 1. 遍历所有 .md 文件
        md_files = list(self.workspace.rglob('*.md'))
        md_files = [f for f in md_files if '.git' not in str(f.relative_to(self.workspace))]

        for f in md_files:
            rel = f.relative_to(self.workspace)
            info = self._analyze_file(f, rel)
            report['files'].append(info)
            report['token_budget']['total_tokens'] += info['estimated_tokens']

            # 按类别统计
            rel_str = str(rel)
            if rel_str == 'MEMORY.md':
                report['token_budget']['mem_md_tokens'] += info['estimated_tokens']
            elif rel_str.startswith('memory/'):
                report['token_budget']['memory_dir_tokens'] += info['estimated_tokens']
            elif '_index.md' in rel_str:
                report['token_budget']['index_files_tokens'] += info['estimated_tokens']
            else:
                report['token_budget']['other_tokens'] += info['estimated_tokens']

        # 2. 检查约束
        report['constraints'] = self._check_constraints(report)

        # 3. 生成优化建议
        report['suggestions'] = self._generate_suggestions(report)

        # 4. 计算健康评分
        report['health_score'] = self._compute_health_score(report)

        # 5. 构建目录结构
        report['directory_structure'] = self._build_tree()

        return report

    def _analyze_file(self, filepath, relpath):
        """分析单个文件：行数、token 估算、内容类型"""
        info = {
            'path': str(relpath),
            'size_bytes': filepath.stat().st_size,
            'lines': 0,
            'estimated_tokens': 0,
            'last_modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'is_index': '_index.md' in str(relpath),
            'is_memory_md': str(relpath) == 'MEMORY.md',
            'is_memory_dir': str(relpath).startswith('memory/'),
            'is_tmp': str(relpath).startswith('tmp/'),
            'age_days': 0,
        }

        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        info['lines'] = len(lines)

        # 计算文件年龄
        mtime = filepath.stat().st_mtime
        info['age_days'] = (time.time() - mtime) / 86400

        # --- 核心算法：Token 估算 ---
        # 方法：逐行分析，根据内容类型用不同系数
        code_block = False
        table_mode = False
        cjk_chars = 0
        ascii_words = 0
        code_lines = 0
        table_lines = 0

        for line in lines:
            stripped = line.strip()

            # 检测代码块
            if stripped.startswith('```'):
                code_block = not code_block
                continue

            # 检测表格行
            if stripped.startswith('|') and stripped.endswith('|'):
                table_lines += 1
                continue

            if code_block:
                code_lines += 1
                continue

            # 统计中文字符
            cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', stripped))
            cjk_chars += cjk

            # 统计英文单词
            words = len(re.findall(r'[a-zA-Z]+', stripped))
            ascii_words += words

        # 综合估算
        token_estimate = (
            cjk_chars * self.CJK_CHAR_TOKENS +
            ascii_words * self.ASCII_WORD_TOKENS +
            code_lines * self.CODE_LINE_TOKENS +
            table_lines * self.TABLE_LINE_TOKENS
        )

        info['estimated_tokens'] = max(1, round(token_estimate))
        info['cjk_chars'] = cjk_chars
        info['ascii_words'] = ascii_words
        info['code_lines'] = code_lines
        info['table_lines'] = table_lines

        return info

    def _check_constraints(self, report):
        """检查各项约束"""
        violations = []

        # 1. MEMORY.md 行数
        mem_file = next((f for f in report['files'] if f['is_memory_md']), None)
        if mem_file:
            if mem_file['lines'] > self.CONSTRAINTS['MEMORY.md_max_lines']:
                violations.append({
                    'type': 'MEMORY_OVERFLOW',
                    'severity': 'ERROR',
                    'message': f"MEMORY.md 行数 {mem_file['lines']} 超过上限 {self.CONSTRAINTS['MEMORY.md_max_lines']}",
                    'detail': f"需要精简 {mem_file['lines'] - self.CONSTRAINTS['MEMORY.md_max_lines']} 行"
                })
            if mem_file['estimated_tokens'] > self.CONSTRAINTS['MEMORY.md_max_tokens']:
                violations.append({
                    'type': 'MEMORY_TOKEN_OVERFLOW',
                    'severity': 'WARNING',
                    'message': f"MEMORY.md token 估算 {mem_file['estimated_tokens']} 超过上限 {self.CONSTRAINTS['MEMORY.md_max_tokens']}",
                })

        # 2. memory/ 目录文件行数
        for f in report['files']:
            if f['is_memory_dir'] and not f['is_index']:
                if f['lines'] > self.CONSTRAINTS['memory_file_max_lines']:
                    violations.append({
                        'type': 'MEMORY_FILE_OVERFLOW',
                        'severity': 'WARNING',
                        'message': f"{f['path']} 行数 {f['lines']} 超过 {self.CONSTRAINTS['memory_file_max_lines']} 行",
                    })

        # 3. 业务目录缺少 _index.md
        dirs_with_index = set()
        for f in report['files']:
            if f['is_index']:
                dirs_with_index.add(Path(f['path']).parent)

        business_dirs = set()
        for f in report['files']:
            p = Path(f['path'])
            if len(p.parts) >= 2 and p.parts[0] not in ('.git', 'memory', 'tmp', 'scripts', 'examples', 'backups'):
                business_dirs.add(p.parts[0])

        for d in business_dirs:
            if Path(d) not in dirs_with_index:
                violations.append({
                    'type': 'MISSING_INDEX',
                    'severity': 'WARNING',
                    'message': f"目录 {d}/ 缺少 _index.md",
                })

        # 4. tmp/ 文件数
        tmp_files = [f for f in report['files'] if f['is_tmp']]
        if len(tmp_files) > self.CONSTRAINTS['tmp_max_files']:
            violations.append({
                'type': 'TMP_OVERFLOW',
                'severity': 'WARNING',
                'message': f"tmp/ 目录有 {len(tmp_files)} 个文件，超过 {self.CONSTRAINTS['tmp_max_files']}",
            })

        # 5. 过期文件
        for f in report['files']:
            category = 'tmp' if f['is_tmp'] else 'memory' if f['is_memory_dir'] else None
            if category and category in self.EXPIRY_THRESHOLDS:
                if f['age_days'] > self.EXPIRY_THRESHOLDS[category]:
                    violations.append({
                        'type': 'EXPIRED_FILES',
                        'severity': 'INFO',
                        'message': f"{f['path']} 已存在 {f['age_days']:.0f} 天（建议清理）",
                    })

        return violations

    def _generate_suggestions(self, report):
        """基于扫描结果生成优化建议"""
        suggestions = []
        seen = set()

        for v in report['constraints']:
            key = v['type']
            if key not in seen:
                seen.add(key)
                suggestions.append({
                    'priority': 'HIGH' if v['severity'] == 'ERROR' else 'MEDIUM',
                    'action': self._get_action_for_type(key),
                    'detail': v['message'],
                })

        return suggestions

    def _get_action_for_type(self, vtype):
        actions = {
            'MEMORY_OVERFLOW': '精简 MEMORY.md：将变动数据移至业务目录，仅保留规则和索引',
            'MEMORY_TOKEN_OVERFLOW': '检查 MEMORY.md 中是否有冗余内容，移除非核心规则',
            'MEMORY_FILE_OVERFLOW': '将 memory/ 中过长的日记条目拆分为多个短文件',
            'MISSING_INDEX': '为业务目录创建 _index.md 导航文件',
            'TMP_OVERFLOW': '清理 tmp/ 目录中的过期临时文件',
            'EXPIRED_FILES': '删除或归档过期文件',
        }
        return actions.get(vtype, '审查并优化')

    def _compute_health_score(self, report):
        """计算健康评分 0-100"""
        score = 100.0
        total_weight = sum(self.SUGGESTION_WEIGHTS.values())
        violations = defaultdict(int)

        for v in report['constraints']:
            violations[v['type']] += 1
            severity_penalty = 20 if v['severity'] == 'ERROR' else 5 if v['severity'] == 'WARNING' else 2
            weight = self.SUGGESTION_WEIGHTS.get(v['type'], 0.1)
            score -= severity_penalty * weight * min(violations[v['type']], 3)

        # 奖励：有 _index.md 的目录比例
        total_dirs = 0
        indexed_dirs = 0
        for f in report['files']:
            if f['is_index']:
                indexed_dirs += 1
        dirs = set()
        for f in report['files']:
            p = Path(f['path'])
            if len(p.parts) >= 1:
                dirs.add(p.parent)
        total_dirs = len([d for d in dirs if str(d) != '.'])
        if total_dirs > 0:
            index_ratio = indexed_dirs / total_dirs
            score += 10 * index_ratio

        return max(0, min(100, round(score)))

    def _build_tree(self):
        """生成目录树结构"""
        tree = {}
        for f in self.workspace.rglob('*.md'):
            if '.git' in str(f):
                continue
            parts = f.relative_to(self.workspace).parts
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = 'file'
        return tree


# ============================================================
# CLI 命令实现
# ============================================================

def cmd_init(args):
    """初始化工作区目录结构"""
    ws = Path(args.dir)
    if not ws.exists():
        print(f"❌ 目录不存在: {args.dir}")
        return 1

    dirs = ['trading', 'research', 'memory', 'tmp', 'work_records']
    for d in dirs:
        (ws / d).mkdir(exist_ok=True)
        # 创建 .gitkeep
        (ws / d / '.gitkeep').write_text('')

    # 创建 memory/_index.md
    index_path = ws / 'memory' / '_index.md'
    if not index_path.exists():
        index_path.write_text(f"""# 日记索引

## 最新
- 今日：`YYYY-MM-DD.md`
- 详见各业务目录的 `_index.md`

## 规范
- 每个文件 ≤ 30 行
- 只写索引，不写详情
""")

    print(f"✅ 已初始化工作区: {ws}")
    print(f"   创建目录: {', '.join(dirs)}")
    print(f"   提示：将你的业务数据移入对应的目录")
    return 0


def cmd_status(args):
    """分析工作区健康状况"""
    analyzer = ContextBudgetAnalyzer(args.dir)
    report = analyzer.scan()

    # ASCII 仪表盘
    score = report['health_score']
    bar_len = 30
    filled = int(bar_len * score / 100)

    print("=" * 50)
    print(f"🧠  AI 记忆管理健康报告")
    print(f"📂  工作区: {report['workspace']}")
    print(f"🕐  扫描时间: {report['scan_time']}")
    print()
    print(f"📊  健康评分: {score}/100")
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"    [{bar}]")
    print()

    # Token 预算
    tb = report['token_budget']
    print(f"📝  Token 预算估算:")
    print(f"    MEMORY.md:        {tb['mem_md_tokens']:>8} tokens")
    print(f"    memory/ 日记目录: {tb['memory_dir_tokens']:>8} tokens")
    print(f"    _index.md 导航:   {tb['index_files_tokens']:>8} tokens")
    print(f"    其他文件:         {tb['other_tokens']:>8} tokens")
    print(f"    ─────────────────────────────")
    print(f"    总计:             {tb['total_tokens']:>8} tokens")
    print()

    # 大文件 Top 5
    sorted_files = sorted(report['files'], key=lambda x: x['estimated_tokens'], reverse=True)
    print(f"📄  最大文件 Top 5:")
    for f in sorted_files[:5]:
        print(f"    {f['path']:<40} {f['estimated_tokens']:>6} tokens ({f['lines']} 行)")

    # 约束违例
    if report['constraints']:
        print()
        print(f"⚠️  发现 {len(report['constraints'])} 个问题:")
        for v in report['constraints'][:10]:
            icon = '🔴' if v['severity'] == 'ERROR' else '🟡' if v['severity'] == 'WARNING' else '🔵'
            print(f"    {icon} {v['message']}")

    # 建议
    if report['suggestions']:
        print()
        print(f"💡  优化建议:")
        for s in report['suggestions']:
            p = '⬆' if s['priority'] == 'HIGH' else '➡'
            print(f"    {p} {s['action']}")

    return 0


def cmd_check(args):
    """检查约束违例，JSON 输出"""
    analyzer = ContextBudgetAnalyzer(args.dir)
    report = analyzer.scan()

    if args.json:
        print(json.dumps(report['constraints'], ensure_ascii=False, indent=2))
    else:
        errors = [v for v in report['constraints'] if v['severity'] == 'ERROR']
        warnings = [v for v in report['constraints'] if v['severity'] == 'WARNING']

        if errors:
            print(f"🔴 {len(errors)} 个错误:")
            for e in errors:
                print(f"   {e['message']}")
        if warnings:
            print(f"🟡 {len(warnings)} 个警告:")
            for w in warnings:
                print(f"   {w['message']}")
        if not errors and not warnings:
            print("✅ 所有检查通过")
            print(f"   健康评分: {report['health_score']}/100")

    return 1 if any(v['severity'] == 'ERROR' for v in report['constraints']) else 0


def cmd_index(args):
    """更新指定目录的 _index.md"""
    target = Path(args.dir)
    if not target.is_dir():
        print(f"❌ 不是目录: {args.dir}")
        return 1

    # 收集该目录下的文件
    files = []
    for f in sorted(target.glob('*.md')):
        if f.name == '_index.md':
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d')
        size = f.stat().st_size
        files.append((mtime, f.name, size))

    if not files:
        print(f"📭  {target} 下没有 .md 文件")
        return 0

    # 生成 _index.md
    lines = [f"# {target.name} 目录索引\n"]
    lines.append(f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append("## 最新文件\n")
    for mtime, name, size in reversed(files[-5:]):
        kb = size / 1024
        lines.append(f"- `{name}` ({mtime}, {kb:.1f}KB)")
    lines.append("\n## 全部文件\n")
    for mtime, name, size in reversed(files):
        kb = size / 1024
        lines.append(f"- `{name}` ({mtime}, {kb:.1f}KB)")

    index_path = target / '_index.md'
    index_path.write_text('\n'.join(lines) + '\n')
    print(f"✅ 已生成: {index_path}")
    print(f"   包含 {len(files)} 个文件")

    return 0


def cmd_prune(args):
    """列出可清理的文件"""
    analyzer = ContextBudgetAnalyzer(args.dir)
    report = analyzer.scan()

    # 找出过期文件和可清理的
    removable = []
    for f in report['files']:
        if f['is_tmp'] and f['age_days'] > analyzer.EXPIRY_THRESHOLDS['tmp']:
            removable.append(f)
        elif f['is_memory_dir'] and not f['is_index'] and f['age_days'] > analyzer.EXPIRY_THRESHOLDS['memory']:
            removable.append(f)

    if not removable:
        print("✅ 没有需要清理的文件")
        return 0

    total_size = sum(f['size_bytes'] for f in removable)
    print(f"📦 可清理 {len(removable)} 个文件 ({total_size / 1024:.1f}KB)")
    print(f"   使用 --dry-run 预览，--execute 执行删除")
    for f in removable:
        age = f['age_days']
        size = f['size_bytes'] / 1024
        print(f"   {f['path']:<50} {size:>6.1f}KB ({age:.0f}天)")

    return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='mh — AI 记忆管理 CLI 工具',
        epilog='详细文档: https://github.com/wanghui316/ai-memory-hygiene'
    )
    parser.add_argument('--dir', '-d', default='.', help='工作区目录（默认当前目录）')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出（仅 check 命令）')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init
    p_init = subparsers.add_parser('init', help='初始化工作区目录结构')

    # status
    p_status = subparsers.add_parser('status', help='分析工作区健康状况')

    # check
    p_check = subparsers.add_parser('check', help='检查约束违例')

    # index
    p_index = subparsers.add_parser('index', help='更新 _index.md 导航文件')

    # prune
    p_prune = subparsers.add_parser('prune', help='列出可清理的文件')

    args = parser.parse_args()

    if args.command == 'init':
        return cmd_init(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'check':
        return cmd_check(args)
    elif args.command == 'index':
        return cmd_index(args)
    elif args.command == 'prune':
        return cmd_prune(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
