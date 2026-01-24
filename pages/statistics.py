"""
数据统计页面
展示详细的审计数据统计和可视化分析
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualization import (
    create_severity_chart,
    create_timeline_chart,
    create_severity_bar_chart,
    create_function_vulnerability_chart
)


def _get_current_user_id() -> str:
    """获取当前登录用户ID"""
    if 'user_id' in st.session_state:
        return st.session_state['user_id']
    return "demo-user"


def _get_mock_detailed_statistics() -> Dict[str, Any]:
    """获取详细的模拟统计数据"""
    return {
        "total_audits": 25,
        "total_contracts": 25,
        "total_functions_analyzed": 156,
        "total_vulnerabilities": 89,
        "severity_distribution": {
            "Critical": 5,
            "High": 15,
            "Medium": 28,
            "Low": 34,
            "Informational": 7
        },
        "vulnerability_types": {
            "Reentrancy": 12,
            "Integer Overflow": 8,
            "Access Control": 15,
            "Unchecked Call": 10,
            "Timestamp Dependence": 6,
            "Denial of Service": 4,
            "Front Running": 3,
            "Others": 31
        },
        "monthly_stats": [
            {"month": "2025-07", "audits": 3, "vulnerabilities": 12},
            {"month": "2025-08", "audits": 5, "vulnerabilities": 18},
            {"month": "2025-09", "audits": 4, "vulnerabilities": 15},
            {"month": "2025-10", "audits": 6, "vulnerabilities": 22},
            {"month": "2025-11", "audits": 4, "vulnerabilities": 14},
            {"month": "2025-12", "audits": 3, "vulnerabilities": 8},
        ],
        "avg_vulnerabilities_per_audit": 3.56,
        "avg_analysis_time": 45.3,
        "most_common_vulnerability": "Access Control Issues"
    }


def _get_mock_audit_history() -> List[Dict[str, Any]]:
    """获取模拟的完整审计历史"""
    history = []
    base_date = datetime.now()

    for i in range(25):
        days_ago = i * 2
        history.append({
            "id": f"audit-{str(i+1).zfill(3)}",
            "target_name": f"Contract{i+1}",
            "created_at": (base_date - timedelta(days=days_ago)).isoformat(),
            "vulnerabilities_count": (i % 10) + 1,
            "severity_score": ((i % 10) + 1) * 0.8,
        })

    return history


def render_overview_section(stats: Dict[str, Any]):
    """渲染概览部分"""
    st.header("📊 Overview Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Audits",
            value=stats["total_audits"],
            delta=f"+{stats['monthly_stats'][-1]['audits']} this month"
        )

    with col2:
        st.metric(
            label="Total Vulnerabilities",
            value=stats["total_vulnerabilities"],
            delta=f"+{stats['monthly_stats'][-1]['vulnerabilities']} this month"
        )

    with col3:
        st.metric(
            label="Avg Vulnerabilities/Audit",
            value=f"{stats['avg_vulnerabilities_per_audit']:.2f}",
            delta=None
        )

    with col4:
        st.metric(
            label="Avg Analysis Time",
            value=f"{stats['avg_analysis_time']:.1f}s",
            delta=None
        )


def render_severity_analysis(stats: Dict[str, Any]):
    """渲染严重性分析"""
    st.header("🎯 Severity Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # 饼图
        fig_pie = create_severity_chart(stats["severity_distribution"])
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 柱状图
        fig_bar = create_severity_bar_chart(stats["severity_distribution"])
        st.plotly_chart(fig_bar, use_container_width=True)

    # 严重性详细信息
    st.subheader("Severity Breakdown")

    severity_data = []
    for severity, count in stats["severity_distribution"].items():
        percentage = (count / stats["total_vulnerabilities"]) * 100
        severity_data.append({
            "Severity": severity,
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })

    st.dataframe(severity_data, use_container_width=True, hide_index=True)


def render_vulnerability_types(stats: Dict[str, Any]):
    """渲染漏洞类型分析"""
    st.header("🔍 Vulnerability Types")

    import plotly.graph_objects as go

    # 创建漏洞类型柱状图
    types = list(stats["vulnerability_types"].keys())
    counts = list(stats["vulnerability_types"].values())

    fig = go.Figure(data=[go.Bar(
        x=types,
        y=counts,
        marker=dict(
            color=counts,
            colorscale='Reds',
            showscale=True
        ),
        text=counts,
        textposition='auto'
    )])

    fig.update_layout(
        title="Vulnerability Types Distribution",
        xaxis_title="Vulnerability Type",
        yaxis_title="Count",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # 最常见的漏洞
    st.info(f"🎯 **Most Common Vulnerability:** {stats['most_common_vulnerability']}")


def render_timeline_analysis(audits: List[Dict[str, Any]], stats: Dict[str, Any]):
    """渲染时间线分析"""
    st.header("📈 Timeline Analysis")

    # 审计时间趋势
    fig_timeline = create_timeline_chart(audits)
    st.plotly_chart(fig_timeline, use_container_width=True)

    # 月度统计
    st.subheader("Monthly Statistics")

    import plotly.graph_objects as go

    months = [stat["month"] for stat in stats["monthly_stats"]]
    audit_counts = [stat["audits"] for stat in stats["monthly_stats"]]
    vuln_counts = [stat["vulnerabilities"] for stat in stats["monthly_stats"]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=months,
        y=audit_counts,
        name='Audits',
        marker_color='#1976d2'
    ))

    fig.add_trace(go.Bar(
        x=months,
        y=vuln_counts,
        name='Vulnerabilities',
        marker_color='#f57c00'
    ))

    fig.update_layout(
        title="Monthly Audit and Vulnerability Trends",
        xaxis_title="Month",
        yaxis_title="Count",
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def render_function_analysis():
    """渲染函数分析"""
    st.header("⚙️ Function Analysis")

    # 模拟函数数据
    mock_functions = [
        {
            "function_name": "transfer",
            "vulnerabilities": [{"severity": "High"}, {"severity": "Medium"}]
        },
        {
            "function_name": "approve",
            "vulnerabilities": [{"severity": "Low"}]
        },
        {
            "function_name": "withdraw",
            "vulnerabilities": [{"severity": "Critical"}, {"severity": "High"}, {"severity": "Medium"}]
        },
        {
            "function_name": "mint",
            "vulnerabilities": [{"severity": "Medium"}]
        },
        {
            "function_name": "burn",
            "vulnerabilities": []
        }
    ]

    fig = create_function_vulnerability_chart(mock_functions)
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Functions with more vulnerabilities require priority attention.")


def main():
    """主函数"""
    st.set_page_config(
        page_title="Statistics - Auditor AI",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 Audit Statistics & Analytics")

    # 获取当前用户
    user_id = _get_current_user_id()
    st.markdown(f"**User:** `{user_id}`")

    st.markdown("---")

    # 获取数据
    stats = _get_mock_detailed_statistics()
    audits = _get_mock_audit_history()

    # 渲染各个部分
    render_overview_section(stats)

    st.markdown("---")

    render_severity_analysis(stats)

    st.markdown("---")

    render_vulnerability_types(stats)

    st.markdown("---")

    render_timeline_analysis(audits, stats)

    st.markdown("---")

    render_function_analysis()

    st.markdown("---")

    # 数据导出
    st.header("💾 Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Export Statistics (JSON)", use_container_width=True):
            import json
            json_str = json.dumps(stats, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with col2:
        if st.button("📊 Export Chart Data (CSV)", use_container_width=True):
            import pandas as pd
            df = pd.DataFrame(stats["monthly_stats"])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"chart_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col3:
        st.button("🔄 Refresh Data", use_container_width=True)


if __name__ == "__main__":
    main()
