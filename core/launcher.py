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

            # 等待Python环境变量生效
            self._update_progress(95, "等待Python环境生效...")
            self._wait_for_python_env()

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
    
    def _wait_for_python_env(self) -> bool:
        """等待Python环境变量生效"""
        import time
        import subprocess

        self._log("等待Python环境变量生效...")
        max_wait_time = 30  # 最大等待30秒
        check_interval = 2  # 每2秒检查一次

        for i in range(0, max_wait_time, check_interval):
            try:
                # 刷新当前进程的环境变量
                self._refresh_environment()

                # 检查Python是否可用
                result = subprocess.run(['python', '--version'],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)

                if result.returncode == 0:
                    python_version = result.stdout.strip()
                    self._log(f"✓ Python环境已生效: {python_version}")
                    return True

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass

            self._log(f"等待Python环境生效... ({i + check_interval}/{max_wait_time}秒)")
            time.sleep(check_interval)

        self._log("⚠ Python环境变量等待超时，将尝试直接启动")
        return False

    def _refresh_environment(self):
        """刷新当前进程的环境变量"""
        try:
            import winreg

            # 读取系统环境变量
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                system_path = winreg.QueryValueEx(key, "PATH")[0]

            # 读取用户环境变量
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                    user_path = winreg.QueryValueEx(key, "PATH")[0]
                    combined_path = f"{system_path};{user_path}"
            except FileNotFoundError:
                combined_path = system_path

            # 更新当前进程的PATH环境变量
            os.environ["PATH"] = combined_path
            self._log("已刷新环境变量")

        except Exception as e:
            self._log(f"刷新环境变量失败: {e}")

    def _run_as_admin(self, bat_path: Path) -> bool:
        """以管理员身份运行批处理文件"""
        try:
            # 使用ShellExecute以管理员身份运行
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # 以管理员身份运行
                "cmd.exe",
                f'/c "cd /d "{bat_path.parent}" && "{bat_path.name}""',
                str(bat_path.parent),
                1  # SW_SHOWNORMAL
            )

            # ShellExecute返回值大于32表示成功
            if result > 32:
                self._log(f"成功以管理员身份启动: {bat_path}")
                return True
            else:
                self._log(f"以管理员身份运行失败，错误代码: {result}")
                return False

        except Exception as e:
            self._log(f"以管理员身份运行时发生异常: {e}")
            return False

    def _run_normal(self, bat_path: Path) -> bool:
        """以普通权限运行批处理文件"""
        try:
            # 使用subprocess运行
            process = subprocess.Popen(
                [str(bat_path)],
                cwd=str(bat_path.parent),
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            self._log(f"成功以普通权限启动: {bat_path} (PID: {process.pid})")
            return True

        except Exception as e:
            self._log(f"以普通权限运行时发生异常: {e}")
            return False
    
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
