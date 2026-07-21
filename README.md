# AI Daily - 部署指南

## 🚀 推荐平台：Render（免费，永久运行）

### **为什么选择 Render？**
- ✅ **支持 Python Flask**
- ✅ **576小时/月免费额度**（足够日常使用）
- ✅ **自动 HTTPS + CDN加速**
- ✅ **GitHub集成，代码更新自动部署**

---

## 📋 快速部署步骤

### **1. 访问 Render Dashboard**
```bash
https://dashboard.render.com/new/static-web-site
或
https://dashboard.render.com/new/web-service
```

### **2. 连接 GitHub 仓库**
- Connect a new Git repository
- 选择 `Keba233/AI-Daily`

---

## 🎯 Render Web Service配置（推荐）

| 配置项 | 值 |
|--------|-----|
| **Name** | ai-daily (或自定义) |
| **Region** | 任意（建议上海/东京） |
| **Branch** | `master` |
| **Environment** | `Python` (3.x) |
| **Build Command** | ````pip install -r requirements.txt```` |
| **Start Command** | ````python app.py```` 或 ````gunicorn app:app --bind 0.0.0.0:5000```` |

### ✅ 点击 Deploy！

Render会自动：
1. 安装依赖（requirements.txt）
2. 启动 Flask应用
3. 生成公网 URL，例如：`https://ai-daily.onrender.com`

---

## 🎯 Render Static Site配置（备选方案）

如果 Vercel部署成功但手机无法访问，可能是跨域问题。尝试静态站点模式：

### **创建构建脚本**
```bash
# 将项目改为纯静态 HTML + API分离
mkdir api && cd api
echo "from ai_daily.app import create_app; app = create_app(); app.run(port=5000)" > server.py
pip install flask -r ../requirements.txt
python server.py &

cd ..
```

### **Render配置：**
- **Build Command:** ````npm install && python app.py````（混合部署）
- **Start Command:** ````gunicorn api.server:app --bind 0.0.0.0:$PORT````

---

## 📱 手机访问问题排查

### ✅ Vercel/Render部署后：
1. **清除浏览器缓存** - 强制刷新（Ctrl+F5）
2. **更换网络测试** - WiFi/4G都试试
3. **检查防火墙** - 某些公司网络可能拦截非HTTPS站点
4. **DNS预解析** - https://www.google.com/search?q=ai-daily.onrender.com

### ⚠️ Vercel跨域限制：
如果手机访问报错 CORS，需要添加 headers（已在 `.vercel.json`配置）

---

## 🔄 本地运行 + Cloudflare Tunnel（当前方案）

**优点：**
- ✅ **完全免费无额度限制**
- ✅ HTTPS加密
- ✅ 一次部署长期使用

**缺点：**
- ❌ 需保持电脑开机
- ❌ URL每次重启变化

### **一键启动脚本：**
```bash
start_with_tunnel.bat
```

---

## 🎯 推荐方案对比

| 平台 | 免费额度 | Python支持 | HTTPS | CDN | 难度 |
|------|---------|-----------|-------|-----|------|
| **Render** | ✓576h/月 | ✅原生支持 | ✅自动 | ✅有 | ⭐⭐ |
| Vercel | ✓永久免费 | ❌需特殊配置 | ✅自动 | ✅有 | ⭐⭐⭐（Flask不支持）|
| Railway | ✗100h/月 | ✅Python专用 | ✅自动 | ✅有 | ⭐⭐ |
| Cloudflare Tunnel | ✓完全免费 | - | ✅自签名 | ❌无 | ⭐⭐⭐（需电脑开机）|

---

## 🚀 立即部署到 Render

### **步骤一：**访问 Render Dashboard
```bash
https://dashboard.render.com/new/web-service
```

### **步骤二：**连接 GitHub
1. Connect a new Git repository
2. Select `Keba233/AI-Daily`

### **步骤三：**配置环境（自动检测）
- Environment: Python 3.x
- Build Command: ````pip install -r requirements.txt````  
- Start Command: ````python app.py````

### **步骤四：**Deploy！✅

Render会自动部署并生成 URL，例如：
```bash
https://ai-daily.onrender.com
```

---

## 📱 手机访问测试清单

1. ✅ HTTPS地址（非HTTP）
2. ✅ 清除浏览器缓存 + Ctrl+F5强制刷新
3. ✅ WiFi/4G网络都试试
4. ✅ DNS预解析：https://www.google.com/search?q=你的域名
5. ✅ 关闭广告拦截器（可能误拦API请求）

---

## 🎯 当前状态确认

**请告诉我：**
1. Vercel部署的URL是什么？
2. 手机访问时具体报错什么内容？
3. 电脑浏览器能正常打开吗？

根据反馈，我会帮您调整到最佳方案！🚀