# AI Daily - Vercel 快速部署指南

## 🚀 一键部署到 Vercel（免费，永久公网访问）

### 前提条件
- ✅ GitHub 账号
- ✅ 已安装 Git

---

## 步骤一：上传代码到 GitHub

```bash
# 1. 创建新仓库
cd ai-daily
git init
git add .
git commit -m "Initial commit"

# 2. 替换为你的用户名和仓库名（示例）
git remote add origin https://github.com/YOUR_USERNAME/ai-daily.git
git push -u origin main
```

---

## 步骤二：部署到 Vercel

### 方式 A：使用 Vercel CLI（推荐，最快）

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 一键部署
vercel --prod
```

**完成！**Vercel 会自动生成公网 URL。

---

### 方式 B：使用 Vercel Web 界面（无需命令行）

1. https://vercel.com 登录 GitHub 账号
2. Import Git Repository → 选择你的 `ai-daily`仓库
3. Build and Deploy:
   - **Build Command:** ````python app.py````
   - **Output Directory:** ````data/feeds/````（或留空）
4. Deploy！

---

## 📝 Vercel 配置说明

由于 Flask 是 Python Web 应用，Vercel 需要特殊配置：

### 推荐方案：使用 Serverless Function

创建 `api/index.py`：

```python
import os
from flask import Flask, jsonify
import sys

app = Flask(__name__)

def run_daily_fetcher():
    from ai_daily.app import create_app
    return create_app()

@app.get("/")
async def get_index():
    # 触发数据采集并返回首页
    app_ctx = app.app_context().push()
    fetcher = run_daily_fetcher()
    
    with open('data/feeds/index.html', 'r') as f:
        html = f.read()
    
    return jsonify({"html": html})

@app.get("/api/news")
async def get_news():
    app_ctx = app.app_context().push()
    fetcher = run_daily_fetcher()
    
    with open('data/feeds/2026-07-21.json', 'r') as f:
        news_data = json.load(f)
    
    return jsonify({"news": news_data})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

## ⚠️ 重要提示

### Vercel/Render等平台的限制：
- ❌ **不支持 Python Flask**（需要 Node.js）
- ✅ **推荐方案：** 使用 Docker 或迁移到 FastAPI/Flask+nginx

### 替代方案对比：

| 平台 | 免费额度 | 适合场景 | 难度 |
|------|---------|---------|-----|
| Vercel + Serverless | ✓永久免费 | 静态网站 | ⭐⭐ |
| Render Free | ✓576h/月 | Flask应用（需配置） | ⭐⭐⭐ |
| Railway Free | ✗100h/月 | Python应用 | ⭐⭐ |
| GitHub Pages + Vercel Functions | ✓永久免费 | 静态+API分离 | ⭐⭐⭐⭐ |

---

## 🎯 推荐方案：本地运行 + Cloudflare Tunnel（当前已配置）

**优点：**
- ✅ 无需服务器费用
- ✅ HTTPS加密访问
- ✅ 一次配置长期使用

**缺点：**
- ❌ 需要保持电脑开机
- ❌ URL每次重启会变化

---

## 📱 手机访问方式

### 方案一：局域网（WiFi）
```bash
http://192.168.110.41:5000
```

### 方案二：公网穿透
- **Cloudflare Tunnel** → https://era-series-visit-lambda.trycloudflare.com
- **Vercel部署后** → vercel.app/生成的URL（永久不变）

---

## 🔧 本地运行命令

```bash
# 启动 Flask + Cloudflare Tunnel
start_with_tunnel.bat

# 仅启动 Flask
python app.py

# 查看日志
tail -f data/logs/app.log
```