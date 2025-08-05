@echo off
chcp 65001
setlocal enabledelayedexpansion

echo ComfyUI 自定义节点安装脚本 (Windows版本)
echo ================================================

:: 获取脚本所在目录的上级目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

:: 检查JSON配置文件（多个可能位置）
set "JSON_CONFIG="
set "USING_JSON=0"

:: 优先级1: 项目根目录
if exist "%PROJECT_ROOT%\custom_nodes.json" (
    set "JSON_CONFIG=%PROJECT_ROOT%\custom_nodes.json"
    set "USING_JSON=1"
    echo 使用JSON配置文件: %PROJECT_ROOT%\custom_nodes.json
) else (
    :: 优先级2: 当前目录
    if exist "custom_nodes.json" (
        set "JSON_CONFIG=custom_nodes.json"
        set "USING_JSON=1"
        echo 使用JSON配置文件: custom_nodes.json
    )
)

if !USING_JSON! equ 1 (
    :: 使用PowerShell解析JSON数组
    powershell -Command "$config = Get-Content '!JSON_CONFIG!' | ConvertFrom-Json; $config | ForEach-Object {Write-Output $_}" > temp_repos.txt
    
) else (
    echo 未找到JSON配置文件，使用默认配置
    
    :: 创建临时仓库列表文件（默认配置）
    echo https://github.com/Comfy-Org/ComfyUI-Manager.git > temp_repos.txt
)

:: 统计仓库数量
set /a "TOTAL_COUNT=0"
for /f %%i in (temp_repos.txt) do (
    set /a "TOTAL_COUNT+=1"
)

echo 将安装 !TOTAL_COUNT! 个自定义节点
echo ================================================

set /a "SUCCESS_COUNT=0"
set /a "CURRENT=0"

:: 克隆所有仓库
for /f "tokens=*" %%i in (temp_repos.txt) do (
    set /a "CURRENT+=1"
    set "URL=%%i"
    
    :: 提取仓库名
    for %%A in ("!URL!") do (
        set "DIRNAME=%%~nA"
        set "DIRNAME=!DIRNAME:.git=!"
    )
    
    echo [!CURRENT!/!TOTAL_COUNT!] 正在处理: !DIRNAME!
    
    :: 检查目标文件夹是否已存在
    if exist "!DIRNAME!" (
        echo   ⚠ 仓库 "!DIRNAME!" 已存在，跳过
        set /a "SUCCESS_COUNT+=1"
    ) else (
        echo   正在克隆到 "!DIRNAME!"
        git clone --depth=1 "!URL!" "!DIRNAME!" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            echo   ✓ !DIRNAME! 克隆成功
            set /a "SUCCESS_COUNT+=1"
        ) else (
            echo   ✗ !DIRNAME! 克隆失败，跳过继续处理
        )
    )
    echo.
)

:: 清理临时文件
del temp_repos.txt >nul 2>&1

echo ================================================
echo 自定义节点安装完成
echo 成功: !SUCCESS_COUNT!/!TOTAL_COUNT!

set /a "FAILED_COUNT=!TOTAL_COUNT! - !SUCCESS_COUNT!"

if !SUCCESS_COUNT! lss !TOTAL_COUNT! (
    echo 警告: 有 !FAILED_COUNT! 个节点安装失败，已跳过
    
    :: 仅在使用默认配置（非JSON）且全部失败时才显示错误
    if !USING_JSON! equ 0 (
        if !SUCCESS_COUNT! equ 0 (
            echo 错误: 所有节点都安装失败，请检查网络连接
            pause
            exit /b 1
        )
    )
) else (
    echo ✓ 所有自定义节点已成功安装
)

echo.
echo 节点安装流程完成。成功安装了 !SUCCESS_COUNT! 个自定义节点。
echo.
echo 使用说明:
echo 要修改节点配置，请编辑 custom_nodes.json 文件
echo JSON格式为简单的URL数组，例如:
echo [
echo   "https://github.com/用户/仓库.git"
echo ]
echo.

pause
