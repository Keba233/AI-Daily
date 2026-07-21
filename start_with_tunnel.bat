@echo off
chcp 65001 >nul 2>&1
title AI日报 - Flask + Cloudflare Tunnel

echo ==================================================
echo   AI日报 - 一键启动（含公网访问）
echo ==================================================
echo.

cd /d "%~dp0"

echo [1/3] 正在启动Flask服务...
start "AI日报-Flask" /min cmd /c "python app.py"

echo [2/3] 等待Flask服务就绪（10秒）...
timeout /t 10 /nobreak >nul

echo [3/3] 正在启动Cloudflare隧道...
echo.
echo ============================================================
echo   公网URL将在下方显示，请复制到手机浏览器访问
echo   每次重启URL会变化，请注意更新
echo ============================================================
echo.

cd /d "C:\Program Files (x86)\cloudflared"
cloudflared.exe tunnel --url http://127.0.0.1:5000

echo.
echo 隧道已断开，按任意键退出...
pause >nul