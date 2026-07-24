#!/usr/bin/env python3
"""
build_index.py

基于 .env.quick.json 生成 tools/index.json 结构化索引。
供 IDE 插件、文档站、grep 类工具消费。

字段：
- id:        相对 TOOLS_DIR 路径（去 .md）
- name:      MCP 名称（文件名）
- category:  行业 / 技术-前端 / 技术-后端 / ...
- tags:      标签列表
- required_env: 必填环境变量数
- strong_env:   强烈建议环境变量数
- env_file:     引用路径
- path:      相对路径（去 .md）
- url:       完整 .md 路径
"""
import json
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
ENV_QUICK = TOOLS_DIR / ".env.quick.json"
OUT = TOOLS_DIR / "index.json"


# 标签映射（按分类）
TAGS_MAP = {
    "行业/地图导航/高德地图": ["导航", "路线", "通勤", "地理位置"],
    "行业/即时通讯/钉钉": ["通知", "群消息", "告警", "国内"],
    "行业/天气/天气": ["实时", "预报", "指数"],
    "行业/日程管理/日历": ["会议", "日程", "Google", "Outlook"],
    "技术/前端/Figma": ["设计", "UI", "协作"],
    "技术/前端/ReactBits": ["组件库", "动画", "React"],
    "技术/前端/Browser": ["Playwright", "截图", "爬虫", "E2E"],
    "技术/后端/Database": ["SQL", "MySQL", "PostgreSQL", "Redis", "只读"],
    "技术/后端/HTTP-Client": ["API", "REST", "SSRF防护"],
    "技术/后端/Desktop-Commander": ["Shell", "进程", "终端", "高权限"],
    "技术/知识库/Context7": ["库文档", "版本精确", "RAG"],
    "技术/知识库/Docfork": ["语义搜索", "跨库"],
    "技术/知识库/DeepWiki": ["Wiki", "Markdown", "抓取"],
    "技术/知识库/Memory": ["知识图谱", "实体", "持久化"],
    "技术/知识库/Sequential-Thinking": ["推理", "思维链", "CoT"],
    "技术/知识库/Brave-Search": ["搜索", "新闻", "隐私"],
    "技术/测试/E2B": ["沙箱", "代码执行", "Python", "JavaScript"],
    "技术/测试/Sentry": ["错误监控", "Issue", "APM"],
    "技术/运维/Filesystem": ["文件", "安全", "受限"],
    "技术/运维/Git": ["版本控制", "分支", "提交"],
    "技术/运维/GitHub": ["仓库", "PR", "Issue", "Actions"],
    "技术/运维/Slack": ["消息", "BlockKit", "海外"],
    "技术/运维/Notion": ["文档", "Database", "协作"],
    "技术/运维/Linear": ["Issue", "敏捷", "Sprint"],
    "技术/运维/Google-Sheets": ["表格", "数据", "协作"],
    "技术/运维/Composio": ["集成平台", "500+应用", "统一"],
}


def split_category(path_id: str) -> str:
    """从 id 推分类。'技术/前端/Figma' → '技术-前端'"""
    parts = path_id.split("/")
    if len(parts) == 1:
        return "其他"
    if parts[0] == "行业":
        # 行业/地图导航/高德地图 → 行业-地图导航
        return f"行业-{parts[1]}" if len(parts) >= 3 else f"行业-{parts[0]}"
    if parts[0] == "技术":
        return f"技术-{parts[1]}" if len(parts) >= 3 else f"技术-{parts[0]}"
    return parts[0]


def main():
    data = json.loads(ENV_QUICK.read_text(encoding="utf-8"))

    mcps = []
    for raw_id, vars_list in data.items():
        # raw_id 形如 "行业/地图导航/高德地图.md"，先归一化
        pid = raw_id[:-3] if raw_id.endswith(".md") else raw_id
        required = [v for v in vars_list if v["level"] == "REQUIRED"]
        strong = [v for v in vars_list if v["level"] == "STRONG"]
        optional = [v for v in vars_list if v["level"] == "OPTIONAL"]

        mcps.append({
            "id": pid,
            "name": pid.split("/")[-1],
            "category": split_category(pid),
            "tags": TAGS_MAP.get(pid, []),
            "path": pid,
            "url": pid + ".md",
            "required_env_count": len(required),
            "strong_env_count": len(strong),
            "optional_env_count": len(optional),
            "total_env_count": len(vars_list),
            "required_env_keys": [v["key"] for v in required],
            "strong_env_keys": [v["key"] for v in strong],
        })

    # 按分类分组
    by_category: dict[str, list] = {}
    for m in mcps:
        by_category.setdefault(m["category"], []).append(m["name"] + ".md")

    index = {
        "version": "1.0.0",
        "generated_by": "scripts/build_index.py",
        "source": ".env.quick.json",
        "total": len(mcps),
        "categories": {
            cat: {"count": len(items), "mcps": sorted(items)}
            for cat, items in sorted(by_category.items())
        },
        "mcps": mcps,
    }

    OUT.write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    print(f"✅ 已生成 {OUT}")
    print(f"   总数: {len(mcps)} 个 MCP")
    print(f"   分类: {len(by_category)} 个")
    print()
    print("=== 分类概览 ===")
    for cat in sorted(by_category.keys()):
        items = by_category[cat]
        print(f"  {cat:20s}  {len(items):2d}  {', '.join(sorted(items))}")


if __name__ == "__main__":
    main()
