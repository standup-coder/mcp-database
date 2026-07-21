# 📊 Google Sheets MCP

> 分类：技术 / 运维
> 适用场景：表格创建、读写、格式化、图表、批量数据处理

---

## 一、简介

Google Sheets MCP 把 Google Sheets API 暴露给 LLM。LLM 可以：
- 读 / 写单元格
- 创建 / 复制表格
- 批量操作
- 设置格式（颜色、字体、合并）
- 图表、命名范围
- 公式

适用：数据收集、报表、轻量 ETL、团队数据协作。

> 默认工具数：6

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 读 | 单元格 / 范围 / 整表 |
| 写 | 单元格 / 范围 / 批量 |
| 创建 | 表格 / 工作表 |
| 复制 | 整表 / 单 sheet |
| 格式 | 字体 / 颜色 / 数字格式 / 合并 |
| 图表 | 柱状 / 折线 / 饼图 |

---

## 三、配置

### 3.1 申请凭据

1. 打开 Google Cloud Console：<https://console.cloud.google.com/>
2. 创建项目 → 启用 **Google Sheets API** + **Google Drive API**
3. 配置 OAuth 同意屏幕
4. 创建 OAuth 2.0 客户端 ID（应用类型：桌面应用）
5. 下载凭据 → 重命名为 `credentials.json`

### 3.2 申请 Service Account（推荐，机器人场景）

1. IAM & Admin → Service Accounts → Create
2. 创建 Key（JSON 格式）→ 保存为 `service_account.json`
3. 把 Service Account 邮箱（`xxx@project.iam.gserviceaccount.com`）分享到目标表格（**编辑者**）

### 3.3 环境变量

```bash
# OAuth（用户场景）
GOOGLE_CREDENTIALS_PATH=./credentials.json
GOOGLE_TOKEN_PATH=./token.json

# Service Account（机器人场景，推荐）
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}

# 可选：默认表格 ID
# GOOGLE_DEFAULT_SHEET_ID=1BxiMVs0XRA...

# 可选：API base
# GOOGLE_API_BASE=https://sheets.googleapis.com
```

---

## 四、使用示例

### 4.1 读范围

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/read_range \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA...",
    "range": "Sheet1!A1:D10"
  }'
```

返回：

```json
{
  "values": [
    ["Name", "Age", "City"],
    ["Alice", "30", "Beijing"],
    ["Bob", "25", "Shanghai"]
  ]
}
```

### 4.2 写单元格

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/write_range \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA...",
    "range": "Sheet1!A1:C1",
    "values": [
      ["Name", "Age", "City"]
    ]
  }'
```

### 4.3 批量追加

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/append_rows \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA...",
    "range": "Sheet1!A1",
    "values": [
      ["Charlie", "28", "Shenzhen"],
      ["David", "35", "Guangzhou"]
    ]
  }'
```

### 4.4 格式化

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/format_range \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA...",
    "range": "Sheet1!A1:C1",
    "format": {
      "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
      "textFormat": {
        "bold": true,
        "foregroundColor": {"red": 1, "green": 1, "blue": 1}
      }
    }
  }'
```

### 4.5 创建表格

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/create_spreadsheet \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly Report - 2024-W37",
    "sheet_names": ["Summary", "Raw Data", "Charts"]
  }'
```

### 4.6 公式

```bash
curl -X POST http://localhost:8000/mcp/execute/google_sheets/write_formula \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1BxiMVs0XRA...",
    "range": "Sheet1!E1",
    "formula": "=SUM(B2:B100)"
  }'
