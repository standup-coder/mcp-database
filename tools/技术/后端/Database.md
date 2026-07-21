# 🗄️ Database MCP

> 分类：技术 / 后端
> 支持：MySQL / PostgreSQL / SQLite / Redis
> 适用场景：数据库查询、Schema 浏览、慢查询分析、运维巡检

---

## 一、简介

Database MCP 给 LLM 提供了**只读 + 受限**的数据库访问能力。LLM 可以：
- 列出表 / 字段 / 索引
- 跑 SELECT 查询
- 看执行计划
- 做数据采样分析

> ⚠️ 默认**只允许 SELECT**，DDL/DML 需显式开启。**生产环境慎用**！

> 默认工具数：7

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 列出数据库 | 当前连接实例的所有库 |
| 列出表 | 库下所有表（含注释、行数估算） |
| 描述 Schema | 字段、类型、索引、外键 |
| 执行 SQL | SELECT（默认）、可配置 DDL/DML |
| 执行计划 | EXPLAIN / EXPLAIN ANALYZE |
| 连接管理 | 多个数据源切换 |
| 慢查询 | 查慢日志（如果数据库开启） |

---

## 三、配置

### 3.1 环境变量（MySQL 示例）

```bash
# 数据源名称（支持多个）
DB_PRIMARY_TYPE=mysql               # mysql | postgresql | sqlite | redis
DB_PRIMARY_HOST=127.0.0.1
DB_PRIMARY_PORT=3306
DB_PRIMARY_USER=readonly
DB_PRIMARY_PASSWORD=your_password
DB_PRIMARY_DATABASE=mydb

# 第二个数据源（可选）
# DB_ANALYTICS_TYPE=postgresql
# DB_ANALYTICS_HOST=...
```

### 3.2 推荐建一个只读账号

```sql
-- MySQL
CREATE USER 'mcp_readonly'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON mydb.* TO 'mcp_readonly'@'%';
FLUSH PRIVILEGES;
```

```sql
-- PostgreSQL
CREATE USER mcp_readonly WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
```

### 3.3 安全配置

```bash
# 必填：禁止的危险关键字
DB_BLOCKED_KEYWORDS=DROP,DELETE,UPDATE,INSERT,TRUNCATE,ALTER,RENAME,GRANT,REVOKE

# 必填：单次返回行数上限
DB_MAX_ROWS=1000

# 必填：查询超时（秒）
DB_QUERY_TIMEOUT=30

# 必填：是否允许 DDL/DML
DB_ALLOW_WRITE=false                # 生产环境必须 false
```

---

## 四、使用示例

### 4.1 列出所有表

```bash
curl -X POST http://localhost:8000/mcp/execute/database/list_tables \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"connection": "primary"}'
```

### 4.2 查看表结构

```bash
curl -X POST http://localhost:8000/mcp/execute/database/describe_table \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connection": "primary",
    "table": "orders"
  }'
```

### 4.3 执行 SQL

```bash
curl -X POST http://localhost:8000/mcp/execute/database/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connection": "primary",
    "sql": "SELECT order_id, amount, created_at FROM orders WHERE created_at > NOW() - INTERVAL 7 DAY LIMIT 100"
  }'
```

### 4.4 看执行计划

```bash
curl -X POST http://localhost:8000/mcp/execute/database/explain \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connection": "primary",
    "sql": "SELECT * FROM orders WHERE user_id = 123"
  }'
```

### 4.5 Redis

```bash
# GET
curl -X POST http://localhost:8000/mcp/execute/database/redis_get \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connection": "primary",
    "key": "user:123:session"
  }'

# 列出 keys
curl -X POST http://localhost:8000/mcp/execute/database/redis_keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connection": "primary",
    "pattern": "user:*",
    "limit": 100
  }'
```

---

## 五、典型使用流程

### 场景：LLM 帮你排查慢查询

```text
 用户              LLM              Database MCP         MySQL
  │                 │                    │                │
  │ "订单查询很慢， │                    │                │
  │  帮看看"       │                    │                │
  ├────────────────▶│                    │                │
  │                 │  1. list_slow_queries              │
  │                 ├───────────────────▶│                │
  │                 │                    │  SHOW FULL     │
  │                 │                    │  PROCESSLIST   │
  │                 │                    ├───────────────▶│
  │                 │                    │◀───────────────┤
  │                 │  2. explain         │                │
  │                 │  SELECT * FROM orders WHERE user_id=?│
  │                 ├───────────────────▶│                │
  │                 │                    │  EXPLAIN       │
  │                 │                    ├───────────────▶│
  │                 │                    │◀───────────────┤
  │                 │  ❌ 全表扫描       │                │
  │                 │  建议加索引        │                │
  │                 │◀───────────────────┤                │
  │ "用户 ID 没索引，建联合索引 (user_id, created_at)"   │
  │◀────────────────┤                    │                │
```

### 场景：业务分析 — 月度订单统计

```text
 LLM            Database MCP         MySQL          输出
  │                  │                  │              │
  │ query 5 个 SQL   │                  │              │
  ├─────────────────▶│                  │              │
  │  1. 月活用户     │                  │              │
  │  2. 订单数       │                  │              │
  │  3. GMV         │                  │              │
  │  4. 退款率       │                  │              │
  │  5. Top 10 商品  │                  │              │
  │                  │  并发执行         │              │
  │                  ├─────────────────▶│              │
  │                  │◀─────────────────┤              │
  │  [{},{},{},{},{}] │                  │              │
  │◀─────────────────┤                  │              │
  │                                                │
  │  整理成 Markdown 表格                           │
  │  + 异常项标注 ⚠️                                │
```

---

## 六、安全红线

> ⚠️ **生产环境数据库接入 MCP，必须遵守以下规则：**

1. **只读账号** —— 不要用 root / 业务账号
2. **网络隔离** —— MCP 部署在堡垒区，不直接暴露公网
3. **审计日志** —— 记录所有 SQL，保留 90 天
4. **关键字过滤** —— 至少拦截 `DROP / DELETE / UPDATE / INSERT / TRUNCATE / ALTER`
5. **行数限制** —— `DB_MAX_ROWS` 防止误拖全表
6. **超时** —— `DB_QUERY_TIMEOUT` 防止慢查询占满连接池
7. **白名单** —— 只允许查指定的库（`DB_ALLOWED_DATABASES`）

---

## 六、注意事项

- **大表查询**：先 `EXPLAIN` 确认走索引，再跑
- **时区**：MySQL 的时区设置跟服务器一致；PostgreSQL 用 `AT TIME ZONE`
- **字符集**：连接串里务必带 `charset=utf8mb4`，避免 emoji 乱码
- **连接数**：每个 MCP 实例会建独立连接，注意 MySQL `max_connections` 配额
- **敏感数据**：返回结果中如有密码、身份证等敏感字段，建议在中间层脱敏

---

## 七、相关工具

- [HTTP Client](./HTTP-Client.md) - 通过 API 访问数据库托管平台（RDS / Cloud SQL）
- [Sentry](../测试/Sentry.md) - 慢查询可能是线上故障的征兆
- [E2B](../测试/E2B.md) - 跑数据分析脚本，避免在生产库跑大查询
