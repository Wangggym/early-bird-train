# 测试快速入门

## 🚀 快速开始

```bash
# 1. 安装依赖
source .venv/bin/activate
pip install -r requirements.txt

# 2. 运行所有测试
pytest

# 3. 查看覆盖率
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 📁 测试组织

```
tests/
├── conftest.py           # 全局 fixtures
├── fixtures/             # 测试数据和工具
│   └── mock_data.py     # Mock 数据
├── unit/                # 单元测试
│   ├── test_ticket_service.py  # ⭐ 重试机制测试
│   ├── test_scheduler.py       # ⭐ 多日期调度测试
│   ├── test_crawler.py
│   ├── test_analyzer.py
│   └── test_notifier.py
└── integration/         # 集成测试（待添加）
```

## ⭐ 重点测试

### 1. 斐波那契退避重试

`test_ticket_service.py` 中测试重试机制：

```bash
# 运行重试相关测试
pytest tests/unit/test_ticket_service.py::TestFetchWithRetry -v
```

**测试场景**：
- ✅ 第1次成功（无需重试）
- ✅ 第3次成功（重试2次）
- ✅ 所有重试失败
- ✅ 斐波那契时间间隔验证

### 2. 多日期调度

`test_scheduler.py` 中测试多日期功能：

```bash
# 运行调度相关测试
pytest tests/unit/test_scheduler.py -v
```

**测试场景**：
- ✅ 单日期调度
- ✅ 多日期调度（周一、三、五）
- ✅ 工作日全覆盖
- ✅ 周末调度

## 🎯 常用命令

```bash
# 运行特定测试文件
pytest tests/unit/test_ticket_service.py

# 运行特定测试类
pytest tests/unit/test_ticket_service.py::TestTicketMonitorService

# 运行特定测试方法
pytest tests/unit/test_ticket_service.py::TestTicketMonitorService::test_monitor_ticket_success

# 显示打印输出
pytest -s

# 详细输出
pytest -v

# 并行运行（快速）
pytest -n auto

# 覆盖率报告
pytest --cov=src --cov-report=term-missing
```

## 📝 编写新测试

### 1. 使用现有 Fixtures

```python
def test_my_feature(mock_crawler, mock_analyzer, mock_notifier):
    """测试我的功能"""
    service = TicketMonitorService(
        crawler=mock_crawler,
        analyzer=mock_analyzer,
        notifier=mock_notifier,
    )
    # ... 测试逻辑
```

### 2. Mock 外部依赖

```python
from unittest.mock import patch

@patch("time.sleep")  # Mock sleep 避免等待
def test_with_retry(mock_sleep):
    # ... 测试逻辑
    assert mock_sleep.called
```

### 3. 测试异常

```python
import pytest

def test_error_handling():
    with pytest.raises(DomainException) as exc_info:
        # 触发异常的代码
        pass
    
    assert "error message" in str(exc_info.value)
```

## 💡 最佳实践

1. **快速运行**: 使用 Mock 避免真实网络请求
2. **独立测试**: 每个测试不依赖其他测试
3. **清晰命名**: 测试名称应该说明测试什么
4. **AAA模式**: Arrange（准备）→ Act（执行）→ Assert（断言）

## 📚 更多信息

详细文档请查看 [TESTING.md](../TESTING.md)

