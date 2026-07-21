@echo off
echo ==================================================
echo   AI日报 - 启动中...
echo ==================================================
echo.

cd /d "%~dp0"

echo 正在启动Flask服务...
start /b python app.py

echo 等待Flask服务就绪...
timeout /t 5 /nobreak >nul

echo 正在启动Cloudflare隧道...
cd /d "C:\Program Files (x86)\cloudflared"
start /b cloudflared.exe tunnel --url http://127.0.0.1:5000

echo.
echo 服务已启动！
echo   本地访问: http://127.0.0.1:5000
echo   公网访问: 请查看cloudflared输出中的URL
echo.
echo 按Ctrl+C停止所有服务...
pause