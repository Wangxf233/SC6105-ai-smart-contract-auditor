# 模块接口定义文档

本文档定义各模块之间的接口，确保团队成员能够并行开发。

---

## 📦 成员1：数据库接口

### 数据库管理器
```python
from src.database import db_manager

# 获取数据库会话
session = db_manager.get_session()

# 关闭会话
db_manager.close_session(session)

# 初始化数据库
db_manager.create_tables()
```

### User模型
```python
from src.database import User

# 字段
user.id              # int: 主键
user.username        # str: 用户名（唯一）
user.email           # str: 邮箱（唯一）
user.password_hash   # str: 密码哈希
user.created_at      # datetime: 创建时间
user.is_active       # bool: 是否激活
user.audits          # relationship: 审计报告列表
```

### AuditReport模型
```python
from src.database import AuditReport

# 字段
report.id                  # int: 主键
report.user_id             # int: 用户ID（外键）
report.contract_code       # str: 合约代码
report.contract_name       # str: 合约名称
report.heuristic_results   # str: 启发式结果（JSON）
report.ai_analysis         # str: AI分析结果
report.severity_score      # float: 严重性评分(0-10)
report.vulnerabilities_count  # int: 漏洞数量
report.created_at          # datetime: 创建时间
report.analysis_duration   # float: 分析耗时（秒）
report.user                # relationship: 所属用户
report.vulnerabilities     # relationship: 漏洞列表
```

### Vulnerability模型
```python
from src.database import Vulnerability

# 字段
vuln.id                # int: 主键
vuln.audit_report_id   # int: 审计报告ID（外键）
vuln.name              # str: 漏洞名称
vuln.severity          # str: 严重级别
vuln.description       # str: 描述
vuln.recommendation    # str: 建议
vuln.line_number       # int: 行号
vuln.function_name     # str: 函数名
vuln.audit_report      # relationship: 所属报告
```

---

## 🔐 成员2：认证接口

### UserAuth类
```python
from src.auth import UserAuth, AuthenticationError

# 用户注册
try:
    user = UserAuth.register_user(
        username="test",
        email="test@example.com",
        password="password123"
    )
    # 返回 User对象
except AuthenticationError as e:
    print(f"注册失败: {e}")

# 用户登录
try:
    user = UserAuth.login_user(
        username="test",  # 支持用户名或邮箱
        password="password123"
    )
    # 返回 User对象
except AuthenticationError as e:
    print(f"登录失败: {e}")

# 获取用户
user = UserAuth.get_user_by_id(user_id)

# 更新密码
success = UserAuth.update_password(
    user_id=1,
    old_password="old123",
    new_password="new123"
)
```

### JWT Token（成员5使用）
```python
from src.security import create_access_token, verify_token

# 生成Token
token = create_access_token(user_id=1)

# 验证Token
user_id = verify_token(token)  # 返回user_id或None
```

---

## 🔍 审计服务（成员3）接口约定

本文件定义了审计服务层 (`src/audit_service.py`) 与其他成员（数据库、认证、前端、API）的对齐接口。

### 一、核心数据模型

#### 1. `VulnerabilityFinding`

- **id**: `str` — 漏洞记录唯一 ID（由服务层生成或数据库生成）
- **title**: `str` — 漏洞名称
- **severity**: `str` — 严重等级：`Critical | High | Medium | Low | Informational | None`
- **description**: `str` — 漏洞描述
- **recommendation**: `str` — 修复建议
- **suggested_code**: `str` — 建议代码（Solidity）

> 建议由成员1将其映射到 `vulnerabilities` 表，外键关联 `audit_reports`。

#### 2. `FunctionAuditResult`

- **id**: `str`
- **function_name**: `str`
- **source_code**: `str`
- **markdown_report**: `str` — 该函数的 AI 审计 Markdown 文本
- **vulnerabilities**: `List[VulnerabilityFinding]` — 可选，当前为空列表，后续可由 NLP 解析填充

> 建议成员1创建 `function_audits` 表，与 `audit_reports` 一对多。

#### 3. `AuditReport`

- **id**: `str`
- **user_id**: `Optional[str]` — 用户 ID，由认证模块提供
- **created_at**: `datetime` (UTC)
- **target_name**: `Optional[str]` — 合约/项目名称或用户自定义标签
- **raw_input**: `str` — 用户提交的 Solidity 或安全问题
- **heuristic_alerts**: `List[str]` — 启发式检查结果（Markdown 列表）
- **full_markdown_report**: `str` — 完整 AI 审计报告（按函数拼接）
- **functions**: `List[FunctionAuditResult]`
- **extra_metadata**: `Dict[str, Any]` — 预留字段（如链类型、编译器版本等）

---

### 二、仓储接口（给成员1：数据库）

`src/audit_service.py` 中定义：

