# 贡献指南

感谢您对MCP Commute Assistant项目的关注！我们欢迎任何形式的贡献。

## 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/your-username/mcp4coder.git
cd mcp4coder
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装开发依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置
```

### 5. 运行开发服务器

```bash
python -m app.main
```

## 代码规范

### Python代码风格

我们遵循PEP 8规范，使用以下工具进行代码质量检查：

```bash
# 代码格式化
black app/ tests/

# 代码检查
flake8 app/ tests/

# 类型检查
mypy app/
```

### 提交信息规范

请使用以下格式编写提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型:**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**示例:**
```
feat(commute): 添加批量路线检查功能

实现了同时检查多条通勤路线的功能，
支持自定义路线对和并发处理。

Closes #123
```

## 测试指南

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_config.py -v

# 运行特定测试类
pytest tests/test_config.py::TestSettings -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html tests/
```

### 编写测试

测试文件应该：

1. 遵循命名约定：`test_*.py`
2. 使用pytest框架
3. 包含充分的测试用例
4. 使用mock隔离外部依赖
5. 测试边界条件和异常情况

**测试示例:**

```python
import pytest
from unittest.mock import Mock, patch

class TestCommuteService:
    def test_successful_commute_check(self):
        """测试成功的通勤检查"""
        with patch('app.mcp.amap_client.AMAPClient') as mock_amap:
            mock_client = Mock()
            mock_client.calculate_route.return_value = Mock(
                distance=15000,
                duration=1800
            )
            mock_amap.return_value = mock_client
            
            # 执行测试
            service = CommuteService()
            result = service.check_route()
            
            # 验证结果
            assert result.distance == 15000
            assert result.duration == 1800
```

## Pull Request流程

### 1. Fork项目

在GitHub上fork本项目到您的账户。

### 2. 创建特性分支

```bash
git checkout -b feature/your-feature-name
```

### 3. 开发和测试

- 编写代码
- 添加测试
- 运行所有测试确保通过
- 更新相关文档

### 4. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 5. 推送到远程仓库

```bash
git push origin feature/your-feature-name
```

### 6. 创建Pull Request

在GitHub上创建PR，填写以下信息：

- 清晰的标题和描述
- 关联的Issue编号（如果有）
- 测试结果截图
- 变更的影响范围

## Issue报告指南

### Bug报告

请包含以下信息：

```
**描述**
清晰简洁地描述bug是什么

**重现步骤**
1. 转到 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**期望行为**
清楚地描述你期望发生什么

**截图**
如果适用，添加屏幕截图来帮助解释你的问题

**环境信息:**
 - 操作系统: [如 macOS 12.0]
 - 浏览器: [如 chrome, safari]
 - 版本: [如 22]

**附加信息**
在此处添加有关问题的任何其他信息
```

### 功能请求

```
**你的功能请求是否与问题相关？请描述。**
清晰简洁地描述问题是什么。例如：我总是感到沮丧，当[...]

**描述你想要的解决方案**
清晰简洁地描述你想要发生什么

**描述你考虑过的替代方案**
清晰简洁地描述你考虑的任何替代解决方案或功能

**附加信息**
在此处添加有关功能请求的任何其他信息或屏幕截图
```

## 代码审查标准

Pull Request需要满足以下标准才能合并：

### 必须满足
- [ ] 所有测试通过
- [ ] 代码覆盖率 ≥ 80%
- [ ] 符合代码风格规范
- [ ] 包含适当的测试
- [ ] 更新相关文档
- [ ] 通过CI/CD流水线

### 建议满足
- [ ] 性能影响评估
- [ ] 安全性审查
- [ ] 用户体验改进
- [ ] 向后兼容性检查

## 开发最佳实践

### 1. 架构原则

- **单一职责原则**: 每个类和函数只负责一项功能
- **开闭原则**: 对扩展开放，对修改关闭
- **依赖倒置**: 依赖抽象而非具体实现
- **接口隔离**: 使用小而专一的接口

### 2. 错误处理

```python
# 好的做法
try:
    result = await service.process_data()
except SpecificException as e:
    logger.error("处理数据失败", error=str(e))
    raise BusinessLogicError(f"数据处理失败: {str(e)}") from e

# 避免的做法
try:
    result = await service.process_data()
except Exception:
    pass  # 静默忽略错误
```

### 3. 日志记录

```python
# 使用结构化日志
logger.info(
    "用户登录成功",
    user_id=user.id,
    ip_address=request.client.host,
    login_time=datetime.now().isoformat()
)

# 避免字符串拼接
logger.info(f"用户{user.id}登录成功")  # 不推荐
```

### 4. 配置管理

```python
# 使用配置类
from app.config.settings import settings

if settings.is_development:
    # 开发环境配置
    pass
else:
    # 生产环境配置
    pass
```

## 社区行为准则

### 我们的承诺

为了营造开放友好的环境，我们作为贡献者和维护者承诺让参与项目的每个人都能免受骚扰，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、教育程度、社会经济地位、国籍、个人外表、种族、宗教或性认同和取向如何。

### 我们的标准

有助于创造积极环境的行为包括：

- 使用欢迎和包容的语言
- 尊重不同的观点和经历
- 优雅地接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同情

参与者不可接受的行为包括：

- 使用性化语言或图像，以及不受欢迎的性关注或挑逗
- 恐吓、骚扰、侮辱性/贬低性评论，以及人身攻击或政治攻击
- 公开或私下骚扰
- 发布他人的私人信息，如物理或电子地址，未经明确许可
- 其他在专业环境中不适当的行为

### 我们的责任

项目维护者负责澄清可接受行为的标准，并应对任何不当行为采取适当和公平的纠正措施。

项目维护者有权删除、编辑或拒绝与本行为准则不符的评论、提交、代码、维基编辑、问题和其他贡献，或暂时或永久禁止任何他们认为行为不当、威胁、冒犯或有害的贡献者。

### 范围

本行为准则适用于项目空间和公共场所代表项目时的个人。代表项目的方式包括使用官方项目电子邮件地址、通过官方社交媒体账户发布或在线或线下活动中担任指定代表。

### 执行

可以通过[插入联系方式]报告辱骂、骚扰或其他不可接受的行为。所有投诉都将得到审查和调查，并产生被认为必要和适合情况的回应。项目团队有义务对事件报告者保密。具体执行政策的更多细节可能会单独发布。

不真诚执行或遵守行为准则的项目维护者可能面临项目领导层其他成员确定的临时或永久性后果。

## 许可证

通过贡献代码，您同意您的贡献将根据项目的MIT许可证进行许可。

## 联系方式

- 项目Issue: [GitHub Issues](https://github.com/your-username/mcp4coder/issues)
- 邮件: standup.coder@example.com
- Discord: [邀请链接]

感谢您的贡献！ 🎉