```

---

## 五、典型使用流程

### 场景：每日订单数据从 DB 同步到 Sheets

```text
 Celery Beat       Database MCP      Google Sheets MCP       Sheets
  每天 23:00             │                  │                  │
     │   query orders   │                  │                  │
     │  last 24h       │                  │                  │
     ├─────────────────▶│                  │                  │
     │                  │  SELECT *       │                  │
     │                  │  FROM orders    │                  │
     │                  │                 │                  │
     │  1500 行        │                  │                  │
     │◀─────────────────┤                  │                  │
     │                  │                  │                  │
     │                  │  append_rows     │                  │
     │                  │  (1500 rows)    │                  │
     ├──────────────────┼─────────────────▶│                  │
     │                  │                  │  POST /values    │
     │                  │                  ├─────────────────▶│
     │                  │                  │  Range: Daily!A2 │
     │                  │                  │  1500 rows        │
     │                  │                  │◀─────────────────┤
     │                  │                  │                  │
     │  写图表公式       │                  │                  │
     │  =SUMIF(...)    │                  │                  │
     ├──────────────────┼─────────────────▶│                  │
     │                  │                  │                  │
     │  ✅ 同步完成     │                  │                  │
```

### 场景：Slack 问卷结果自动汇总

```text
 Slack 频道         Slack MCP         LLM        Google Sheets MCP
     │                 │                │                │
     │  调查问卷消息   │                │                │
     │  "1. A          │                │                │
     │   2. B          │                │                │
     │   3. C"        │                │                │
     │                 │  list_messages │                │
     ├────────────────▶│                │                │
     │                 │  50 条回复     │                │
     │                 │◀───────────────┤                │
     │                 │                │                │
     │                 │  解析统计     │                │
     │                 ├───────────────▶│                │
     │                 │                │  A: 20,        │
     │                 │                │  B: 25,        │
     │                 │                │  C: 5         │
     │                 │                │                │
     │                 │                │  write_range  │
     │                 │                │  [A, B, C,    │
     │                 │                │   20, 25, 5]  │
     │                 │                ├───────────────▶│
     │                 │                │                │
     │                 │                │  ✅ 写入完成   │
```

### 场景：报表协作

```text
 多个用户           Google Sheets MCP         Sheets 表格
   │                    │                        │
   │                    │                        │
   │  用户 A 写数据     │                        │
   ├───────────────────▶│  write_range           │
   │                    ├───────────────────────▶│
   │                    │                        │  Sheet1
   │                    │                        │
   │  用户 B 读数据     │                        │
   ├───────────────────▶│  read_range            │
   │                    ├───────────────────────▶│
   │                    │                        │
   │  用户 B 写公式     │                        │
   ├───────────────────▶│  write_formula         │
   │                    │  =SUM(B2:B100)         │
   │                    ├───────────────────────▶│
   │                    │                        │
   │  实时多人协作       │                        │
   │◀───────────────────┼────────────────────────┤
   │                    │  WebSocket 推送变更     │
```

---

## 六、注意事项

- **API 限流**：每用户 60 req/min；超大会触发 429
- **Service Account**：**没有邮箱 → 看不到表格**，必须先分享
- **OAuth 过期**：Token 1 小时过期，框架自动 refresh
- **公式**：写公式用 `USER_ENTERED` valueInputOption；写文本用 `RAW`
- **大批量**：单次请求上限 10000 单元格
- **历史数据**：Google Sheets 有完整版本历史，可回滚

---

## 七、对比 Excel Online

| 维度 | Google Sheets | Excel Online |
|------|---------------|--------------|
| **协作** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **公式** | Google 公式（接近 Excel） | Excel 全套 |
| **API** | ⭐⭐⭐⭐⭐ | Graph API 复杂 |
| **价格** | 免费 | 需 Office 365 |
| **集成** | 大量第三方 | 微软生态 |

> 选 Google Sheets 除非重度依赖 Excel 高级功能（数据透视、VBA）。

---

## 八、相关工具

- [Notion](./Notion.md) - 文档类内容用 Notion
- [Linear](./Linear.md) - 任务管理
- [Database](../后端/Database.md) - 数据源
- [E2B](../测试/E2B.md) - 数据预处理
