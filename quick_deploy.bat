@echo off
chcp 65001 >nul
cd ai-daily

:: 配置 Git 用户信息（如果未设置）
git config --global user.email "your-email@example.com" 2>nul
git config --global user.name "Your Name" 2>nul

:: 初始化并提交
if not exist .git (git init)
git add .
git commit -m "Initial commit: AI Daily" >nul

echo ==================================================
echo 🚀 Vercel/Render/Railway 部署指南
echo ==================================================
echo 
echo ✅ Git 仓库已准备就绪！
echo 
echo 📋 下一步操作：
echo ==================================================
echo 
echo   【方案 A】Vercel（推荐，永久免费）:
echo     1. https://vercel.com/new/git/external
echo        → 登录 GitHub 账号
echo        → Import Git Repository → 选择 ai-daily 仓库
echo        → Build Command: python app.py
echo        → Output Directory: (留空)
echo        → Deploy! ✓
echo 
echo   【方案 B】Render（支持 Python Flask）:
echo     https://dashboard.render.com/new/blank-web-service
echo       - Connect GitHub Account
echo       - Select ai-daily repository  
echo       - Environment: Python 3.x
echo       - Build Command: python app.py
echo       - Start Command: gunicorn app:app || python app.py
echo 
echo   【方案 C】Railway（100h/月免费）:
echo     https://railway.app/new/github
echo       - Connect GitHub → Select ai-daily
echo       - Railway 自动检测 requirements.txt
echo       
echo ==================================================
echo 
echo 💡 Vercel 部署后，您将获得永久公网 URL！
echo    例如：https://ai-daily.vercel.app
echo 
pause