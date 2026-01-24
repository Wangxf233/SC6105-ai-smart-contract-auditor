"""
数据可视化模块
提供审计报告的可视化图表功能
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd


def create_severity_chart(severity_distribution: Dict[str, int]) -> go.Figure:
    """
    创建严重性分布饼图

    Args:
        severity_distribution: 严重性分布字典 {"Critical": 2, "High": 5, ...}

    Returns:
        Plotly Figure对象
    """
    if not severity_distribution:
        # 返回空图表
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # 颜色映射
    color_map = {
        "Critical": "#d32f2f",
        "High": "#f57c00",
        "Medium": "#fbc02d",
        "Low": "#388e3c",
        "Informational": "#1976d2",
        "None": "#757575"
    }

    labels = list(severity_distribution.keys())
    values = list(severity_distribution.values())
    colors = [color_map.get(label, "#757575") for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.3,
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title_text="Vulnerability Severity Distribution",
        title_x=0.5,
        showlegend=True,
        height=400
    )

    return fig


def create_timeline_chart(audits: List[Dict[str, Any]]) -> go.Figure:
    """
    创建审计时间趋势图

    Args:
        audits: 审计报告列表，每个报告包含 created_at 和 vulnerabilities_count

    Returns:
        Plotly Figure对象
    """
    if not audits:
        fig = go.Figure()
        fig.add_annotation(
            text="No audit history available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # 准备数据
    dates = []
    vuln_counts = []

    for audit in audits:
        if isinstance(audit.get('created_at'), str):
            date = datetime.fromisoformat(audit['created_at'].replace('Z', '+00:00'))
        else:
            date = audit.get('created_at', datetime.now())

        dates.append(date)
        vuln_counts.append(audit.get('vulnerabilities_count', 0))

    # 创建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'vulnerabilities': vuln_counts
    })

    # 按日期排序
    df = df.sort_values('date')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['vulnerabilities'],
        mode='lines+markers',
        name='Vulnerabilities Found',
        line=dict(color='#f57c00', width=2),
        marker=dict(size=8, color='#d32f2f'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Vulnerabilities:</b> %{y}<extra></extra>'
    ))

    fig.update_layout(
        title_text="Audit History Timeline",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Number of Vulnerabilities",
        hovermode='x unified',
        height=400,
        showlegend=True
    )

    return fig


def create_severity_bar_chart(severity_data: Dict[str, int]) -> go.Figure:
    """
    创建严重性柱状图

    Args:
        severity_data: 严重性数据字典

    Returns:
        Plotly Figure对象
    """
    if not severity_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # 颜色映射
    color_map = {
        "Critical": "#d32f2f",
        "High": "#f57c00",
        "Medium": "#fbc02d",
        "Low": "#388e3c",
        "Informational": "#1976d2",
        "None": "#757575"
    }

    # 按严重性排序
    severity_order = ["Critical", "High", "Medium", "Low", "Informational", "None"]
    sorted_data = {k: severity_data.get(k, 0) for k in severity_order if k in severity_data}

    labels = list(sorted_data.keys())
    values = list(sorted_data.values())
    colors = [color_map.get(label, "#757575") for label in labels]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors),
        text=values,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title_text="Vulnerability Severity Analysis",
        title_x=0.5,
        xaxis_title="Severity Level",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )

    return fig


def create_function_vulnerability_chart(functions: List[Dict[str, Any]]) -> go.Figure:
    """
    创建函数漏洞分布图

    Args:
        functions: 函数列表，每个包含 function_name 和 vulnerabilities

    Returns:
        Plotly Figure对象
    """
    if not functions:
        fig = go.Figure()
        fig.add_annotation(
            text="No function data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    # 准备数据
    function_names = []
    vuln_counts = []

    for func in functions:
        func_name = func.get('function_name', 'Unknown')
        vuln_count = len(func.get('vulnerabilities', []))

        if vuln_count > 0:  # 只显示有漏洞的函数
            function_names.append(func_name)
            vuln_counts.append(vuln_count)

    if not function_names:
        fig = go.Figure()
        fig.add_annotation(
            text="No vulnerabilities found in functions",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig

    fig = go.Figure(data=[go.Bar(
        x=function_names,
        y=vuln_counts,
        marker=dict(color='#f57c00'),
        text=vuln_counts,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Vulnerabilities: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title_text="Vulnerabilities by Function",
        title_x=0.5,
        xaxis_title="Function Name",
        yaxis_title="Number of Vulnerabilities",
        height=400,
        showlegend=False
    )

    return fig


def create_audit_stats_cards(stats: Dict[str, Any]) -> Dict[str, str]:
    """
    创建统计卡片数据

    Args:
        stats: 统计数据字典

    Returns:
        格式化的统计数据字典
    """
    return {
        "total_audits": str(stats.get("total_audits", 0)),
        "total_vulnerabilities": str(stats.get("total_vulnerabilities", 0)),
        "critical_count": str(stats.get("critical_count", 0)),
        "high_count": str(stats.get("high_count", 0)),
        "avg_severity_score": f"{stats.get('avg_severity_score', 0):.2f}",
        "recent_audit_count": str(stats.get("recent_audit_count", 0))
    }
