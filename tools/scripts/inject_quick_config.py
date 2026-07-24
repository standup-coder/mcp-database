#!/usr/bin/env python3
"""
inject_quick_config.py

为每个 MCP 文档插入"## 快速配置"区块，从 .env.quick.json 读取数据。
- 已有该区块则替换
- 没有则在 "## 三、配置" 之前插入（如果存在），否则插在文件开头
"""
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = TOOLS_DIR / ".env.quick.json"


def render_block(vars_list: list) -> str:
    """渲染一个 .env 代码块 + 说明。"""
    required = [v for v in vars_list if v["level"] == "REQUIRED"]
    strong = [v for v in vars_list if v["level"] == "STRONG"]
    optional = [v for v in vars_list if v["level"] == "OPTIONAL"]

    lines = ["## 快速配置", ""]
    lines.append("> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。")
    lines.append(">")
    lines.append("> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选")
    lines.append("")

    if required:
        lines.append("### 必填")
        lines.append("")
        lines.append("```bash")
        for v in required:
            note = f"  # {v['note']}" if v.get("note") else ""
            lines.append(f"{v['key']}={v['sample']}{note}")
        lines.append("```")
        lines.append("")

    if strong:
        lines.append("### 强烈建议（生产环境）")
        lines.append("")
        lines.append("```bash")
        for v in strong:
            note = f"  # {v['note']}" if v.get("note") else ""
            lines.append(f"{v['key']}={v['sample']}{note}")
        lines.append("```")
        lines.append("")

    if optional:
        lines.append("### 可选")
        lines.append("")
        lines.append("```bash")
        for v in optional:
            note = f"  # {v['note']}" if v.get("note") else ""
            lines.append(f"{v['key']}={v['sample']}{note}")
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def inject(md_path: Path, block: str) -> bool:
    """把区块插进 md 文件，返回是否变更。"""
    text = md_path.read_text(encoding="utf-8")

    # 1) 已存在 → 替换
    pattern = re.compile(r"## 快速配置[\s\S]*?(?=\n## |\Z)", re.MULTILINE)
    if pattern.search(text):
        new_text = pattern.sub(block.strip() + "\n\n", text, count=1)
        if new_text != text:
            md_path.write_text(new_text, encoding="utf-8")
            return True
        return False

    # 2) 找 "## 三、配置" 前面插入
    marker = re.compile(r"^## 三、配置", re.MULTILINE)
    m = marker.search(text)
    if m:
        new_text = text[: m.start()] + block + "\n---\n\n" + text[m.start():]
        md_path.write_text(new_text, encoding="utf-8")
        return True

    # 3) 兜底：插在 "## 二、核心能力" 后 / "## 一、简介" 后
    fallback = re.compile(r"^## (一、简介|一、简介|## 简介)", re.MULTILINE)
    m = fallback.search(text)
    if m:
        # 找到这个二级标题结束的下一个二级标题
        next_h2 = re.compile(r"^## ", re.MULTILINE)
        starts = [s.start() for s in next_h2.finditer(text)]
        section_start = m.start()
        section_end = next((s for s in starts if s > section_start), len(text))
        new_text = text[:section_end] + "\n" + block + "\n---\n\n" + text[section_end:]
        md_path.write_text(new_text, encoding="utf-8")
        return True

    return False


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    changed = 0
    skipped = 0
    for rel, vars_list in data.items():
        md_path = TOOLS_DIR / rel
        if not md_path.exists():
            print(f"  ❌ missing: {rel}")
            continue
        block = render_block(vars_list)
        if inject(md_path, block):
            n_req = sum(1 for v in vars_list if v["level"] == "REQUIRED")
            n_str = sum(1 for v in vars_list if v["level"] == "STRONG")
            n_opt = sum(1 for v in vars_list if v["level"] == "OPTIONAL")
            print(f"  ✅ {rel}  (R:{n_req} S:{n_str} O:{n_opt})")
            changed += 1
        else:
            skipped += 1

    print(f"\n=== 完成：变更 {changed} 个文件，跳过 {skipped} 个 ===")


if __name__ == "__main__":
    main()
