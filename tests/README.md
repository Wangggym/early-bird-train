# Testing Quick Start

## 🚀 Quick Start

```bash
# 1. Install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run all tests
pytest

# 3. View coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 📁 Test Organization

```
tests/
├── conftest.py           # Global fixtures
├── fixtures/             # Test data and utilities
│   └── mock_data.py     # Mock data
├── unit/                # Unit tests
│   ├── test_ticket_service.py  # ⭐ Retry mechanism tests
│   ├── test_scheduler.py       # ⭐ Multi-date scheduling tests
│   ├── test_crawler.py
│   ├── test_analyzer.py
│   └── test_notifier.py
└── integration/         # Integration tests (to be added)
```

## ⭐ Key Tests

### 1. Fibonacci Backoff Retry

`test_ticket_service.py` tests retry mechanism:

```bash
# Run retry-related tests
pytest tests/unit/test_ticket_service.py::TestFetchWithRetry -v
```

**Test Scenarios**:
- ✅ First attempt succeeds (no retry)
- ✅ Third attempt succeeds (2 retries)
- ✅ All retries fail
- ✅ Fibonacci time interval validation

### 2. Multi-date Scheduling

`test_scheduler.py` tests multi-date functionality:

```bash
# Run scheduling-related tests
pytest tests/unit/test_scheduler.py -v
```

**Test Scenarios**:
- ✅ Single date scheduling
- ✅ Multi-date scheduling (Monday, Wednesday, Friday)
- ✅ All weekdays coverage
- ✅ Weekend scheduling

## 🎯 Common Commands

```bash
# Run specific test file
pytest tests/unit/test_ticket_service.py

# Run specific test class
pytest tests/unit/test_ticket_service.py::TestTicketMonitorService

# Run specific test method
pytest tests/unit/test_ticket_service.py::TestTicketMonitorService::test_monitor_ticket_success

# Show print output
pytest -s

# Verbose output
pytest -v

# Run in parallel (fast)
pytest -n auto

# Coverage report
pytest --cov=src --cov-report=term-missing
```

## 📝 Writing New Tests

### 1. Use Existing Fixtures

```python
def test_my_feature(mock_crawler, mock_analyzer, mock_notifier):
    """Test my feature"""
    service = TicketMonitorService(
        crawler=mock_crawler,
        analyzer=mock_analyzer,
        notifier=mock_notifier,
    )
    # ... test logic
```

### 2. Mock External Dependencies

```python
from unittest.mock import patch

@patch("time.sleep")  # Mock sleep to avoid waiting
def test_with_retry(mock_sleep):
    # ... test logic
    assert mock_sleep.called
```

### 3. Test Exceptions

```python
import pytest

def test_error_handling():
    with pytest.raises(DomainException) as exc_info:
        # Code that raises exception
        pass
    
    assert "error message" in str(exc_info.value)
```

## 💡 Best Practices

1. **Fast Execution**: Use Mocks to avoid real network requests
2. **Independent Tests**: Each test doesn't depend on other tests
3. **Clear Naming**: Test names should describe what is being tested
4. **AAA Pattern**: Arrange → Act → Assert

## 📚 More Information

For detailed documentation, see [TESTING.md](../TESTING.md)
