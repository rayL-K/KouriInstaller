#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统检查模块 - 负责检查系统环境和已安装软件
"""

import subprocess
import re
import winreg
import os
from typing import Tuple, Optional


class SystemChecker:
    """系统检查器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化系统检查器
        
        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
    
    def _log(self, message: str):
        """日志记录"""
        if self.progress_callback:
            self.progress_callback('detail', message)
        else:
            print(message)
    
    def check_python_version(self) -> Tuple[bool, bool, Optional[str]]:
        """
        检查Python版本
        
        Returns:
            Tuple[已安装合适版本, 环境变量正确, 版本信息]
        """
        self._log("正在检查Python安装状态...")
        
        python_version = None
        python_in_path = False
        
        # 检查命令行Python
        try:
            result = subprocess.run(["python", "--version"], 
                                   capture_output=True, 
                                   text=True, 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                python_in_path = True
                version_output = result.stdout.strip()
                match = re.search(r'Python (\d+\.\d+\.\d+)', version_output)
                if match:
                    python_version = match.group(1)
                    self._log(f"检测到系统已安装Python版本：{python_version}")
        except Exception as e:
            self._log(f"检测Python版本时发生错误，将继续尝试其他检测方法")
        
        # 判断版本是否符合要求
        version_suitable = False
        if python_version:
            try:
                major, minor, _ = map(int, python_version.split('.'))
                if major == 3 and minor <= 11:
                    version_suitable = True
                    self._log(f"当前Python版本 {python_version} 符合要求")
                else:
                    self._log(f"当前Python版本 {python_version} 不符合要求，将安装Python 3.11")
            except ValueError:
                self._log(f"无法解析Python版本字符串: {python_version}")
        
        # 检查注册表
        if not python_version:
            self._log("未从命令行检测到Python，正在检查注册表...")
            try:
                python_keys = []
                
                # 检查HKEY_CURRENT_USER
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Python\PythonCore") as key:
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                python_keys.append(version)
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
                
                # 检查HKEY_LOCAL_MACHINE
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Python\PythonCore") as key:
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                if version not in python_keys:
                                    python_keys.append(version)
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
                
                # 检查符合要求的版本
                for version in python_keys:
                    try:
                        major, minor = map(int, version.split('.'))
                        if major == 3 and minor <= 11:
                            version_suitable = True
                            python_version = version
                            self._log(f"从注册表检测到Python版本：{version}，符合要求")
                            break
                    except ValueError:
                        continue
            except Exception as e:
                self._log("检查Python注册表信息时发生错误，将继续后续安装步骤")
        
        return version_suitable, python_in_path, python_version
    
    def check_wechat_version(self) -> Tuple[bool, Optional[str]]:
        """
        检查微信版本
        
        Returns:
            Tuple[版本符合要求, 版本信息]
        """
        self._log("正在检查微信安装状态...")
        
        wechat_version = None
        version_suitable = False
        
        # 可能的微信安装路径
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Tencent\WeChat\WeChat.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Tencent\WeChat\WeChat.exe"),
            os.path.expandvars(r"%APPDATA%\Tencent\WeChat\WeChat.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Tencent\WeChat\WeChat.exe"),
        ]
        
        # 检查注册表
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat") as key:
                try:
                    raw_version, reg_type = winreg.QueryValueEx(key, "Version")
                    self._log(f"从注册表检测到微信原始版本值：{raw_version}，类型：{reg_type}")
                    
                    if isinstance(raw_version, int):
                        # 解析DWORD格式版本号
                        major = (raw_version >> 24) & 0xFF
                        minor = (raw_version >> 16) & 0xFF
                        patch = (raw_version >> 8) & 0xFF
                        build = raw_version & 0xFF
                        
                        if major > 10:
                            major = 3
                        
                        wechat_version = f"{major}.{minor}.{patch}.{build}"
                        self._log(f"解析微信版本号：{raw_version} → {wechat_version}")
                    else:
                        wechat_version = str(raw_version)
                        self._log(f"从注册表检测到微信版本：{wechat_version}")
                except WindowsError:
                    pass
        except WindowsError:
            pass
        
        # 从文件属性获取版本
        if not wechat_version:
            self._log("在注册表中未找到微信版本信息，尝试从文件属性获取...")
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        escaped_path = path.replace("\\", "\\\\")
                        cmd = f'wmic datafile where name="{escaped_path}" get Version /value'
                        result = subprocess.run(cmd, 
                                               capture_output=True, 
                                               text=True, 
                                               shell=True,
                                               creationflags=subprocess.CREATE_NO_WINDOW)
                        
                        if result.returncode == 0:
                            match = re.search(r'Version=(.+)', result.stdout)
                            if match:
                                wechat_version = match.group(1).strip()
                                self._log(f"从文件属性检测到微信版本：{wechat_version}")
                                break
                    except Exception as e:
                        self._log(f"读取微信版本信息时发生错误: {e}")
        
        # 判断版本是否符合要求
        if wechat_version:
            try:
                if not re.match(r'^\d+(\.\d+)*$', wechat_version):
                    self._log(f"微信版本号格式异常: {wechat_version}，视为符合要求")
                    version_suitable = True
                else:
                    version_parts = wechat_version.split('.')
                    major = int(version_parts[0])
                    minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                    
                    if (major == 3 and minor >= 9) or major < 4:
                        version_suitable = True
                        self._log(f"微信版本 {wechat_version} 符合要求")
                    else:
                        self._log(f"微信版本 {wechat_version} 不符合要求，将安装新版本")
            except (ValueError, IndexError) as e:
                self._log(f"解析微信版本字符串时发生错误，视为符合要求")
                version_suitable = True
        
        return version_suitable, wechat_version
    
    def check_admin_privileges(self) -> bool:
        """检查管理员权限"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