```python
class AuditRepository(Protocol):
    def create_audit(self, audit: AuditReport) -> AuditReport: ...

    def list_audits_for_user(
        self,
        user_id: Optional[str],
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditReport]: ...

    def get_audit_by_id(
        self,
        audit_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[AuditReport]: ...
```

**成员1需要做的事：**

1. 使用 SQLAlchemy 定义与上述数据结构对应的模型。
2. 实现一个类（例如 `DatabaseAuditRepository`）满足 `AuditRepository` 协议。
3. 在应用启动时调用：

```python
from src.audit_service import set_audit_repository

set_audit_repository(DatabaseAuditRepository(...))
```

---

### 三、服务层公开函数（给成员2、4、5 使用）

#### 1. `analyze_and_persist_audit(...) -> AuditReport`

```python
from src.audit_service import analyze_and_persist_audit

audit = analyze_and_persist_audit(
    qa_chain,
    raw_input=solidity_code_or_question,
    user_id=current_user_id,          # 由认证模块提供
    target_name="MyContract",         # UI / API 传入
    extra_metadata={"network": "L1"}, # 可选
)
```

- 内部调用：
  - `run_heuristic_checks(raw_input)`
  - `analyze_code_with_ai(qa_chain, raw_input, on_function_analyzed=...)`
  - `_repository.create_audit(audit)`

#### 2. `list_audits_for_user(user_id, limit=50, offset=0) -> List[AuditReport]`

供：

- `pages/history.py`（前端）
- 将来的 `GET /audits` API（成员5）

#### 3. `get_audit(audit_id, user_id=None) -> Optional[AuditReport]`

供：

- `pages/report_detail.py`
- 将来的 `GET /audits/{id}` API

---

### 四、与认证模块（成员2）的对接约定

- 目前 `pages/history.py` 与 `pages/report_detail.py` 中通过：

```python
def _get_current_user_id() -> str:
    return "demo-user"
```

- 未来改造方式（由成员2负责）：
  - 替换为从会话 / JWT 中提取的真实 `user_id`。
  - 保证：
    - 创建审计：`analyze_and_persist_audit(..., user_id=current_user_id, ...)`
    - 查询审计列表：`list_audits_for_user(user_id=current_user_id, ...)`
    - 查询详情：`get_audit(audit_id, user_id=current_user_id)`

---

### 五、与前端（成员4）和 API（成员5）的协作点

#### 前端（Streamlit）

- 主审计页面：
  - 目前仍使用 `src.logic.analyze_code_with_ai` 直接返回 Markdown。
  - 成员4在改造界面时，应改为调用：

```python
from src.audit_service import analyze_and_persist_audit

audit = analyze_and_persist_audit(qa_chain, user_input, user_id=current_user_id, target_name=label)
st.markdown(audit.full_markdown_report)
```

- 历史页 / 详情页：
  - 已由成员3提供 `pages/history.py` 与 `pages/report_detail.py` 的基础实现。

#### API（FastAPI）

将来的典型接口设计建议：

- `POST /api/audits`：触发一次新的审计，返回 `AuditReport` JSON。
- `GET /api/audits`：分页列出当前用户的审计记录。
- `GET /api/audits/{id}`：返回单个审计报告。

这三个接口内部均应调用本文件描述的服务接口，而不是直接操作数据库。

---

## 🎨 成员4：前端接口

### 使用审计服务（成员3）的接口
```python
# 在Streamlit页面中使用

import streamlit as st
from src.auth import UserAuth
from src.audit_service import (
    analyze_and_persist_audit,
    list_audits_for_user,
    get_audit
)

# 获取当前登录用户
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
    
    # 创建新的审计报告
    audit = analyze_and_persist_audit(
        qa_chain,
        raw_input=contract_code,
        user_id=user_id,
        target_name="MyContract"
    )
    st.markdown(audit.full_markdown_report)
    
    # 获取审计历史
    audits = list_audits_for_user(user_id, limit=50, offset=0)
    
    # 获取单个审计详情
    audit = get_audit(audit_id, user_id=user_id)
```

### 导出服务（成员4创建）
```python
from src.export_service import ExportService

# 导出PDF
pdf_path = ExportService.export_to_pdf(audit_report)

# 导出JSON
json_str = ExportService.export_to_json(audit_report)
```

### 可视化服务（成员4创建）
```python
from src.visualization import create_severity_chart, create_timeline_chart

# 创建严重性分布图
fig = create_severity_chart(stats['severity_distribution'])

# 创建时间趋势图
fig = create_timeline_chart(audits)
```

---

## 🔌 成员5：API接口

### API端点（供外部调用）

#### 认证相关
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "test",
  "email": "test@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "user_id": 1,
  "username": "test",
  "email": "test@example.com"
}
```

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "test",
  "password": "password123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1
}
```

