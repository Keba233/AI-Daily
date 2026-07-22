# AI日报 - DeepSeek API 部署指南

## 🚀 使用 DeepSeek API 实现随时随地访问

### 前提条件
1. 拥有 DeepSeek API Key（[前往注册](https://platform.deepseek.com/)）
2. 将代码推送到 GitHub

### 步骤一：获取 DeepSeek API Key

1. 访问 [DeepSeek Open Platform](https://platform.deepseek.com/)
2. 注册/登录账号
3. 创建 API Key（需要充值，按量付费）

### 步骤二：部署到 Render（推荐）

#### 1. 连接 GitHub 仓库
- 访问 [Render Dashboard](https://dashboard.render.com/)
- 点击 "New +" → "Web Service"
- 连接你的 GitHub 仓库 `Keba233/AI-Daily`

#### 2. 配置环境

| 配置项 | 值 |
|--------|-----|
| **Name** | ai-daily (或自定义) |
| **Region** | 任意（建议新加坡） |
| **Branch** | `master` |
| **Environment** | `Python` (3.x) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |

#### 3. 添加环境变量

在 Render 的 "Environment" 标签页中添加：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PORT=5000
```

#### 4. 点击 Deploy！✅

Render 会自动部署并生成公网 URL，例如：
```
https://ai-daily.onrender.com
```

### 步骤三：验证功能

1. 访问生成的 URL
2. 首页应显示 AI 每日总结（使用 DeepSeek API）
3. 可以在手机/平板上随时随地访问

---

## 🔄 本地运行（带 DeepSeek API）

### 方法一：设置环境变量

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"
python app.py

# 或永久设置
[System.Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "your_api_key_here", "User")
python app.py
```

### 方法二：使用 .env 文件

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API Key
3. 安装 python-dotenv：
   ```bash
   pip install python-dotenv
   ```
4. 修改 `app.py` 开头添加：
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## 💰 费用说明

DeepSeek API 按量付费，非常便宜：
- **deepseek-chat**：约 ¥0.14/百万 token
- 每次生成摘要约消耗 1000-3000 tokens
- **每月费用约 ¥1-5 元**（取决于使用频率）

---

## 🎯 功能对比

| 功能 | Ollama 本地 | DeepSeek API | 规则摘要（降级） |
|------|------------|--------------|-----------------|
| AI 深度总结 | ✅ | ✅ | ❌ |
| 需要本地模型 | ✅ | ❌ | ❌ |
| 云端可用 | ❌ | ✅ | ✅ |
| 费用 | 免费 | ¥1-5/月 | 免费 |

---

## ⚠️ 注意事项

1. **API Key 安全**：不要将 API Key 提交到 GitHub！使用环境变量
2. **首次部署**：可能需要几分钟冷启动时间
3. **Render 免费额度**：576小时/月，足够日常使用
4. **自动休眠**：Render 免费版 15 分钟无访问会自动休眠，下次访问需等待 30-60 秒唤醒

---

## 📱 手机访问测试清单

1. ✅ HTTPS 地址（Render 自动提供）
2. ✅ 清除浏览器缓存 + Ctrl+F5 强制刷新
3. ✅ WiFi/4G 网络都试试
4. ✅ 关闭广告拦截器（可能误拦 API 请求）
