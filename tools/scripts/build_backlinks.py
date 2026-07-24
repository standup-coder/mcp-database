#!/usr/bin/env python3
"""
build_backlinks.py

扫描 tools/ 下所有 MCP 文档的「相关工具」/「常见组合」/「组合」等小节中的相对链接，
建立反向索引（backlinks），并在每个文档末尾追加/更新"被以下 MCP 引用"区块。

用法：
    python3 scripts/build_backlinks.py          # 构建 + 写回所有文档
    python3 scripts/build_backlinks.py --dry    # 只构建不写
    python3 scripts/build_backlinks.py --stats  # 打印统计
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

TOOLS_DIR = Path(__file__).resolve().parent.parent
MARKER_START = "<!-- BACKLINKS START -->"
MARKER_END = "<!-- BACKLINKS END -->"

# 这些小节中的相对 .md 链接算"相关工具"链接
RELEVANT_SECTIONS = [
    "相关工具", "常见组合", "组合", "Related", "Related Tools",
    "对比", "Comparison", "对比其他", "替代",
]


def find_md_files() -> list[Path]:
    return sorted(TOOLS_DIR.rglob("*.md"))


def extract_name(md_path: Path) -> str:
    """从文件名取 MCP 名称。Figma.md → Figma; 高德地图.md → 高德地图"""
    return md_path.stem


def path_id(md_path: Path) -> str:
    """唯一标识 = 相对 TOOLS_DIR 的路径，去后缀"""
    return str(md_path.relative_to(TOOLS_DIR)).rsplit(".", 1)[0]


def find_links_to(text: str, src_path: Path) -> set[str]:
    """提取 markdown 中形如 [text](./path/xxx.md) 或 (../path/xxx.md) 的相对链接，返回 id 集合"""
    # 先把 "## 相关工具" 等之后到下一个 ## 之间的内容截出来
    sections = []
    for sec_name in RELEVANT_SECTIONS:
        # 二级标题
        m = re.search(
            rf"^##\s+.*?{re.escape(sec_name)}.*$",
            text,
            re.MULTILINE,
        )
        if not m:
            continue
        start = m.end()
        # 找下一个 ## 标题
        nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
        end = start + nxt.start() if nxt else len(text)
        sections.append(text[start:end])

    if not sections:
        return set()

    relevant = "\n".join(sections)
    # 抓相对 .md 链接（含 ./ 和 ../ 两种）
    found = set()
    src_dir = src_path.parent
    for m in re.finditer(r"\]\((\.\.?/[^)#]+\.md)(?:#[^)]*)?\)", relevant):
        rel = m.group(1)
        # 用 pathlib 解析相对路径
        resolved = (src_dir / rel).resolve()
        # 转回相对 TOOLS_DIR 的 id
        try:
            rel_to_tools = resolved.relative_to(TOOLS_DIR.resolve())
        except ValueError:
            continue
        target = str(rel_to_tools).rsplit(".", 1)[0]
        if target:
            found.add(target)
    return found


def build_index(files: list[Path]) -> dict[str, list[str]]:
    """建反向索引：target_id -> [source_id, ...]"""
    name_to_id = {extract_name(f): path_id(f) for f in files}
    # 也支持 "Figma" / "Figma.md" 这种别名
    idx: dict[str, set[str]] = defaultdict(set)

    for f in files:
        src_id = path_id(f)
        text = f.read_text(encoding="utf-8")
        targets = find_links_to(text, f)
        for t in targets:
            idx[t].add(src_id)
    return {k: sorted(v) for k, v in idx.items()}


def render_block(backlinks: list[str], name_to_id: dict[str, str]) -> str:
    if not backlinks:
        return ""
    lines = [
        MARKER_START,
        "",
        "## 🔗 被以下 MCP 引用",
        "",
        "> 反向链接自动生成（`scripts/build_backlinks.py`）。",
        "",
    ]
    for src_id in sorted(set(backlinks)):
        # src_id 形如 "技术/前端/ReactBits"
        mcp_name = src_id.split("/")[-1]
        lines.append(f"- [{mcp_name}]({src_id}.md)")
    lines.append("")
    lines.append(MARKER_END)
    return "\n".join(lines)


def inject(f: Path, block: str) -> bool:
    text = f.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(MARKER_START)}[\s\S]*?{re.escape(MARKER_END)}\n*",
        re.MULTILINE,
    )
    if pattern.search(text):
        if block:
            new_text = pattern.sub(block + "\n\n", text, count=1)
        else:
            # 没 backlinks，把整个区块删掉
            new_text = pattern.sub("", text, count=1)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            return True
        return False
    else:
        if block:
            new_text = text.rstrip() + "\n\n" + block + "\n"
            f.write_text(new_text, encoding="utf-8")
            return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="只构建不写")
    parser.add_argument("--stats", action="store_true", help="只打印统计")
    args = parser.parse_args()

    files = find_md_files()
    files = [f for f in files if f.name != "README.md"]
    name_to_id = {extract_name(f): path_id(f) for f in files}

    index = build_index(files)

    if args.stats:
        # 统计
        no_back = [path_id(f) for f in files if path_id(f) not in index]
        no_refs = [src for src, tgts in index.items() if not tgts]
        print(f"=== 反向链接统计 ===")
        print(f"MCP 总数:        {len(files)}")
        print(f"有反向引用的:    {len(files) - len(no_back)}")
        print(f"无反向引用的:    {len(no_back)}")
        if no_back:
            print(f"  → {', '.join(no_back)}")
        print()
        print(f"=== Top 10 最常被引用 ===")
        top = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for tid, srcs in top:
            print(f"  {tid}: 被 {len(srcs)} 个引用")
        return

    # 写回
    changed = 0
    for f in files:
        pid = path_id(f)
        backlinks = index.get(pid, [])
        block = render_block(backlinks, name_to_id)
        if args.dry:
            n = len(backlinks)
            print(f"  {pid}: 会被 {n} 个引用")
        else:
            if inject(f, block):
                changed += 1
                n = len(backlinks)
                print(f"  ✅ {pid} (refs: {n})")

    if not args.dry:
        print(f"\n=== 完成：更新 {changed} 个文件 ===")


if __name__ == "__main__":
    main()