#### 审计相关
```bash
POST /api/audits
Authorization: Bearer <token>
Content-Type: application/json

{
  "raw_input": "pragma solidity ^0.8.0; ...",
  "target_name": "MyContract",
  "extra_metadata": {"network": "L1"}
}

Response: 200 OK
{
  "id": "audit-uuid-123",
  "user_id": "user-123",
  "target_name": "MyContract",
  "created_at": "2026-01-23T10:30:00Z",
  "full_markdown_report": "## 审计报告...",
  "heuristic_alerts": ["⚠️ Warning..."],
  "functions": [
    {
      "id": "func-1",
      "function_name": "withdraw",
      "markdown_report": "### withdraw() 函数...",
      "vulnerabilities": [...]
    }
  ]
}
```

```bash
GET /api/audits/{audit_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "audit-uuid-123",
  "user_id": "user-123",
  "target_name": "MyContract",
  "created_at": "2026-01-23T10:30:00Z",
  "raw_input": "pragma solidity ^0.8.0; ...",
  "full_markdown_report": "## 审计报告...",
  "functions": [...]
}
```

```bash
GET /api/audits?limit=10&offset=0
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "audit-uuid-123",
    "target_name": "MyContract",
    "created_at": "2026-01-23T10:30:00Z"
  },
  ...
]
```

### 使用审计服务（成员3）的接口
```python
# 在FastAPI路由中使用

from fastapi import APIRouter, Depends
from src.audit_service import (
    analyze_and_persist_audit,
    list_audits_for_user,
    get_audit
)
from src.auth import get_current_user

router = APIRouter(prefix="/api/audits")

@router.post("/")
async def create_audit(
    raw_input: str,
    target_name: str,
    current_user_id: str = Depends(get_current_user)
):
    audit = analyze_and_persist_audit(
        qa_chain,
        raw_input=raw_input,
        user_id=current_user_id,
        target_name=target_name
    )
    return audit

@router.get("/")
async def list_audits(
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user)
):
    return list_audits_for_user(current_user_id, limit, offset)

@router.get("/{audit_id}")
async def get_audit_detail(
    audit_id: str,
    current_user_id: str = Depends(get_current_user)
):
    return get_audit(audit_id, user_id=current_user_id)
```

### Pydantic模型（成员5定义）
```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VulnerabilityFinding(BaseModel):
    id: str
    title: str
    severity: str
    description: str
    recommendation: str
    suggested_code: str

class FunctionAuditResult(BaseModel):
    id: str
    function_name: str
    source_code: str
    markdown_report: str
    vulnerabilities: List[VulnerabilityFinding]

class AuditReport(BaseModel):
    id: str
    user_id: Optional[str]
    created_at: datetime
    target_name: Optional[str]
    raw_input: str
    heuristic_alerts: List[str]
    full_markdown_report: str
    functions: List[FunctionAuditResult]
    extra_metadata: Dict[str, Any]
```

---

## 🧪 成员6：测试接口

### 测试固件（供所有测试使用）
```python
# tests/conftest.py
import pytest
from src.database import db_manager

@pytest.fixture
def db_session():
    """提供数据库会话"""
    session = db_manager.get_session()
    yield session
    session.rollback()
    db_manager.close_session(session)

@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    from src.auth import UserAuth
    user = UserAuth.register_user("testuser", "test@test.com", "password")
    return user

@pytest.fixture
def authenticated_client():
    """提供已认证的API客户端"""
    from fastapi.testclient import TestClient
    from api import app
    client = TestClient(app)
    # 登录并设置token
    return client
```

### 测试示例
```python
# tests/test_auth.py
def test_register_user(db_session):
    from src.auth import UserAuth
    user = UserAuth.register_user("test", "test@test.com", "pass123")
    assert user.username == "test"

# tests/test_api.py
def test_create_audit(authenticated_client):
    response = authenticated_client.post("/api/audit", json={
        "contract_code": "pragma solidity ^0.8.0; ...",
        "contract_name": "Test"
    })
    assert response.status_code == 200
```

---

## 📝 接口变更流程

1. **提议变更**：在团队会议或GitHub Issue中讨论
2. **更新文档**：修改本文档的相应部分
3. **通知团队**：在群聊中@相关成员
4. **更新代码**：实现接口变更
5. **更新测试**：确保测试覆盖新接口

---

## ⚠️ 重要约定

1. **数据库会话**：使用完必须关闭（使用`try-finally`或上下文管理器）
2. **异常处理**：使用自定义异常类（如`AuthenticationError`）
3. **类型注解**：所有函数使用Type Hints
4. **文档字符串**：遵循Google风格的Docstring
5. **日志记录**：重要操作使用logger记录

---

有问题请在团队频道提出！🚀
