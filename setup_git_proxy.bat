@echo off
echo 配置Git代理...

REM 请根据您的代理配置修改以下参数
set PROXY_HOST=127.0.0.1
set PROXY_PORT=7890
set PROXY_TYPE=http

echo 当前代理配置: %PROXY_TYPE%://%PROXY_HOST%:%PROXY_PORT%

REM 配置Git代理
git config --global http.proxy %PROXY_TYPE%://%PROXY_HOST%:%PROXY_PORT%
git config --global https.proxy %PROXY_TYPE%://%PROXY_HOST%:%PROXY_PORT%

REM 也可以只为GitHub配置
REM git config --global http.https://github.com.proxy %PROXY_TYPE%://%PROXY_HOST%:%PROXY_PORT%
REM git config --global https.https://github.com.proxy %PROXY_TYPE%://%PROXY_HOST%:%PROXY_PORT%

REM 配置其他Git设置优化网络
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

echo Git代理配置完成！
echo.
echo 当前Git配置:
git config --global --get http.proxy
git config --global --get https.proxy

echo.
echo 如果需要取消代理，运行:
echo git config --global --unset http.proxy
echo git config --global --unset https.proxy

pause 