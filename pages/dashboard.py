"""
用户仪表板页面
显示用户的审计统计和最近的审计记录
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
    create_audit_stats_cards
)


def _get_current_user_id() -> str:
    """
    获取当前登录用户ID
    TODO: 集成认证模块后，从session_state或JWT中获取
    """
    if 'user_id' in st.session_state:
        return st.session_state['user_id']
    return "demo-user"


def _get_mock_statistics() -> Dict[str, Any]:
    """
    获取模拟的统计数据
    TODO: 集成数据库后，从实际数据库查询
    """
    return {
        "total_audits": 15,
        "total_vulnerabilities": 47,
        "critical_count": 3,
        "high_count": 8,
        "medium_count": 15,
        "low_count": 18,
        "informational_count": 3,
        "avg_severity_score": 6.5,
        "recent_audit_count": 5,
        "severity_distribution": {
            "Critical": 3,
            "High": 8,
            "Medium": 15,
            "Low": 18,
            "Informational": 3
        }
    }


def _get_mock_recent_audits() -> List[Dict[str, Any]]:
    """
    获取模拟的最近审计记录
    TODO: 集成数据库后，从实际数据库查询
    """
    now = datetime.now()
    
    return [
        {
            "id": "audit-001",
            "target_name": "TokenContract",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "vulnerabilities_count": 5,
            "severity_score": 7.5
        },
        {
            "id": "audit-002",
            "target_name": "NFTMarketplace",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "vulnerabilities_count": 8,
            "severity_score": 8.2
        },
        {
            "id": "audit-003",
            "target_name": "StakingPool",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "vulnerabilities_count": 3,
            "severity_score": 5.0
        },
        {
            "id": "audit-004",
            "target_name": "DEXRouter",
            "created_at": (now - timedelta(days=5)).isoformat(),
            "vulnerabilities_count": 12,
            "severity_score": 9.1
        },
        {
            "id": "audit-005",
            "target_name": "LendingProtocol",
            "created_at": (now - timedelta(days=7)).isoformat(),
            "vulnerabilities_count": 6,
            "severity_score": 6.8
        }
    ]


def render_stats_cards(stats: Dict[str, Any]):
    """渲染统计卡片"""
    cards = create_audit_stats_cards(stats)
    
    # 第一行：总体统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📊 Total Audits",
            value=cards["total_audits"],
            delta="Recent activity"
        )
    
    with col2:
        st.metric(
            label="🔍 Total Vulnerabilities",
            value=cards["total_vulnerabilities"],
            delta=None
        )
    
    with col3:
        st.metric(
            label="📈 Avg Severity Score",
            value=cards["avg_severity_score"],
            delta=None
        )
    
    # 第二行：严重性统计
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(
            label="🔴 Critical Issues",
            value=cards["critical_count"],
            delta="High Priority"
        )
    
    with col5:
        st.metric(
            label="🟠 High Issues",
            value=cards["high_count"],
            delta=None
        )
    
    with col6:
        st.metric(
            label="📋 Recent Audits (7 days)",
            value=cards["recent_audit_count"],
            delta=None
        )


def render_recent_audits_table(audits: List[Dict[str, Any]]):
    """渲染最近审计记录表格"""
    st.subheader("📝 Recent Audit History")
    
    if not audits:
        st.info("No audit history available yet. Start your first audit!")
        return
    
    # 准备表格数据
    table_data = []
    for audit in audits:
        # 格式化日期
        created_at = audit.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = created_at
        else:
            formatted_date = 'N/A'
        
        # 严重性评分颜色
        severity_score = audit.get('severity_score', 0)
        if severity_score >= 8:
            severity_emoji = "🔴"
        elif severity_score >= 6:
            severity_emoji = "🟠"
        elif severity_score >= 4:
            severity_emoji = "🟡"
        else:
            severity_emoji = "🟢"
        
        table_data.append({
            "Contract Name": audit.get('target_name', 'Unknown'),
            "Date": formatted_date,
            "Vulnerabilities": audit.get('vulnerabilities_count', 0),
            "Severity": f"{severity_emoji} {severity_score:.1f}",
            "ID": audit.get('id', 'N/A')
        })
    
    # 显示表格
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )
    
    # 快速操作按钮
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 View All History", use_container_width=True):
            st.info("Full history view coming soon!")


def main():
    """主函数"""
    st.set_page_config(
        page_title="Dashboard - Auditor AI",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 User Dashboard")
    
    # 获取当前用户
    user_id = _get_current_user_id()
    st.markdown(f"**Welcome back, User:** `{user_id}`")
    
    st.markdown("---")
    
    # 获取统计数据
    stats = _get_mock_statistics()
    
    # 渲染统计卡片
    render_stats_cards(stats)
    
    st.markdown("---")
    
    # 可视化图表
    st.subheader("📈 Visualization")
    
    tab1, tab2 = st.tabs(["Severity Distribution", "Timeline"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # 饼图
            fig_pie = create_severity_chart(stats["severity_distribution"])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 柱状图
            fig_bar = create_severity_bar_chart(stats["severity_distribution"])
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        # 获取审计历史
        audits = _get_mock_recent_audits()
        
        # 时间趋势图
        fig_timeline = create_timeline_chart(audits)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # 最近审计记录
    render_recent_audits_table(_get_mock_recent_audits())
    
    st.markdown("---")
    
    # 页脚信息
    st.info("""
    💡 **Tips:**
    - Click on any audit ID to view detailed report
    - Use filters to narrow down your search
    - Export reports in PDF or JSON format
    """)


if __name__ == "__main__":
    main()
