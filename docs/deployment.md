# 部署文档

## 生产环境部署指南

### 系统要求

- Ubuntu 20.04 LTS 或 CentOS 8+
- Docker 20.10+
- Docker Compose 1.29+
- 2GB RAM minimum
- 10GB disk space

### 部署步骤

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将用户添加到docker组
sudo usermod -aG docker $USER
```

#### 2. 项目部署

```bash
# 克隆项目
git clone <repository-url> /opt/mcp-commute-assistant
cd /opt/mcp-commute-assistant

# 创建生产环境配置
cp .env.example .env.production
# 编辑配置文件，设置生产环境参数

# 构建并启动服务
docker-compose -f docker-compose.yml up -d --build

# 检查服务状态
docker-compose ps
```

#### 3. 反向代理配置 (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 4. SSL证书配置

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 监控和日志

#### 日志查看

```bash
# 查看应用日志
docker-compose logs -f app

# 查看Worker日志
docker-compose logs -f celery-worker

# 查看Beat日志
docker-compose logs -f celery-beat

# 查看Redis日志
docker-compose logs -f redis
```

#### 系统监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看CPU使用
top
```

### 备份和恢复

#### 数据备份

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/mcp-commute"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份配置文件
cp .env $BACKUP_DIR/.env.backup_$DATE

# 备份日志文件
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# 备份Redis数据（如果需要持久化）
docker exec mcp_redis redis-cli BGSAVE
docker cp mcp_redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

echo "Backup completed: $BACKUP_DIR"
```

#### 数据恢复

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
RESTORE_DIR="/opt/mcp-commute-assistant"

# 停止服务
docker-compose down

# 恢复配置文件
cp $BACKUP_FILE/.env.backup_* $RESTORE_DIR/.env

# 恢复日志（可选）
tar -xzf $BACKUP_FILE/logs_*.tar.gz -C $RESTORE_DIR/

# 恢复Redis数据（如果需要）
cp $BACKUP_FILE/redis_*.rdb /tmp/dump.rdb
docker cp /tmp/dump.rdb mcp_redis:/data/dump.rdb

# 启动服务
docker-compose up -d
```

### 故障排除

#### 常见问题

1. **服务无法启动**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep 8000
   
   # 查看详细错误日志
   docker-compose logs app
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis容器状态
   docker-compose ps redis
   
   # 测试Redis连接
   docker exec mcp_redis redis-cli ping
   ```

3. **定时任务不执行**
   ```bash
   # 检查Celery Beat状态
   docker-compose logs celery-beat
   
   # 手动测试任务
   docker exec mcp_app python -c "
   from app.workers.tasks import check_commute_and_notify
   result = check_commute_and_notify.delay()
   print(f'Task ID: {result.id}')
   "
   ```

#### 性能优化

```bash
# 调整Docker资源限制
# 在docker-compose.yml中添加:
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

# Redis性能调优
# 在docker-compose.yml中添加Redis配置:
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 安全加固

#### 防火墙配置

```bash
# UFW防火墙配置
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 8000  # 禁止直接访问应用端口
```

#### 容器安全

```bash
# 启用Docker内容信任
export DOCKER_CONTENT_TRUST=1

# 定期更新基础镜像
docker-compose pull
docker-compose up -d --build
```

### 升级维护

#### 版本升级流程

```bash
#!/bin/bash
# upgrade.sh

# 备份当前版本
./backup.sh

# 拉取最新代码
git pull origin main

# 更新依赖
docker-compose build --no-cache

# 平滑重启
docker-compose up -d --force-recreate

# 验证服务状态
sleep 30
curl -f http://localhost:8000/health || exit 1

echo "Upgrade completed successfully"
```

这样就完成了完整的Docker部署方案，包括生产环境部署、监控、备份恢复、故障排除等完整的内容。