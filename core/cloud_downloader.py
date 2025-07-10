#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端下载模块 - 负责从云端下载文件
"""

import urllib.request
import urllib.error
import hashlib
import json
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class CloudDownloader:
    """云端下载器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化云端下载器
        
        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        self.app_path = self._get_application_path()
        self.download_dir = self.app_path / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _get_application_path(self) -> Path:
        """获取应用程序路径"""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(os.path.abspath(__file__)).parent.parent
    
    def _load_config(self) -> Dict:
        """加载云端配置"""
        config_file = self.app_path / "cloud_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"加载配置文件失败: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "base_url": "",
            "packages": [
                {
                    "name": "python-3.11.9-amd64.exe",
                    "url": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",
                    "size": 26214400,
                    "md5": "",
                    "description": "Python 3.11.9 官方安装程序"
                },
                {
                    "name": "WeChatSetup.exe",
                    "url": "https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe",
                    "size": 157286400,
                    "md5": "",
                    "description": "微信官方安装程序"
                }
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
    
    def download_file_with_fallback(self, package_name: str, local_path: Path, expected_size: int = 0) -> bool:
        """
        使用主URL和备用URL下载文件

        Args:
            package_name: 包名称
            local_path: 本地保存路径
            expected_size: 预期文件大小

        Returns:
            下载是否成功
        """
        # 获取主URL
        package = next((p for p in self.config.get("packages", []) if p.get("name") == package_name), None)
        if not package:
            self._log(f"未找到包配置: {package_name}")
            return False

        primary_url = package.get("url", "")
        if not primary_url:
            self._log(f"包 {package_name} 没有配置下载URL")
            return False

        # 获取备用URLs
        fallback_urls = self.config.get("fallback_urls", {}).get(package_name, [])

        # 构建完整的URL列表（主URL + 备用URLs）
        all_urls = [primary_url] + fallback_urls

        # 逐个尝试下载
        for i, url in enumerate(all_urls):
            url_type = "主源" if i == 0 else f"备用源{i}"
            provider = self._get_provider_name(url)

            self._update_progress(f"尝试从{url_type}下载: {package_name} ({provider})")

            if self.download_file(url, local_path, expected_size):
                if i == 0:
                    self._log(f"✓ 主源下载成功: {package_name}")
                else:
                    self._log(f"✓ 备用源下载成功: {package_name} (使用了第{i}个备用源)")
                return True
            else:
                if i == 0:
                    self._log(f"✗ 主源下载失败: {package_name}，尝试备用源...")
                else:
                    self._log(f"✗ 备用源{i}下载失败: {package_name}")

        self._log(f"✗ 所有下载源都失败: {package_name}")
        return False

    def _get_provider_name(self, url: str) -> str:
        """根据URL判断提供商名称"""
        if "aliyuncs.com" in url:
            return "阿里云OSS"
        elif "github.com" in url:
            return "GitHub"
        elif "python.org" in url:
            return "Python官方"
        elif "qq.com" in url or "weixin" in url:
            return "腾讯官方"
        elif "huaweicloud.com" in url:
            return "华为云"
        else:
            return "其他源"

    def download_file(self, url: str, local_path: Path, expected_size: int = 0) -> bool:
        """
        下载单个文件
        
        Args:
            url: 下载URL
            local_path: 本地保存路径
            expected_size: 预期文件大小
            
        Returns:
            下载是否成功
        """
        try:
            self._update_progress(f"开始下载: {local_path.name}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', expected_size))
                downloaded = 0
                
                with open(local_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            download_progress = (downloaded / total_size) * 100
                            self._update_progress(
                                f"下载中: {local_path.name} ({downloaded // 1024}KB / {total_size // 1024}KB) - {download_progress:.1f}%"
                            )
            
            self._update_progress(f"✓ 下载完成: {local_path.name}")
            return True
            
        except urllib.error.URLError as e:
            self._log(f"下载失败 - 网络错误: {e}")
            self._update_progress(f"✗ 下载失败: {local_path.name} - 网络错误")
            return False
        except Exception as e:
            self._log(f"下载失败: {e}")
            self._update_progress(f"✗ 下载失败: {local_path.name} - {str(e)}")
            return False
    
    def verify_file(self, file_path: Path, expected_md5: str = "") -> bool:
        """
        验证文件完整性
        
        Args:
            file_path: 文件路径
            expected_md5: 期望的MD5值
            
        Returns:
            文件是否有效
        """
        if not file_path.exists():
            return False
        
        if not expected_md5:
            return file_path.stat().st_size > 0
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            file_md5 = hash_md5.hexdigest()
            return file_md5.lower() == expected_md5.lower()
        except Exception as e:
            self._log(f"文件校验失败: {e}")
            return False

    def extract_zip_file(self, zip_path: Path, extract_to: str = ".") -> bool:
        """
        解压ZIP文件

        Args:
            zip_path: ZIP文件路径
            extract_to: 解压目标目录

        Returns:
            解压是否成功
        """
        try:
            # 确定解压目标目录
            if extract_to == ".":
                target_dir = self.app_path
            else:
                target_dir = self.app_path / extract_to

            target_dir.mkdir(parents=True, exist_ok=True)

            self._update_progress(f"开始解压: {zip_path.name}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取压缩包内容信息
                file_list = zip_ref.namelist()
                total_files = len(file_list)

                self._log(f"ZIP文件包含 {total_files} 个文件/文件夹")

                # 逐个解压文件以显示进度
                for i, file_name in enumerate(file_list):
                    try:
                        zip_ref.extract(file_name, target_dir)

                        # 更新进度
                        progress = (i + 1) / total_files * 100
                        if i % 10 == 0 or i == total_files - 1:  # 每10个文件或最后一个文件更新一次
                            self._update_progress(f"解压中: {progress:.1f}% ({i+1}/{total_files})")
                    except Exception as e:
                        self._log(f"解压文件 {file_name} 时出错: {e}")
                        continue

            self._update_progress(f"✓ 解压完成: {zip_path.name}")
            self._log(f"ZIP文件解压成功: {zip_path} -> {target_dir}")

            # 解压完成后删除ZIP文件以节省空间
            try:
                zip_path.unlink()
                self._log(f"已删除ZIP文件: {zip_path}")
            except Exception as e:
                self._log(f"删除ZIP文件失败: {e}")

            return True

        except zipfile.BadZipFile:
            self._log(f"ZIP文件损坏: {zip_path}")
            self._update_progress(f"✗ ZIP文件损坏: {zip_path.name}")
            return False
        except Exception as e:
            self._log(f"解压ZIP文件失败: {e}")
            self._update_progress(f"✗ 解压失败: {zip_path.name} - {str(e)}")
            return False

    def download_packages(self, skip_python: bool = False, skip_wechat: bool = False) -> List[Path]:
        """
        下载所有配置的安装包

        Args:
            skip_python: 是否跳过Python安装包下载
            skip_wechat: 是否跳过微信安装包下载

        Returns:
            成功下载的文件路径列表
        """
        downloaded_files = []
        packages = self.config.get("packages", [])

        if not packages:
            self._log("没有配置需要下载的安装包")
            return downloaded_files

        # 根据检测结果过滤需要下载的包
        filtered_packages = []
        for package in packages:
            package_name = package.get("name", "").lower()

            if skip_python and "python" in package_name:
                self._log(f"跳过Python安装包下载: {package.get('name', '')}")
                continue

            if skip_wechat and ("wechat" in package_name or "微信" in package_name):
                self._log(f"跳过微信安装包下载: {package.get('name', '')}")
                continue

            filtered_packages.append(package)

        if not filtered_packages:
            self._log("根据系统检测结果，没有需要下载的安装包")
            return downloaded_files

        if self.progress_callback:
            self.progress_callback('progress', (12, "准备从云端下载安装包..."))
            self.progress_callback('detail', "开始云端下载流程")

        total_packages = len(filtered_packages)
        self._log(f"需要下载 {total_packages} 个安装包")

        for i, package in enumerate(filtered_packages):
            package_name = package.get("name", f"package_{i}")
            package_url = package.get("url", "")
            package_size = package.get("size", 0)
            package_md5 = package.get("md5", "")
            
            if not package_url:
                self._log(f"跳过无效的包配置: {package_name}")
                continue
            
            # 计算进度 (从12%开始，到20%结束)
            base_progress = 12
            download_progress = (i / total_packages) * 8
            current_progress = base_progress + download_progress

            if self.progress_callback:
                self.progress_callback('progress', (
                    current_progress,
                    f"下载安装包: {package_name} ({i+1}/{total_packages})"
                ))
            
            local_path = self.download_dir / package_name
            
            # 检查文件是否已存在且有效
            if self.verify_file(local_path, package_md5):
                self._log(f"文件已存在且有效，跳过下载: {package_name}")
                self._update_progress(f"✓ 文件已存在: {package_name}")
                downloaded_files.append(local_path)
                continue
            
            # 使用主源和备用源下载文件
            if self.download_file_with_fallback(package_name, local_path, package_size):
                if self.verify_file(local_path, package_md5):
                    # 检查是否需要解压
                    post_download = package.get("post_download", "")
                    if post_download == "extract" and local_path.suffix.lower() == ".zip":
                        extract_to = package.get("extract_to", ".")
                        if self.extract_zip_file(local_path, extract_to):
                            self._log(f"文件下载、验证并解压成功: {package_name}")
                            # 对于ZIP文件，我们返回解压后的目录而不是ZIP文件本身
                            if extract_to == ".":
                                extracted_dir = self.app_path
                            else:
                                extracted_dir = self.app_path / extract_to
                            downloaded_files.append(extracted_dir)
                        else:
                            self._log(f"文件下载成功但解压失败: {package_name}")
                            downloaded_files.append(local_path)  # 仍然返回ZIP文件
                    else:
                        downloaded_files.append(local_path)
                        self._log(f"文件下载并验证成功: {package_name}")
                else:
                    self._log(f"文件下载后验证失败: {package_name}")
                    try:
                        local_path.unlink()
                    except:
                        pass
            
            # 更新完成进度
            completed_progress = base_progress + ((i + 1) / total_packages) * 8
            if self.progress_callback:
                self.progress_callback('progress', (completed_progress, None))

        if self.progress_callback:
            self.progress_callback('progress', (20, "云端下载完成"))
            self.progress_callback('detail', f"云端下载完成，成功下载 {len(downloaded_files)} 个文件")
        
        self._log(f"云端下载完成，成功下载 {len(downloaded_files)}/{total_packages} 个文件")
        return downloaded_files
    
    def get_packages_info(self) -> List[Dict]:
        """获取包信息"""
        return self.config.get("packages", [])
    
    def reload_config(self):
        """重新加载配置"""
        self.config = self._load_config()
