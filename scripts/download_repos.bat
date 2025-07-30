@echo off
chcp 65001
setlocal enabledelayedexpansion

echo ComfyUI 自定义节点安装脚本 (Windows版本)
echo ================================================

:: 检查是否存在JSON配置文件
set "JSON_CONFIG=custom_nodes.json"
if exist "%JSON_CONFIG%" (
    echo 使用JSON配置文件: %JSON_CONFIG%
    
    :: 使用PowerShell解析JSON配置
    powershell -Command "$config = Get-Content '%JSON_CONFIG%' | ConvertFrom-Json; $config.nodes | Where-Object {$_.enabled -eq $true} | ForEach-Object {Write-Output $_.url}" > temp_repos.txt
    
    :: 设置目标目录（从JSON读取，默认为当前目录）
    for /f "tokens=*" %%i in ('powershell -Command "$config = Get-Content '%JSON_CONFIG%' | ConvertFrom-Json; Write-Output $config.target_directory"') do set "TARGET_DIR=%%i"
    if "!TARGET_DIR!"=="null" set "TARGET_DIR=."
    
    echo 目标目录: !TARGET_DIR!
    
) else (
    echo 未找到JSON配置文件，使用默认配置
    
    :: 创建临时仓库列表文件（默认配置）
    (
        echo https://github.com/Comfy-Org/ComfyUI-Manager.git
    ) > temp_repos.txt
    
    set "TARGET_DIR=."
)

:: 统计仓库数量
set /a "TOTAL_COUNT=0"
for /f %%i in (temp_repos.txt) do (
    set /a "TOTAL_COUNT+=1"
)

echo 将安装 !TOTAL_COUNT! 个自定义节点到目录: !TARGET_DIR!
echo ================================================

:: 如果目标目录不是当前目录，则创建并切换
if not "!TARGET_DIR!"=="." (
    if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"
    cd /d "!TARGET_DIR!"
)

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
            echo   ✗ !DIRNAME! 克隆失败
        )
    )
    echo.
)

:: 清理临时文件
del temp_repos.txt >nul 2>&1

echo ================================================
echo 自定义节点安装完成
echo 成功: !SUCCESS_COUNT!/!TOTAL_COUNT!

if !SUCCESS_COUNT! lss !TOTAL_COUNT! (
    echo ⚠ 部分节点安装失败，请检查网络连接或仓库地址
) else (
    echo ✓ 所有自定义节点已成功安装
)

echo.
echo 使用说明:
echo 1. 要修改节点配置，请编辑 custom_nodes.json 文件
echo 2. 要管理节点，请使用: python scripts/manage_nodes.py
echo 3. 支持的操作: add, remove, list, toggle, validate
echo.

pause
