@echo off
echo ======================================
echo KouriInstaller һ���������
echo ======================================
echo.

REM ���Python����
echo ���Python����...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ����δ��⵽Python�����Ȱ�װPython���������û���������
    goto END
)

REM ���uv�Ƿ�װ��û����װ
echo ���uv����...
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo uv�Ѱ�װ����������...
    python -m pip install --upgrade uv -i https://mirrors.aliyun.com/pypi/simple/
) else (
    echo δ��⵽uv�����ڰ�װ...
    python -m pip install uv -i https://mirrors.aliyun.com/pypi/simple/
    if %errorlevel% neq 0 (
        echo ���󣺰�װuvʧ�ܣ�����pip�Ƿ���ã�
    )
)

REM ��װ����Python��
echo ��װ��������...
echo ����ʹ��uv��װ��������ʧ���Զ��л�pip��...
uv pip install --system pyinstaller pywin32 pillow requests urllib3
if %errorlevel% neq 0 (
    echo ����uv��װ����ʧ�ܣ�����ʹ��pip...
    python -m pip install pyinstaller pywin32 pillow requests urllib3
    if %errorlevel% neq 0 (
        echo ����������װʧ��
        goto END
    )
)

echo.
echo ���PyInstaller����...

REM ���pyinstaller�Ƿ�װ
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ����δ��⵽pyinstaller�����ڰ�װ���°�...
    python -m pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo ���󣺰�װpyinstallerʧ�ܣ������������ӣ�
        goto END
    )
)

REM ��ȡ��ǰ�ű�Ŀ¼
set "SCRIPT_DIR=%~dp0"

echo ����Ҫ�ļ�...
if not exist "install_all_new.py" (
    echo ����δ�ҵ������� install_all_new.py
    goto END
)

if not exist "cloud_config.json" (
    echo ����δ�ҵ������ļ� cloud_config.json
    goto END
)

if not exist "ui" (
    echo ����δ�ҵ�ui�ļ���
    goto END
)

if not exist "core" (
    echo ����δ�ҵ�core�ļ���
    goto END
)

echo �� �ļ����ͨ��

echo ������ʷ�����ļ�...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo ��ʼ���EXE�ļ�...
echo ������̿�����Ҫ�����ӣ������ĵȴ�...

REM --uac-admin ��Ҫ����ԱȨ��
REM --onefile ���Ϊ���ļ�EXE
REM --icon ����ͼ��
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
    echo ���󣺴�������г������⣬���������Ϣ��
    goto END
)

echo.
echo ������ɵ�EXE�ļ�...
if not exist "dist\KouriInstaller.exe" (
    echo ����δ����EXE�ļ�
    goto END
)

echo ����EXE����ǰĿ¼...
copy /Y "dist\KouriInstaller.exe" "."

if %errorlevel% neq 0 (
    echo ���󣺸���EXEʧ��
    goto END
) else (
    echo �����ɣ��ļ��ѱ�����: %CD%
)

echo.
echo ������ʱ�ļ�...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo �������

echo.
echo ======================================
echo KouriInstaller ������
echo.
echo ʹ��˵��:
echo 1. ˫��"KouriInstaller.exe"������װ��
echo 2. ����ɱ����������������
echo 3. �����ϴ�OSS��ο�GitHub�ĵ�
echo 4. ������������ϵ�����߻��ύissue
echo 5. �������´����ɾ���ɵ�KouriInstaller.exe�������б��ű�
echo ======================================
echo.

:END
pause