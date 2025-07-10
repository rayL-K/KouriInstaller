@echo off
echo ======================================
echo KouriInstaller 一键打包工具
echo ======================================
echo.

REM 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python，请先安装Python环境并配置环境变量！
    goto END
)

REM 检查uv是否安装，没有则安装
echo 检查uv环境...
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo uv已安装，尝试升级...
    python -m pip install --upgrade uv -i https://mirrors.aliyun.com/pypi/simple/
) else (
    echo 未检测到uv，正在安装...
    python -m pip install uv -i https://mirrors.aliyun.com/pypi/simple/
    if %errorlevel% neq 0 (
        echo 错误：安装uv失败，请检查pip是否可用！
    )
)

REM 安装依赖Python包
echo 安装依赖包中...
echo 优先使用uv安装依赖（如失败自动切换pip）...
uv pip install --system pyinstaller pywin32 pillow requests urllib3
if %errorlevel% neq 0 (
    echo 错误：uv安装依赖失败，尝试使用pip...
    python -m pip install pyinstaller pywin32 pillow requests urllib3
    if %errorlevel% neq 0 (
        echo 错误：依赖安装失败
        goto END
    )
)

echo.
echo 检查PyInstaller环境...

REM 检查pyinstaller是否安装
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到pyinstaller，正在安装最新版...
    python -m pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo 错误：安装pyinstaller失败，请检查网络连接！
        goto END
    )
)

REM 获取当前脚本目录
set "SCRIPT_DIR=%~dp0"

echo 检查必要文件...
if not exist "install_all_new.py" (
    echo 错误：未找到主程序 install_all_new.py
    goto END
)

if not exist "cloud_config.json" (
    echo 错误：未找到配置文件 cloud_config.json
    goto END
)

if not exist "ui" (
    echo 错误：未找到ui文件夹
    goto END
)

if not exist "core" (
    echo 错误：未找到core文件夹
    goto END
)

echo √ 文件检查通过

echo 清理历史构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo 开始打包EXE文件...
echo 打包过程可能需要几分钟，请耐心等待...

REM --uac-admin 需要管理员权限
REM --onefile 打包为单文件EXE
REM --icon 设置图标
python -m PyInstaller --onefile ^
            --noconsole ^
            --uac-admin ^
            --name "KouriInstaller" ^
            --clean ^
            --icon "final_exe\KouriInstaller_ico.ico" ^
            --specpath "." ^
            --workpath "." ^
            --distpath ".\dist" ^
            --add-data "cloud_config.json;." ^
            --add-data "final_exe\title.ico;final_exe" ^
            --add-data "final_exe\KouriInstaller_ico.ico;final_exe" ^
            --add-data "final_exe\MenuZhizhi.png;final_exe" ^
            --hidden-import "tkinter" ^
            --hidden-import "tkinter.ttk" ^
            --hidden-import "winreg" ^
            --hidden-import "ctypes.wintypes" ^
            install_all_new.py

if %errorlevel% neq 0 (
    echo 错误：打包过程中出现问题，请检查输出信息！
    goto END
)

echo.
echo 检查生成的EXE文件...
if not exist "dist\KouriInstaller.exe" (
    echo 错误：未生成EXE文件
    goto END
)

echo 复制EXE到当前目录...
copy /Y "dist\KouriInstaller.exe" "."

if %errorlevel% neq 0 (
    echo 错误：复制EXE失败
    goto END
) else (
    echo 打包完成，文件已保存至: %CD%
)

echo.
echo 清理临时文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo 清理完成

echo.
echo ======================================
echo KouriInstaller 打包完成
echo.
echo 使用说明:
echo 1. 双击"KouriInstaller.exe"启动安装器
echo 2. 如遇杀毒软件误报请添加信任
echo 3. 若需上传OSS请参考GitHub文档
echo 4. 如遇问题请联系开发者或提交issue
echo 5. 若需重新打包请删除旧的KouriInstaller.exe后再运行本脚本
echo ======================================
echo.

:END
pause