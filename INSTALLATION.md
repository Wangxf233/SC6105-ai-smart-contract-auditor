# 安装和运行指南

## 前置要求

- Python 3.8+
- pip

## 安装步骤

### 1. 安装基础依赖

```bash
pip install -r requirements.txt
```

### 2. 安装成员4新增的依赖

```bash
# 安装可视化库
pip install plotly==5.18.0

# 安装PDF导出库
pip install reportlab==4.0.9
```

或者一次性安装所有依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中打开，默认地址：`http://localhost:8501`

## 功能导航

### 主页 - Smart Audit (app.py)
- 输入Solidity代码进行审计
- 查看启发式分析和AI深度分析
- 导出报告（Markdown、JSON、PDF）

### Dashboard 页面
- 查看审计统计数据
- 查看最近的审计历史
- 可视化严重性分布

访问方式：
1. 通过侧边栏点击 "📊 Dashboard"
2. 或直接访问：`http://localhost:8501/dashboard`

### Statistics 页面
- 详细的数据分析
- 多维度可视化图表
- 漏洞类型分析
- 月度趋势分析

访问方式：
1. 通过侧边栏点击 "📈 Statistics"
2. 或直接访问：`http://localhost:8501/statistics`

## 验证安装

运行以下命令验证依赖是否正确安装：

```bash
python -c "import plotly; import reportlab; import streamlit; print('✅ All dependencies installed successfully!')"
```

## 故障排除

### 问题：无法导入plotly
```bash
# 解决方案
pip install --upgrade plotly
```

### 问题：PDF导出失败
```bash
# 解决方案
pip install --upgrade reportlab
```

### 问题：Streamlit页面无法访问
- 确保 `pages/` 目录存在
- 检查文件名是否正确（`dashboard.py`, `statistics.py`）
- 重启Streamlit应用

## 开发模式

如果需要开发和调试：

```bash
# 启用调试模式
streamlit run app.py --logger.level=debug

# 自动重载
streamlit run app.py --server.runOnSave=true
```

## 注意事项

1. **首次运行**：首次运行可能需要下载一些依赖包
2. **模拟数据**：当前使用模拟数据，等待数据库模块集成
3. **PDF字体**：PDF导出使用默认字体，中文显示可能有问题
4. **浏览器缓存**：如果页面显示异常，尝试清除浏览器缓存

## 下一步

- 等待成员1完成数据库模块集成
- 等待成员2完成认证模块集成
- 测试完整的用户流程

---

如有问题，请联系团队成员！
