@echo off
echo 取消Git代理配置...

REM 取消全局代理
git config --global --unset http.proxy
git config --global --unset https.proxy

REM 取消GitHub特定代理
git config --global --unset http.https://github.com.proxy
git config --global --unset https.https://github.com.proxy

echo Git代理配置已清除！
echo.
echo 当前Git代理配置:
git config --global --get http.proxy
git config --global --get https.proxy

if "%1"=="nopause" goto :eof
pause 