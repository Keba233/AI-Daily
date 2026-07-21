@echo off
chcp 65001 >nul
echo ==================================================
echo AI Daily - Vercel/Render/Railway 部署脚本
echo ==================================================

:: 检查 Git 是否安装
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到 Git，请先安装：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [步骤 1/3] 初始化 Git 仓库...
cd ai-daily
if not exist .git (
    git init
    echo ✓ Git 仓库已创建
) else (
    echo ✓ Git 仓库已存在
)

:: 添加所有文件到暂存区
echo [步骤 2/3] 准备提交代码...
git add .
git commit -m "Initial commit: AI Daily" || git status

echo ==================================================
echo 🚀 部署方式选择：
echo ==================================================
echo   A. Vercel（推荐，永久免费）- https://vercel.com
echo   B. Render（支持 Python Flask）- https://render.com
echo   C. Railway（100h/月免费额度）- https://railway.app
echo   D. 本地运行 + Cloudflare Tunnel（当前方案）
echo ==================================================

set /p choice="请选择部署方式 (A/B/C/D): "

if "%choice%"=="A" goto vercel
if "%choice%"=="B" goto render
if "%choice%"=="C" goto railway
goto local_tunnel

:: Vercel 部署
:vercel
echo ==================================================
echo [Vercel 部署]
echo ==================================================
echo 1. https://vercel.com/new/git/external
echo    - 登录 GitHub 账号
echo    - Import Git Repository → 选择你的 ai-daily 仓库
echo    - Build Command: python app.py
echo    - Output Directory: (留空)
echo    - Deploy!
echo ==================================================
echo ✓ Vercel Web 界面部署说明已显示
goto end

:: Render 部署
:render
echo ==================================================
echo [Render 部署]
echo ==================================================
echo 1. https://dashboard.render.com → New + Blank Web Service
echo    - Connect GitHub Account
echo    - Select your ai-daily repository
echo    - Environment: Python (3.x)
echo    - Build Command: python app.py
echo    - Start Command: gunicorn app:app || python app.py
echo    - Deploy!
echo ==================================================
echo ✓ Render 部署说明已显示
goto end

:: Railway 部署
:railway
echo ==================================================
echo [Railway 部署]
echo ==================================================
echo 1. https://railway.app → New Project → Connect GitHub
echo    - Select your ai-daily repository
echo    - Add service: Python (Flask)
echo    - Railway will auto-detect requirements.txt
echo    - Deploy!
echo ==================================================
echo ✓ Railway 部署说明已显示
goto end

:: Cloudflare Tunnel（本地方案）
:local_tunnel
echo ==================================================
echo [Cloudflare Tunnel]
echo ==================================================
echo ⚠️  Windows 需要安装 cloudflared：https://github.com/cloudflare/cloudflared/releases/latest
echo    - 下载并解压到 C:\cloudflared-windows-amd64.exe
echo    - 运行命令: cloudflared tunnel --url http://127.0.0.1:5000 run
echo ==================================================
echo ✓ Cloudflare Tunnel 说明已显示

:: 启动本地服务并创建隧道（如果安装了 cloudflared）
where cloudflared >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [步骤 3/3] 启动 Flask + Cloudflare Tunnel...
    start http://127.0.0.1:5000
    cd ai-daily
    python app.py ^&^& cloudflared tunnel --url http://127.0.0.1:5000 run
    
) else (
    echo [提示] 未检测到 cloudflared，仅启动 Flask...
    start http://127.0.0.1:5000
    cd ai-daily
    python app.py
)

:end
echo ==================================================
echo ✓ 部署脚本执行完成！
echo ==================================================
pause