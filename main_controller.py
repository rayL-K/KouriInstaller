#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控制器 - 协调各个模块的工作
"""

import sys
import time
import ctypes
from pathlib import Path
from typing import List

# 导入各个模块
from ui.progress_window import ProgressWindow
from core.cloud_downloader import CloudDownloader
from core.system_checker import SystemChecker
from core.installer import SoftwareInstaller
from core.launcher import ScriptLauncher
from core.hot_updater import HotUpdater


class InstallationController:
    """安装控制器 - 负责协调整个安装流程"""
    
    def __init__(self):
        """初始化控制器"""
        self.progress_window = None
        self.cloud_downloader = None
        self.system_checker = None
        self.installer = None
        self.launcher = None
        self.hot_updater = None
        
        self._setup_components()
    
    def _setup_components(self):
        """设置各个组件"""
        # 创建进度窗口
        self.progress_window = ProgressWindow("KouriChat安装向导")
        
        # 创建进度回调函数
        def progress_callback(callback_type: str, data):
            if callback_type == 'progress':
                progress, status = data
                self.progress_window.set_progress(progress, status)
            elif callback_type == 'detail':
                self.progress_window.update_detail(data)
        
        # 初始化各个模块
        self.cloud_downloader = CloudDownloader(progress_callback)
        self.system_checker = SystemChecker(progress_callback)
        self.installer = SoftwareInstaller(progress_callback)
        self.launcher = ScriptLauncher(progress_callback)
        self.hot_updater = HotUpdater(progress_callback)
        
        # 初始状态
        self.progress_window.set_progress(0, "正在初始化云端安装程序...")
        self.progress_window.update_detail("欢迎使用云端软件安装向导")
        self.progress_window.keep_alive()
    
    def check_admin_privileges(self) -> bool:
        """检查管理员权限"""
        if not self.system_checker.check_admin_privileges():
            self.progress_window.update_detail("警告：当前程序未以管理员权限运行，这可能导致安装失败")
            
            if getattr(sys, 'frozen', False):
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0, 
                        "请右键点击程序，选择'以管理员身份运行'", 
                        "需要管理员权限", 
                        0x10
                    )
                except:
                    pass
                return False
            else:
                self.progress_window.update_detail("建议使用管理员权限重新运行")
                print("\n警告：未以管理员权限运行，安装可能失败。建议使用管理员权限重新运行。\n")
        
        return True
    
    def download_packages(self, skip_python: bool = False, skip_wechat: bool = False) -> List[Path]:
        """下载安装包"""
        self.progress_window.update_detail("开始云端下载流程")

        try:
            downloaded_files = self.cloud_downloader.download_packages(skip_python, skip_wechat)
            if downloaded_files:
                self.progress_window.update_detail(f"✓ 云端下载成功，获得 {len(downloaded_files)} 个安装包")
                return downloaded_files
            else:
                self.progress_window.update_detail("✗ 云端下载失败，没有获取到任何安装包")
                return []
        except Exception as e:
            self.progress_window.update_detail(f"✗ 云端下载错误: {str(e)}")
            return []
    
    def install_packages(self, downloaded_items: List[Path]) -> bool:
        """安装软件包"""
        if not downloaded_items:
            return False

        # 分离可执行文件和其他文件
        exe_files = [f for f in downloaded_items if f.is_file() and f.suffix.lower() == '.exe']
        other_items = [f for f in downloaded_items if f not in exe_files]

        self.progress_window.set_progress(20, f"云端获取到 {len(downloaded_items)} 个项目")

        # 显示下载的内容
        download_info = []
        for item in downloaded_items:
            if item.is_file():
                download_info.append(f"文件: {item.name}")
            elif item.is_dir():
                download_info.append(f"目录: {item.name}")

        self.progress_window.update_detail(f"云端下载完成: {', '.join(download_info)}")

        # 如果没有可执行文件，跳过安装步骤
        if not exe_files:
            self.progress_window.set_progress(90, "没有需要安装的程序")
            self.progress_window.update_detail("所有下载项目都是数据文件，跳过安装步骤")
            return True

        success_count = 0
        total_count = len(exe_files)

        # 优先安装Python
        python_exe = next((f for f in exe_files if "python" in f.name.lower()), None)
        other_exes = [f for f in exe_files if f != python_exe]
        ordered_exes = ([python_exe] if python_exe else []) + other_exes

        for i, exe_file in enumerate(ordered_exes):
            # 计算进度 (从20%开始，到85%结束)
            base_progress = 20
            install_progress = (i / total_count) * 65
            current_progress = base_progress + install_progress

            progress_text = f"正在处理: {exe_file.name} ({i+1}/{total_count})"
            self.progress_window.set_progress(current_progress, progress_text)
            self.progress_window.update_detail(f"开始处理 {exe_file.name}")

            install_successful = self.installer.install_software(exe_file)

            if install_successful:
                success_count += 1
                self.progress_window.update_detail(f"✓ {exe_file.name} 处理成功")
            else:
                self.progress_window.update_detail(f"✗ {exe_file.name} 处理失败")

            # 更新完成进度
            completed_progress = base_progress + ((i + 1) / total_count) * 65
            self.progress_window.set_progress(completed_progress)

            # 确保UI保持响应
            self.progress_window.force_update()
        
        # 最终状态
        all_success = success_count == total_count
        if all_success:
            self.progress_window.set_progress(100, "所有程序安装完成")
            self.progress_window.update_detail(f"✓ 安装完成: {success_count}/{total_count} 个程序成功处理")
        else:
            self.progress_window.set_progress(90, "安装完成（部分失败）")
            self.progress_window.update_detail(f"⚠ 安装完成: {success_count}/{total_count} 个程序成功处理")
        
        # 短暂显示最终状态，但保持UI响应
        for _ in range(10):  # 1秒分成10个100ms的片段
            if self.progress_window and not self.progress_window.closed:
                self.progress_window.force_update()
                time.sleep(0.1)
            else:
                break
        
        return all_success
    
    def post_install_tasks(self):
        """安装后任务"""
        # 等待Python环境变量生效（如果Python被安装了）
        if self.installer.python_installed:
            self.progress_window.update_detail("Python安装/检查成功，等待环境变量生效...")
            self.installer.wait_for_python_env_vars()

        # 无论Python是否安装，都尝试查找并启动脚本
        self.progress_window.update_detail("查找并启动 run.bat 脚本...")
        if self.launcher.find_and_launch_script():
            self.progress_window.update_detail("已成功找到并启动 run.bat")
            return True
        else:
            self.progress_window.update_detail("未找到 run.bat 文件，安装流程完成")
            if getattr(sys, 'frozen', False):
                self.launcher.show_completion_dialog()
            return True
    
    def run_installation(self) -> bool:
        """运行完整的安装流程"""
        try:
            # 检查管理员权限
            if not self.check_admin_privileges():
                return False

            self.progress_window.update_detail("=== 开始云端自动安装程序 ===")

            # 执行热更新检查
            self.progress_window.set_progress(1, "检查项目包体更新...")
            try:
                hot_update_success = self.hot_updater.perform_hot_update()
                if hot_update_success:
                    self.progress_window.set_progress(8, "热更新检查完成")
                    self.progress_window.update_detail("✓ 热更新检查完成")
                    # 重新加载云端下载器的配置
                    self.cloud_downloader.reload_config()
                    self.progress_window.update_detail("✓ 配置已重新加载")
                else:
                    self.progress_window.set_progress(8, "使用本地版本")
                    self.progress_window.update_detail("⚠ 热更新检查失败，继续使用本地版本")
            except Exception as e:
                self.progress_window.set_progress(8, "使用本地版本")
                self.progress_window.update_detail(f"⚠ 热更新异常: {str(e)}，继续使用本地版本")

            # 检测系统环境，决定是否需要下载Python和微信
            self.progress_window.set_progress(10, "检测系统环境...")
            self.progress_window.update_detail("正在检测Python和微信安装状态")

            # 检测Python
            python_suitable, python_in_path, python_version = self.system_checker.check_python_version()
            skip_python = python_suitable and python_in_path

            if skip_python:
                self.progress_window.update_detail(f"✓ 检测到合适的Python版本: {python_version}，跳过下载")
            else:
                self.progress_window.update_detail("✗ 未检测到合适的Python版本，将下载安装")

            # 检测微信
            wechat_suitable, wechat_version = self.system_checker.check_wechat_version()
            skip_wechat = wechat_suitable

            if skip_wechat:
                self.progress_window.update_detail(f"✓ 检测到合适的微信版本: {wechat_version}，跳过下载")
            else:
                self.progress_window.update_detail("✗ 未检测到合适的微信版本，将下载安装")

            # 下载安装包和项目文件
            downloaded_items = self.download_packages(skip_python, skip_wechat)
            if not downloaded_items:
                self.progress_window.update_detail("错误: 云端下载失败，没有获取到任何文件")
                self.progress_window.set_progress(0, "云端下载失败")
                return False

            # 安装软件包
            install_success = self.install_packages(downloaded_items)
            
            if install_success:
                self.progress_window.update_detail("所有必要的程序已成功安装或确认已存在")
                
                # 执行安装后任务
                post_success = self.post_install_tasks()
                
                if not post_success and getattr(sys, 'frozen', False):
                    self.launcher.show_completion_dialog()
                
                return True
            else:
                self.progress_window.update_detail("部分程序安装失败")
                if getattr(sys, 'frozen', False):
                    try:
                        ctypes.windll.user32.MessageBoxW(
                            0, 
                            "部分程序安装失败，请检查详细信息", 
                            "安装失败", 
                            0x10
                        )
                    except:
                        pass
                return False
                
        except Exception as e:
            self.progress_window.update_detail(f"安装过程中发生异常: {e}")
            
            # 显示错误消息
            if getattr(sys, 'frozen', False):
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0, 
                        f"安装过程中发生错误: {str(e)}", 
                        "安装错误", 
                        0x10
                    )
                except:
                    pass
            
            print(f"\n安装过程中发生错误: {str(e)}")
            return False
        finally:
            # 确保窗口被关闭
            if self.progress_window and not self.progress_window.closed:
                # 给用户一点时间看结果，但保持UI响应
                for _ in range(20):  # 2秒分成20个100ms的片段
                    if self.progress_window and not self.progress_window.closed:
                        self.progress_window.force_update()
                        time.sleep(0.1)
                    else:
                        break
                self.progress_window.close()
    
    def cleanup(self):
        """清理资源"""
        if self.progress_window and not self.progress_window.closed:
            self.progress_window.close()
