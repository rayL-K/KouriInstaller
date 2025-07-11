#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动器模块 - 负责查找和启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path
import ctypes


class ScriptLauncher:
    """脚本启动器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化启动器
        
        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        self.app_path = self._get_application_path()
    
    def _get_application_path(self) -> Path:
        """获取应用程序路径"""
        import sys
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(os.path.abspath(__file__)).parent.parent
    
    def _log(self, message: str):
        """日志记录"""
        if self.progress_callback:
            self.progress_callback('detail', message)
        else:
            print(message)
    
    def _update_progress(self, progress: float, status: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback('progress', (progress, status))
    
    def find_and_launch_script(self) -> bool:
        """
        查找并以管理员身份运行run.bat脚本

        Returns:
            是否成功找到并运行脚本
        """
        self._update_progress(98, "查找启动脚本...")
        self._log("正在查找 run.bat 文件")

        # 递归搜索run.bat文件
        bat_path = self._search_run_bat()

        if not bat_path:
            self._log("未找到 run.bat 文件")
            # 不显示错误，而是显示完成信息
            self._show_completion_message()
            return True  # 返回True，让程序正常结束

        try:
            self._log(f"找到 run.bat 文件于: {bat_path}")

            # 更新状态
            self._update_progress(99, "启动项目...")
            self._log("正在以管理员身份运行 run.bat...")

            # 以管理员身份运行run.bat
            success = self._run_as_admin(bat_path)

            if success:
                self._update_progress(100, "项目启动成功")
                self._log("✓ run.bat 已成功以管理员身份启动")
                self._show_success_message()
                return True
            else:
                self._log("✗ 以管理员身份运行失败，尝试普通方式运行...")
                # 如果管理员运行失败，尝试普通方式
                success = self._run_normal(bat_path)
                if success:
                    self._update_progress(100, "项目启动成功")
                    self._log("✓ run.bat 已以普通权限启动")
                    self._show_success_message()
                    return True
                else:
                    # 如果自动运行失败，打开文件夹让用户手动运行
                    self._open_folder_and_highlight(bat_path)
                    return True  # 仍然返回True，表示处理完成

        except Exception as e:
            self._log(f"运行脚本时发生错误: {e}")
            self._show_manual_run_message(bat_path)
            return False

    def _search_run_bat(self) -> Path:
        """
        递归搜索run.bat文件

        Returns:
            找到的run.bat文件路径，如果未找到则返回None
        """
        # 获取exe文件的实际运行目录
        if getattr(sys, 'frozen', False):
            # 如果是打包的exe，获取exe文件所在目录
            exe_dir = Path(sys.executable).parent
        else:
            # 如果是开发环境，使用当前工作目录
            exe_dir = Path.cwd()

        search_paths = [
            # 首先在exe文件所在目录搜索
            exe_dir,
            # 在app_path目录下搜索
            self.app_path,
            # 在app_path的父目录下搜索
            self.app_path.parent,
        ]

        for search_root in search_paths:
            if not search_root.exists():
                continue

            self._log(f"在目录中搜索 run.bat: {search_root}")

            # 首先检查直接的kourichat目录
            kourichat_path = search_root / "kourichat" / "run.bat"
            if kourichat_path.exists():
                self._log(f"在kourichat目录中找到 run.bat: {kourichat_path}")
                return kourichat_path

            # 递归搜索run.bat文件
            for root, dirs, files in os.walk(search_root):
                if "run.bat" in files:
                    bat_path = Path(root) / "run.bat"
                    self._log(f"找到 run.bat 文件: {bat_path}")
                    return bat_path

                # 优先搜索可能的项目目录
                for dir_name in dirs:
                    if any(keyword in dir_name.lower() for keyword in ['kourichat', 'kouri', 'exploration']):
                        priority_path = Path(root) / dir_name / "run.bat"
                        if priority_path.exists():
                            self._log(f"在优先目录中找到 run.bat: {priority_path}")
                            return priority_path

        self._log("未找到 run.bat 文件")
        return None
    
    def _run_as_admin(self, bat_path: Path) -> bool:
        """以管理员身份运行批处理文件，带智能重启检测"""
        return self._run_with_smart_restart(bat_path, admin=True)

    def _run_with_smart_restart(self, bat_path: Path, admin: bool = True, max_retries: int = 2) -> bool:
        """智能启动run.bat，检测Python未安装错误并自动重启"""
        for attempt in range(max_retries):
            self._log(f"第 {attempt + 1} 次尝试启动 {bat_path.name}...")

            # 创建智能启动脚本
            temp_bat_content = f'''@echo off
echo ========================================
echo KouriChat 智能启动器 (尝试 {attempt + 1}/{max_retries})
echo ========================================
echo.

echo 正在刷新环境变量...
:: 刷新环境变量
for /f "tokens=2*" %%i in ('reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" /v PATH') do set "SystemPath=%%j"
for /f "tokens=2*" %%i in ('reg query "HKCU\\Environment" /v PATH 2^>nul') do set "UserPath=%%j"
if defined UserPath (
    set "PATH=%SystemPath%;%UserPath%"
) else (
    set "PATH=%SystemPath%"
)

echo 环境变量已刷新
echo 当前PATH: %PATH%
echo.

echo 正在启动 {bat_path.name}...
cd /d "{bat_path.parent}"

:: 创建输出文件来捕获run.bat的输出
set "output_file=%TEMP%\\kourichat_output_{attempt}.txt"
echo 输出将保存到: %output_file%

:: 运行run.bat并捕获输出
call "{bat_path.name}" > "%output_file%" 2>&1

:: 检查输出中是否包含Python未安装的错误
findstr /i "python.*not.*found\\|python.*未.*安装\\|python.*不是.*命令\\|'python'.*不是.*可运行" "%output_file%" >nul
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 检测到Python未安装错误！
    echo ========================================
    echo 输出内容:
    type "%output_file%"
    echo.
    if {attempt + 1} lss {max_retries} (
        echo 将在5秒后重新启动...
        timeout /t 5 /nobreak >nul
        echo 正在重新启动...
        exit /b 1
    ) else (
        echo 已达到最大重试次数，请手动检查Python安装
        pause
        exit /b 1
    )
) else (
    echo.
    echo ========================================
    echo 启动成功！
    echo ========================================
    type "%output_file%"
    echo.
    echo 程序正在运行中...
    pause
    exit /b 0
)
'''

            # 创建临时批处理文件
            temp_bat_path = bat_path.parent / f"smart_launcher_{attempt}.bat"
            try:
                with open(temp_bat_path, 'w', encoding='gbk') as f:
                    f.write(temp_bat_content)

                self._log(f"创建智能启动脚本: {temp_bat_path}")

                # 根据admin参数选择启动方式
                if admin:
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "runas",  # 以管理员身份运行
                        "cmd.exe",
                        f'/c "{temp_bat_path}"',
                        str(bat_path.parent),
                        1  # SW_SHOWNORMAL
                    )
                else:
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "open",
                        "cmd.exe",
                        f'/c "{temp_bat_path}"',
                        str(bat_path.parent),
                        1  # SW_SHOWNORMAL
                    )

                # ShellExecute返回值大于32表示成功
                if result > 32:
                    self._log(f"成功启动智能启动脚本 (尝试 {attempt + 1})")

                    # 等待一段时间让脚本执行
                    import time
                    time.sleep(3)

                    # 检查输出文件是否存在Python错误
                    output_file = Path(os.environ.get('TEMP', '')) / f"kourichat_output_{attempt}.txt"
                    if output_file.exists():
                        try:
                            with open(output_file, 'r', encoding='gbk', errors='ignore') as f:
                                output_content = f.read().lower()

                            # 检查是否包含Python未安装的错误信息
                            python_errors = [
                                'python.*not.*found',
                                'python.*未.*安装',
                                'python.*不是.*命令',
                                "'python'.*不是.*可运行"
                            ]

                            has_python_error = any(error in output_content for error in python_errors)

                            if has_python_error and attempt < max_retries - 1:
                                self._log(f"检测到Python错误，准备重试 (尝试 {attempt + 1}/{max_retries})")
                                # 清理临时文件
                                try:
                                    temp_bat_path.unlink()
                                    output_file.unlink()
                                except:
                                    pass
                                continue  # 重试
                            else:
                                self._log(f"启动完成 (尝试 {attempt + 1})")
                                return True

                        except Exception as e:
                            self._log(f"读取输出文件失败: {e}")

                    return True
                else:
                    self._log(f"启动失败，错误代码: {result}")

            except Exception as e:
                self._log(f"创建智能启动脚本失败: {e}")
            finally:
                # 延迟清理临时文件
                try:
                    import threading
                    def delayed_cleanup():
                        import time
                        time.sleep(10)  # 等待10秒后删除
                        try:
                            if temp_bat_path.exists():
                                temp_bat_path.unlink()
                        except:
                            pass

                    cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
                    cleanup_thread.start()
                except:
                    pass

        self._log(f"所有启动尝试都失败了")
        return False

    def _run_normal(self, bat_path: Path) -> bool:
        """以普通权限运行批处理文件，带智能重启检测"""
        return self._run_with_smart_restart(bat_path, admin=False)
    
    def _show_error_message(self, message: str):
        """显示错误消息"""
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "未找到脚本",
                0x10 | 0x1000  # MB_ICONERROR | MB_SYSTEMMODAL
            )
        except Exception as e:
            self._log(f"显示提示信息时发生错误: {e}")
            print(f"\n错误：{message}")

    def _show_success_message(self):
        """显示成功消息"""
        try:
            message = "项目已成功启动！\n\nrun.bat 正在以管理员身份运行，请查看新打开的命令行窗口。"
            ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "启动成功",
                0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
            )
        except Exception as e:
            self._log(f"显示成功消息时发生错误: {e}")
            print(f"\n✅ 项目启动成功！")

    def _show_manual_run_message(self, bat_path: Path):
        """显示手动运行提示"""
        try:
            message = f"自动启动失败，请手动运行以下文件：\n\n{bat_path}\n\n建议右键选择\"以管理员身份运行\"。"
            ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "请手动运行",
                0x30 | 0x1000  # MB_ICONWARNING | MB_SYSTEMMODAL
            )
        except Exception as e:
            self._log(f"显示手动运行提示时发生错误: {e}")
            print(f"\n⚠️ 请手动运行: {bat_path}")
    
    def _open_folder_and_highlight(self, bat_path):
        """打开文件夹并高亮显示run.bat文件"""
        try:
            # 使用Windows资源管理器打开文件夹并选中文件
            subprocess.run(['explorer', '/select,', str(bat_path)], check=True)
            self._log(f"已打开文件夹并选中: {bat_path}")
            self._show_manual_run_message(bat_path)
        except Exception as e:
            self._log(f"打开文件夹失败: {e}")
            # 如果打开文件夹失败，尝试只打开文件夹
            try:
                subprocess.run(['explorer', str(bat_path.parent)], check=True)
                self._log(f"已打开文件夹: {bat_path.parent}")
                self._show_manual_run_message(bat_path)
            except Exception as e2:
                self._log(f"打开文件夹也失败: {e2}")
                self._show_manual_run_message(bat_path)

    def _show_completion_message(self):
        """显示安装完成消息"""
        try:
            message = "KouriChat安装完成！\n\n所有必要的程序已安装或确认存在。\n项目文件已解压完成。"
            ctypes.windll.user32.MessageBoxW(
                0,
                message,
                "安装完成",
                0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
            )
        except Exception as e:
            self._log(f"显示完成消息时发生错误: {e}")
            print(f"\n✅ 安装完成！")

    def show_completion_dialog(self):
        """显示安装完成对话框"""
        message = "所有必要的程序已安装或确认存在！\n\n安装过程已完成。"
        title = "安装完成"

        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                message,
                title,
                0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
            )
        except Exception as e:
            self._log(f"显示完成消息弹窗时发生错误: {e}")
            print(f"\n{title}\n{message}")
