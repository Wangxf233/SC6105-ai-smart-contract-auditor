# 成员4模块快速参考

## 📚 模块导入快速参考

### 可视化模块 (src/visualization.py)

```python
from src.visualization import (
    create_severity_chart,          # 创建严重性饼图
    create_severity_bar_chart,      # 创建严重性柱状图
    create_timeline_chart,          # 创建时间趋势图
    create_function_vulnerability_chart,  # 创建函数漏洞图
    create_audit_stats_cards        # 创建统计卡片
)

# 使用示例
severity_data = {
    "Critical": 3,
    "High": 8,
    "Medium": 15,
    "Low": 18,
    "Informational": 3
}

fig = create_severity_chart(severity_data)
st.plotly_chart(fig, use_container_width=True)
```

### 导出服务 (src/export_service.py)

```python
from src.export_service import ExportService

# 导出为JSON
json_str = ExportService.export_to_json(audit_report)

# 导出为Markdown
md_str = ExportService.export_to_markdown(audit_report)

# 导出为PDF
pdf_bytes = ExportService.export_to_pdf(audit_report)

# Streamlit下载按钮
st.download_button(
    label="Download PDF",
    data=pdf_bytes,
    file_name="audit_report.pdf",
    mime="application/pdf"
)
```

## 🔌 集成示例

### 在Streamlit页面中使用

```python
import streamlit as st
from src.visualization import create_severity_chart
from src.export_service import ExportService

# 页面配置
st.set_page_config(
    page_title="My Page",
    page_icon="📊",
    layout="wide"
)

# 显示图表
fig = create_severity_chart(data)
st.plotly_chart(fig)

# 导出按钮
if st.button("Export Report"):
    pdf = ExportService.export_to_pdf(report)
    st.download_button("Download", pdf, "report.pdf")
```

### 数据格式要求

#### 审计报告格式 (用于导出)

```python
audit_report = {
    'id': 'audit-001',
    'target_name': 'MyContract',
    'created_at': datetime.now().isoformat(),
    'user_id': 'user-123',
    'raw_input': 'pragma solidity ^0.8.0; ...',
    'heuristic_alerts': ['⚠️ Warning 1', '⚠️ Warning 2'],
    'full_markdown_report': '## Analysis Report...',
    'functions': [
        {
            'function_name': 'transfer',
            'vulnerabilities': [
                {
                    'title': 'Reentrancy',
                    'severity': 'High',
                    'description': '...',
                    'recommendation': '...'
                }
            ]
        }
    ]
}
```

#### 统计数据格式 (用于可视化)

```python
stats = {
    'total_audits': 15,
    'total_vulnerabilities': 47,
    'critical_count': 3,
    'high_count': 8,
    'avg_severity_score': 6.5,
    'recent_audit_count': 5,
    'severity_distribution': {
        'Critical': 3,
        'High': 8,
        'Medium': 15,
        'Low': 18,
        'Informational': 3
    }
}
```

#### 审计历史格式 (用于时间趋势图)

```python
audits = [
    {
        'id': 'audit-001',
        'target_name': 'TokenContract',
        'created_at': '2026-01-22T10:30:00',
        'vulnerabilities_count': 5,
        'severity_score': 7.5
    },
    # ... more audits
]
```

## 🎨 UI组件示例

### 统计卡片

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Audits", "15", "+3")

with col2:
    st.metric("Vulnerabilities", "47", "-5")

with col3:
    st.metric("Avg Score", "6.5", "0.3")
```

### 导航按钮

```python
if st.button("📊 Dashboard", use_container_width=True):
    st.switch_page("pages/dashboard.py")
```

### 数据表格

```python
import pandas as pd

data = [
    {"Contract": "Token", "Date": "2026-01-22", "Vulns": 5},
    {"Contract": "NFT", "Date": "2026-01-21", "Vulns": 3}
]

st.dataframe(data, use_container_width=True, hide_index=True)
```

## 🔄 与其他模块集成

### 获取当前用户ID (成员2)

```python
def _get_current_user_id() -> str:
    if 'user_id' in st.session_state:
        return st.session_state['user_id']
    return "guest"
```

### 查询数据库 (成员1)

```python
# 替换模拟数据函数
from src.database import AuditReport

def get_user_audits(user_id: str):
    # 从数据库查询
    return db.query(AuditReport).filter_by(user_id=user_id).all()
```

### 使用审计服务 (成员3)

```python
from src.audit_service import analyze_and_persist_audit

audit = analyze_and_persist_audit(
    qa_chain,
    raw_input=code,
    user_id=current_user_id,
    target_name="MyContract"
)
```

## 🐛 调试技巧

### 查看数据结构

```python
import streamlit as st

# 在页面中显示数据
st.json(audit_report)
st.write(stats)
```

### 捕获错误

```python
try:
    fig = create_severity_chart(data)
    st.plotly_chart(fig)
except Exception as e:
    st.error(f"Error creating chart: {str(e)}")
    st.exception(e)  # 显示完整堆栈
```

### 日志记录

```python
from src.logger_config import logger

logger.info(f"Creating chart for user {user_id}")
logger.error(f"Chart creation failed: {error}")
```

## 📋 常用命令

```bash
# 运行应用
streamlit run app.py

# 清除缓存
streamlit cache clear

# 查看日志
tail -f auditor.log

# 测试导入
python -c "from src.visualization import *; from src.export_service import *; print('OK')"
```

## 💡 最佳实践

1. **使用类型注解**：帮助IDE提供更好的代码提示
2. **错误处理**：所有外部调用都要有try-except
3. **数据验证**：检查数据是否为空或格式是否正确
4. **用户反馈**：使用st.spinner、st.success、st.error等提示
5. **性能优化**：大数据量使用st.cache_data装饰器

## 📞 需要帮助？

- 查看完整文档：`MEMBER4_COMPLETION.md`
- 查看接口定义：`INTERFACES.md`
- 查看安装指南：`INSTALLATION.md`

---

Happy Coding! 🚀
