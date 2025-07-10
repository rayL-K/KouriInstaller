#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热更新器 - 负责从云端更新配置文件
简化版本：启动时下载云端配置文件替换本地配置
"""

import os
import json
import sys
import urllib.request
import urllib.error
import shutil
from pathlib import Path


class HotUpdater:
    """热更新器 - 负责从云端更新配置文件"""

    def __init__(self, progress_callback=None):
        """
        初始化热更新器

        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        self.app_path = self._get_application_path()
        self.config_path = self.app_path / "cloud_config.json"

        # 云端配置文件URL
        self.cloud_config_url = "https://krc-packages.oss-cn-nanjing.aliyuncs.com/cloud_config.json"
        self.fallback_config_urls = [
            "https://github.com/rayL-K/Kouri-installer-packages/releases/download/v1.4.2-fix/cloud_config.json",
            "https://raw.githubusercontent.com/rayL-K/Kouri-installer-packages/main/cloud_config.json"
        ]

    def _get_application_path(self) -> Path:
        """获取应用程序路径"""
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径 - 使用EXE所在目录
            return Path(os.path.dirname(sys.executable))
        else:
            # 开发环境路径
            return Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _log(self, message: str):
        """记录日志"""
        print(f"[热更新] {message}")
        if self.progress_callback:
            self.progress_callback('detail', message)

    def _update_progress(self, message: str):
        """更新进度详情"""
        self._log(message)

    def _set_progress(self, progress: int, status: str):
        """设置进度"""
        if self.progress_callback:
            self.progress_callback('progress', (progress, status))
    
    def download_cloud_config(self) -> bool:
        """
        从云端下载并替换本地的cloud_config.json文件

        Returns:
            下载是否成功
        """
        self._update_progress("正在从云端获取最新配置文件...")

        # 尝试从主源和备用源下载cloud_config.json
        all_urls = [self.cloud_config_url] + self.fallback_config_urls

        for i, url in enumerate(all_urls):
            url_type = "主源" if i == 0 else f"备用源{i}"
            self._update_progress(f"正在从{url_type}获取云端配置文件...")

            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                req.add_header('Cache-Control', 'no-cache')

                with urllib.request.urlopen(req, timeout=15) as response:
                    data = response.read().decode('utf-8')

                    try:
                        # 验证JSON格式
                        cloud_config = json.loads(data)

                        # 备份当前配置文件
                        if self.config_path.exists():
                            backup_path = self.config_path.with_suffix('.json.bak')
                            try:
                                shutil.copy2(self.config_path, backup_path)
                                self._log(f"已备份原配置文件到 {backup_path}")
                            except Exception as e:
                                self._log(f"备份配置文件失败: {e}")

                        # 保存新的配置文件
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            json.dump(cloud_config, f, indent=2, ensure_ascii=False)

                        self._log(f"✓ 成功下载云端配置文件 (使用{url_type})")
                        self._log(f"✓ 配置版本: {cloud_config.get('version', 'unknown')}")
                        self._log(f"✓ 配置文件保存到: {self.config_path}")

                        # 验证文件是否正确保存
                        if self.config_path.exists():
                            self._log("✓ 配置文件验证成功")
                        else:
                            self._log("✗ 配置文件保存失败")
                            return False

                        return True

                    except json.JSONDecodeError as e:
                        self._log(f"✗ 云端配置文件格式错误: {e}")
                        continue

            except urllib.error.URLError as e:
                self._log(f"✗ {url_type}连接失败: {e}")
            except Exception as e:
                self._log(f"✗ {url_type}获取失败: {e}")

        self._log("✗ 所有云端配置源都无法访问，使用本地配置")
        return False
    
    def _get_local_config_version(self) -> str:
        """获取本地配置文件版本"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("version", "unknown")
            return "unknown"
        except Exception as e:
            self._log(f"读取本地配置版本失败: {e}")
            return "unknown"
    
    def perform_hot_update(self) -> bool:
        """
        执行热更新
        
        Returns:
            热更新是否成功
        """
        try:
            self._set_progress(1, "正在检查云端配置更新...")
            self._update_progress("=== 开始云端配置热更新检查 ===")
            
            # 下载云端配置文件
            config_updated = self.download_cloud_config()
            
            if config_updated:
                self._set_progress(5, "云端配置已更新")
                self._update_progress("✓ 云端配置文件已成功更新")
            else:
                self._set_progress(5, "使用当前配置")
                self._update_progress("ℹ 使用当前配置文件继续")
            
            self._set_progress(8, "热更新检查完成")
            return True
            
        except Exception as e:
            self._log(f"热更新过程中发生异常: {e}")
            self._set_progress(8, "热更新异常终止")
            self._update_progress("❌ 热更新异常终止")
            return False