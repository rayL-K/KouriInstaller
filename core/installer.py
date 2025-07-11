#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装器模块 - 负责执行软件安装
"""

import subprocess
import time
import os
from pathlib import Path
from typing import Dict, List


class SoftwareInstaller:
    """软件安装器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化安装器
        
        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        self.python_installed = False
        self.python_install_time = None
        
        # 安装参数配置
        self.install_params: Dict[str, List[str]] = {
            "WeChatSetup.exe": ["/S"],
            "python-3.11.9-amd64.exe": [
                "/quiet", 
                "InstallAllUsers=1", 
                "PrependPath=1", 
                "Include_test=0",
                "Include_launcher=1",
                "Include_tcltk=1",
                "Include_pip=1",
                "Include_doc=0"
            ]
        }
    
    def _log(self, message: str):
        """日志记录"""
        if self.progress_callback:
            self.progress_callback('detail', message)
        else:
            print(message)
    
    def _update_progress(self, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback('detail', message)
    
    def install_software(self, exe_path: Path) -> bool:
        """
        安装单个软件
        
        Args:
            exe_path: 安装程序路径
            
        Returns:
            安装是否成功
        """
        exe_name = exe_path.name
        self._log(f"开始处理 {exe_name}")
        self._update_progress(f"正在分析 {exe_name}...")
        
        # 检查是否需要跳过安装
        if self._should_skip_installation(exe_name):
            self._log(f"跳过安装 {exe_name}")
            return True
        
        # 执行安装
        self._log(f"准备执行安装 {exe_name}")
        self._update_progress(f"开始安装 {exe_name}...")
        
        params = self.install_params.get(exe_name, [])
        cmd = [str(exe_path)] + params
        
        try:
            self._log(f"执行命令: {' '.join(cmd)}")
            self._update_progress(f"执行安装命令，请稍候...")
            
            create_flags = 0
            if os.name == 'nt':
                CREATE_NO_WINDOW = 0x08000000
                create_flags = CREATE_NO_WINDOW
            
            timeout_seconds = 600
            result = subprocess.run(cmd, 
                                    check=True, 
                                    creationflags=create_flags,
                                    capture_output=True, 
                                    text=True, 
                                    encoding='gbk', 
                                    errors='ignore',
                                    timeout=timeout_seconds)
            
            self._log(f"{exe_name} 安装命令执行完成，返回码: {result.returncode}")
            self._update_progress(f"{exe_name} 安装完成")
            
            if "python" in exe_name.lower():
                self.python_installed = True
                self.python_install_time = time.time()
                self._log("Python安装完成，记录安装时间")
                self._update_progress("Python安装成功")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self._log(f"{exe_name} 安装失败，返回码: {e.returncode}")
            self._log(f"错误输出: {e.stderr[:200]}...")
            self._update_progress(f"{exe_name} 安装失败: 返回码 {e.returncode}")
            return False
        except subprocess.TimeoutExpired as e:
            self._log(f"{exe_name} 安装超时 ({timeout_seconds}秒)")
            self._log(f"输出: {e.stdout}")
            self._log(f"错误: {e.stderr}")
            self._update_progress(f"{exe_name} 安装超时 ({timeout_seconds}秒)")
            return False
        except Exception as e:
            self._log(f"安装 {exe_name} 时发生未知错误: {e}")
            self._update_progress(f"安装 {exe_name} 时发生未知错误: {e}")
            return False
    
    def _should_skip_installation(self, exe_name: str) -> bool:
        """检查是否应该跳过安装"""
        from .system_checker import SystemChecker
        
        checker = SystemChecker(self.progress_callback)
        
        if "python" in exe_name.lower():
            python_suitable, python_in_path, python_version = checker.check_python_version()
            if python_suitable:
                if python_in_path:
                    self._log(f"系统已安装合适的Python版本({python_version})且环境变量配置正确，跳过安装")
                    self._update_progress(f"系统已安装合适的Python版本({python_version})，跳过安装")
                    self.python_installed = True
                    return True
                else:
                    self._log(f"系统已安装Python {python_version}，但环境变量配置不正确，将安装新版本")
                    self._update_progress(f"系统已安装Python {python_version}，但环境变量未配置，将安装新版本")
        
        elif "wechat" in exe_name.lower() or "微信" in exe_name.lower():
            wechat_suitable, wechat_version = checker.check_wechat_version()
            if wechat_suitable:
                self._log(f"系统已安装合适的微信版本({wechat_version})，跳过安装")
                self._update_progress(f"系统已安装合适的微信版本({wechat_version})，跳过安装")
                return True
        
        return False


    def wait_for_python_env_vars(self, min_wait_time: int = 10, max_wait_time: int = 60):
        """等待Python环境变量生效"""
        if not self.python_install_time:
            self._log("未检测到Python安装时间，不执行等待")
            return
            
        elapsed = time.time() - self.python_install_time
        
        if self.progress_callback:
            self.progress_callback('progress', (95, "等待环境变量生效..."))
        self._update_progress("正在等待Python环境变量生效")
        
        wait_needed = False
        if elapsed < min_wait_time:
            wait_time = min_wait_time - elapsed
            self._log(f"Python安装后时间过短({elapsed:.1f}s)，等待环境变量生效，将等待 {wait_time:.1f} 秒...")
            self._update_progress(f"正在等待环境变量生效，请稍候...")
            wait_needed = True
            
            start_time = time.time()
            while time.time() - start_time < wait_time:
                remaining = wait_time - (time.time() - start_time)
                if remaining <= 0:
                    break
                if int(remaining) % 2 == 0 or remaining < 2:
                    self._update_progress(f"正在等待环境变量生效，剩余约 {int(remaining)+1} 秒...")
                time.sleep(0.2)
            self._update_progress("等待结束，检查Python命令...")
        
        elif elapsed > max_wait_time:
            self._log(f"Python安装后已过去 {elapsed:.1f} 秒，超过最大等待时间 {max_wait_time} 秒，假设环境变量已生效")
            self._update_progress(f"已等待较长时间 ({elapsed:.1f}s)，继续检查Python命令")
        else:
            self._log(f"Python安装后已过去 {elapsed:.1f} 秒，继续检查Python命令")
            self._update_progress(f"已等待 {elapsed:.1f} 秒，检查Python命令...")
        
        # 检查Python是否能正常使用
        self._update_progress("尝试执行 'python --version'...")
        python_ok = False
        try:
            result = subprocess.run(["python", "--version"],
                                   capture_output=True,
                                   text=True,
                                   creationflags=subprocess.CREATE_NO_WINDOW,
                                   timeout=10)
            if result.returncode == 0:
                self._log(f"Python环境变量已生效: {result.stdout.strip()}")
                self._update_progress(f"Python命令执行成功: {result.stdout.strip()}")
                python_ok = True
            else:
                self._log(f"'python --version' 执行失败，返回码: {result.returncode}")
                self._update_progress(f"Python命令执行失败 (返回码 {result.returncode})")
        except subprocess.TimeoutExpired:
            self._log("检查Python命令超时")
            self._update_progress("检查Python命令超时，可能存在问题。")
        except Exception as e:
            self._log(f"检查Python命令时出错: {e}")
            self._update_progress(f"检查Python命令时出错: {e}")
        
        # 额外等待
        if wait_needed and not python_ok:
            extra_wait = 5
            self._log(f"首次检查Python命令失败，额外等待 {extra_wait} 秒...")
            self._update_progress(f"Python命令检查失败，再等待 {extra_wait} 秒...")
            start_time = time.time()
            while time.time() - start_time < extra_wait:
                remaining = extra_wait - (time.time() - start_time)
                if remaining <= 0: 
                    break
                self._update_progress(f"额外等待 {int(remaining)+1} 秒...")
                time.sleep(0.2)
            self._log("额外等待结束")
            self._update_progress("额外等待结束")
