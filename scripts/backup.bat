@echo off
chcp 65001 >nul
REM Windows数据库备份脚本
REM 用途：定期备份SQLite数据库
REM 使用：backup.bat

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
set "BACKUP_DIR=%PROJECT_ROOT%\backups"
set "DB_FILE=%PROJECT_ROOT%\web\backend\data\chaoxing.db"

REM 生成时间戳
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%"
set "DATE=%datetime:~0,8%"

REM 创建备份目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [*] 开始备份数据库...

REM 检查数据库文件是否存在
if not exist "%DB_FILE%" (
    echo [!] 数据库文件不存在: %DB_FILE%
    exit /b 1
)

REM 备份文件名
set "BACKUP_FILE=%BACKUP_DIR%\chaoxing_%TIMESTAMP%.db"

REM 复制数据库文件
copy "%DB_FILE%" "%BACKUP_FILE%" >nul
if %errorlevel% equ 0 (
    echo [+] 备份成功: %BACKUP_FILE%
) else (
    echo [!] 备份失败
    exit /b 1
)

REM 使用7-Zip压缩（如果可用）
where 7z >nul 2>&1
if %errorlevel% equ 0 (
    7z a -tgzip "%BACKUP_FILE%.gz" "%BACKUP_FILE%" >nul
    if %errorlevel% equ 0 (
        del "%BACKUP_FILE%"
        echo [+] 压缩成功: %BACKUP_FILE%.gz
    )
)

REM 删除7天前的备份
forfiles /P "%BACKUP_DIR%" /S /M chaoxing_*.db* /D -7 /C "cmd /c del @path" 2>nul
if %errorlevel% equ 0 (
    echo [+] 已删除7天前的旧备份
)

echo.
echo [OK] 备份完成
echo.
echo 定时任务设置（可选）：
echo 1. 打开"任务计划程序"
echo 2. 创建基本任务
echo 3. 触发器：每天凌晨2点
echo 4. 操作：启动程序 - %~f0
echo.

endlocal

