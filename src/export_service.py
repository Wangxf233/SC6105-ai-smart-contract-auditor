"""
报告导出服务模块
提供PDF和JSON格式的报告导出功能
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO


class ExportService:
    """审计报告导出服务"""

    @staticmethod
    def export_to_json(audit_report: Dict[str, Any]) -> str:
        """
        将审计报告导出为JSON格式

        Args:
            audit_report: 审计报告字典

        Returns:
            JSON字符串
        """
        # 处理datetime对象
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(audit_report, indent=2, default=json_serial, ensure_ascii=False)

    @staticmethod
    def export_to_json_file(audit_report: Dict[str, Any], filepath: str) -> str:
        """
        将审计报告导出为JSON文件

        Args:
            audit_report: 审计报告字典
            filepath: 文件路径

        Returns:
            保存的文件路径
        """
        json_str = ExportService.export_to_json(audit_report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)

        return filepath

    @staticmethod
    def export_to_pdf(audit_report: Dict[str, Any], filepath: Optional[str] = None) -> bytes:
        """
        将审计报告导出为PDF格式

        Args:
            audit_report: 审计报告字典
            filepath: 可选的文件保存路径，如果不提供则返回字节流

        Returns:
            PDF字节数据或保存的文件路径
        """
        # 创建PDF
        if filepath:
            buffer = filepath
        else:
            buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # 容器
        story = []

        # 样式
        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceAfter=12,
            spaceBefore=12
        )

        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14

        # 标题
        story.append(Paragraph("Smart Contract Audit Report", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # 基本信息
        story.append(Paragraph("Basic Information", heading_style))

        basic_info = [
            ["Report ID:", audit_report.get('id', 'N/A')],
            ["Target Name:", audit_report.get('target_name', 'N/A')],
            ["Created At:", str(audit_report.get('created_at', 'N/A'))],
            ["User ID:", audit_report.get('user_id', 'N/A')],
        ]

        basic_table = Table(basic_info, colWidths=[2 * inch, 4 * inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(basic_table)
        story.append(Spacer(1, 0.3 * inch))

        # 启发式检查结果
        story.append(Paragraph("Heuristic Analysis", heading_style))
        heuristic_alerts = audit_report.get('heuristic_alerts', [])

        if heuristic_alerts:
            for alert in heuristic_alerts:
                # 清理Markdown格式
                clean_alert = alert.replace('**', '').replace('⚠️', '').replace('✅', '')
                story.append(Paragraph(f"• {clean_alert}", normal_style))
        else:
            story.append(Paragraph("No heuristic alerts found.", normal_style))

        story.append(Spacer(1, 0.3 * inch))

        # 函数分析
        functions = audit_report.get('functions', [])

        if functions:
            story.append(Paragraph("Function Analysis", heading_style))

            for idx, func in enumerate(functions, 1):
                func_name = func.get('function_name', 'Unknown')

                story.append(Paragraph(f"<b>{idx}. Function: {func_name}</b>", normal_style))
                story.append(Spacer(1, 0.1 * inch))

                # 漏洞列表
                vulnerabilities = func.get('vulnerabilities', [])

                if vulnerabilities:
                    for vuln in vulnerabilities:
                        vuln_title = vuln.get('title', 'Unknown')
                        severity = vuln.get('severity', 'Unknown')
                        description = vuln.get('description', 'No description')

                        # 根据严重性设置颜色
                        severity_color = ExportService._get_severity_color(severity)

                        story.append(Paragraph(
                            f"<b>Vulnerability:</b> {vuln_title} "
                            f"<font color='{severity_color}'>[{severity}]</font>",
                            normal_style
                        ))
                        story.append(Paragraph(f"<i>{description}</i>", normal_style))
                        story.append(Spacer(1, 0.1 * inch))
                else:
                    story.append(Paragraph("<i>No vulnerabilities found in this function.</i>", normal_style))

                story.append(Spacer(1, 0.2 * inch))

        # AI分析摘要
        full_report = audit_report.get('full_markdown_report', '')

        if full_report:
            story.append(PageBreak())
            story.append(Paragraph("AI Analysis Summary", heading_style))

            # 简化Markdown到PDF的转换
            lines = full_report.split('\n')
            for line in lines[:50]:  # 限制行数以避免PDF过大
                if line.strip():
                    # 清理Markdown格式
                    clean_line = line.replace('**', '').replace('##', '').replace('###', '')
                    if len(clean_line) > 500:  # 截断过长的行
                        clean_line = clean_line[:500] + "..."

                    try:
                        story.append(Paragraph(clean_line, normal_style))
                    except:
                        # 如果包含无法处理的字符，跳过
                        pass

        # 生成PDF
        doc.build(story)

        if isinstance(buffer, BytesIO):
            return buffer.getvalue()
        else:
            return filepath

    @staticmethod
    def _get_severity_color(severity: str) -> str:
        """获取严重性对应的颜色"""
        color_map = {
            "Critical": "#d32f2f",
            "High": "#f57c00",
            "Medium": "#fbc02d",
            "Low": "#388e3c",
            "Informational": "#1976d2",
        }
        return color_map.get(severity, "#757575")

    @staticmethod
    def export_to_markdown(audit_report: Dict[str, Any]) -> str:
        """
        将审计报告导出为Markdown格式

        Args:
            audit_report: 审计报告字典

        Returns:
            Markdown字符串
        """
        md_lines = []

        # 标题
        md_lines.append("# Smart Contract Audit Report")
        md_lines.append("")

        # 基本信息
        md_lines.append("## Basic Information")
        md_lines.append("")
        md_lines.append(f"- **Report ID:** {audit_report.get('id', 'N/A')}")
        md_lines.append(f"- **Target Name:** {audit_report.get('target_name', 'N/A')}")
        md_lines.append(f"- **Created At:** {audit_report.get('created_at', 'N/A')}")
        md_lines.append(f"- **User ID:** {audit_report.get('user_id', 'N/A')}")
        md_lines.append("")

        # 启发式检查
        md_lines.append("## Heuristic Analysis")
        md_lines.append("")
        heuristic_alerts = audit_report.get('heuristic_alerts', [])
        if heuristic_alerts:
            for alert in heuristic_alerts:
                md_lines.append(f"- {alert}")
        else:
            md_lines.append("No heuristic alerts found.")
        md_lines.append("")

        # 完整报告
        full_report = audit_report.get('full_markdown_report', '')
        if full_report:
            md_lines.append("## AI Analysis Report")
            md_lines.append("")
            md_lines.append(full_report)

        return "\n".join(md_lines)

    @staticmethod
    def export_to_markdown_file(audit_report: Dict[str, Any], filepath: str) -> str:
        """
        将审计报告导出为Markdown文件

        Args:
            audit_report: 审计报告字典
            filepath: 文件路径

        Returns:
            保存的文件路径
        """
        md_str = ExportService.export_to_markdown(audit_report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_str)

        return filepath
