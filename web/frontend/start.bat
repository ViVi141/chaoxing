@echo off
chcp 65001 >nul
echo ========================================
echo   超星学习通Web平台 - 前端启动脚本
echo ========================================
echo.

cd /d %~dp0

REM 检查node_modules是否存在
if not exist "node_modules" (
    echo [1/2] 安装依赖...
    echo.
    
    REM 检查是否安装了pnpm
    where pnpm >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 使用pnpm安装依赖...
        pnpm install
    ) else (
        echo pnpm未安装，使用npm安装依赖...
        npm install
    )
    
    if errorlevel 1 (
        echo ❌ 依赖安装失败！
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
    echo.
)

echo [2/2] 启动开发服务器...
echo.
echo ========================================
echo   服务信息
echo ========================================
echo   前端地址: http://localhost:5173
echo   API代理: http://localhost:8000
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 检查是否安装了pnpm
where pnpm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    pnpm dev
) else (
    npm run dev
)

pause

