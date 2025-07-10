# 🚀 KouriInstaller

一个基于云端下载的软件安装器，采用高内聚、低耦合的模块化架构设计。

## 📋 目录

- [功能特性](#功能特性)
- [项目架构](#项目架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [阿里云OSS配置](#阿里云oss配置)
- [开发指南](#开发指南)
- [开发者接口](#开发者接口)
- [故障排除](#故障排除)
- [更新日志](#更新日志)

## 🌟 功能特性

### 🚀 **纯云端下载**
- 完全基于云端，不依赖本地文件
- 自动从配置的URL下载安装包
- 实时显示下载进度和速度
- 支持大文件下载和网络重试

### 🔄 **多源备用**
- **主源**: 阿里云OSS (国内高速)
- **备用**: GitHub Release (全球可用)
- 主源失败时自动切换备用源
- 智能选择最快的下载源

### 📦 **ZIP文件支持**
- 自动下载和解压ZIP压缩包
- 支持大型项目文件分发
- 解压完成后自动清理ZIP文件
- 智能文件类型识别

### ✅ **文件验证**
- 支持MD5校验确保文件完整性
- 自动验证文件大小
- 损坏文件自动重新下载
- 下载缓存避免重复下载

### 🎨 **UI**
- 流畅的进度条动画
- 实时状态和详细信息显示
- 简洁的界面设计
- 用户友好的交互体验

### 🔥 **云端配置热更新**
- 程序启动时自动检查云端配置更新
- 从云端获取最新的配置文件
- 支持版本比较和增量更新
- 无需重新发布安装器即可更新下载内容
- 云端统一管理所有配置

### 🛡️ **智能检测**
- 自动检测已安装的Python和微信版本
- 跳过已安装的符合要求的软件
- 自动请求管理员权限
- 环境变量验证

### 🔐 **管理员权限**
- 程序启动时自动检测管理员权限
- 未检测到权限时自动请求提升
- 支持多种启动方式确保权限获取
- 打包后的EXE文件自带权限清单

## 🏗️ 项目架构

### 📁 文件结构

```
云端安装器/
├── install_all_new.py          # 主程序入口
├── main_controller.py          # 主控制器
├── cloud_config.json           # 云端配置文件
├── ui/                         # UI模块
│   ├── __init__.py
│   └── progress_window.py      # 进度窗口
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── cloud_downloader.py     # 云端下载器
│   ├── system_checker.py       # 系统检查器
│   ├── installer.py            # 软件安装器
│   ├── launcher.py             # 脚本启动器
│   └── hot_updater.py          # 云端配置热更新器
└── downloads/                  # 下载缓存目录（自动创建）
```

### 🧩 模块设计原则

#### 高内聚 (High Cohesion)
- 每个模块内部的功能紧密相关
- 单一职责原则：每个模块只负责一个特定的功能领域
- 模块内部的代码协同工作，实现共同目标

#### 低耦合 (Low Coupling)
- 模块之间的依赖关系最小化
- 通过标准接口进行通信
- 模块可以独立开发、测试和维护

### 📋 模块职责

| 模块 | 职责 | 特点 |
|------|------|------|
| `install_all_new.py` | 程序启动和异常处理 | 简洁的入口点 |
| `main_controller.py` | 协调各个模块的工作流程 | 统一的流程控制 |
| `ui/progress_window.py` | 用户界面和交互 | 完全独立，不依赖业务逻辑 |
| `core/cloud_downloader.py` | 云端文件下载 | 纯下载逻辑，不涉及UI |
| `core/system_checker.py` | 系统环境检查 | 纯检查逻辑，无副作用 |
| `core/installer.py` | 软件安装执行 | 专注安装，不处理下载 |
| `core/launcher.py` | 脚本查找和启动 | 独立的启动逻辑 |
| `core/hot_updater.py` | 云端配置热更新 | 配置文件自动更新 |

## 🚀 快速开始

### 1. **运行安装器**

#### 方法1：Python脚本（自动请求管理员权限）
```bash
python install_all_new.py
```

#### 方法2：批处理文件（推荐）
```bash
run_as_admin.bat
```

#### 方法3：PowerShell脚本
```powershell
.\run_as_admin.ps1
```

#### 方法4：打包后的EXE文件
```bash
KouriInstaller.exe  # 自动请求管理员权限
```

### 2. **安装流程**
1. 程序启动时自动下载云端配置文件
2. 用云端配置替换本地配置文件
3. 智能检测Python和微信安装状态
4. 根据检测结果决定是否下载安装包
5. 下载项目文件并自动解压
6. 安装必要的软件（如果需要）
7. 启动 `run.bat` 脚本

## ⚙️ 配置说明

### 云端配置文件 (`cloud_config.json`)

```json
{
  "base_url": "https://krc-packages.oss-cn-nanjing.aliyuncs.com/",
  "packages": [
    {
      "name": "python-3.11.9-amd64.exe",
      "url": "https://krc-packages.oss-cn-nanjing.aliyuncs.com/python-3.11.9-amd64.exe",
      "size": 26214400,
      "description": "Python 3.11.9 官方安装程序"
    },
    {
      "name": "1.4.2fix.zip",
      "url": "https://krc-packages.oss-cn-nanjing.aliyuncs.com/1.4.2fix.zip",
      "size": 104857600,
      "description": "Kouri项目文件压缩包",
      "extract_to": ".",
      "post_download": "extract"
    }
  ],
  "fallback_urls": {
    "python-3.11.9-amd64.exe": [
      "https://github.com/rayL-K/Kouri-installer-packages/releases/download/v1.4.2-fix/python-3.11.9-amd64.exe"
    ]
  },
  "version": "1.4.2-fix",
  "last_updated": "2024-07-09T15:30:00Z",
  "description": "阿里云OSS主源 + GitHub备用源配置"
}
```

### 配置项说明

- **`base_url`**: 基础下载URL（可选）
- **`packages`**: 安装包列表
  - **`name`**: 文件名
  - **`url`**: 下载地址
  - **`size`**: 文件大小（字节）
  - **`extract_to`**: 解压目标目录（ZIP文件）
  - **`post_download`**: 下载后处理（`"extract"` = 自动解压）
- **`fallback_urls`**: 备用下载地址
- **`version`**: 配置文件版本号（用于热更新比较）
- **`last_updated`**: 最后更新时间
- **`description`**: 配置描述

## 🌐 阿里云OSS配置

### 📊 下载源配置

#### 🚀 **主要下载源 - 阿里云OSS**
```
Bucket: krc-packages
Region: 华东1(南京) 
Endpoint: oss-cn-nanjing.aliyuncs.com
Base URL: https://krc-packages.oss-cn-nanjing.aliyuncs.com/

优势:
✅ 国内高速下载
✅ 低延迟访问  
✅ 稳定可靠
✅ CDN加速
```

#### 🔄 **备用下载源 - GitHub Release**
```
Repository: rayL-K/Kouri-installer-packages
Tag: v1.4.2-fix

优势:
✅ 全球可用
✅ 免费服务
✅ 版本管理
✅ 自动备份
```

### 📁 需要上传的文件

```
krc-packages (Bucket)
├── cloud_config.json          # 云端配置文件（关键）
├── python-3.11.9-amd64.exe    # Python安装程序 (~25MB)
├── WeChatSetup.exe            # 微信安装程序 (~150MB)
└── 1.4.2fix.zip               # Kouri项目压缩包 (~100MB)
```

### ⚙️ 阿里云OSS设置步骤

1. **创建Bucket**
   - Bucket名称: `krc-packages`
   - 地域: 华东1(南京)
   - 读写权限: 公共读

2. **上传文件**
   - 将文件上传到Bucket根目录
   - 设置文件权限为"公共读"

3. **验证访问**
   - 确认文件URL可直接访问
   - 测试下载功能

### 🔧 智能下载机制

```
下载优先级:
1. 阿里云OSS (主源) → 高速国内下载
2. GitHub Release (备用源) → 主源失败时自动切换
3. 官方源 (Python/微信) → 最终备用
```

## 🛠️ 开发指南

### 添加新功能
1. 确定功能属于哪个模块
2. 如果需要新模块，创建独立的文件
3. 通过回调机制与UI通信
4. 在主控制器中协调新功能

### 修改现有功能
1. 定位到对应的模块
2. 只修改该模块内部实现
3. 保持接口不变
4. 测试模块功能

### 云端配置热更新
1. 修改云端的`cloud_config.json`文件
2. 更新版本号和最后更新时间
3. 修改包体信息（如需要）
4. 上传新的项目包体（如需要）
5. 用户下次启动程序时会自动获取新配置

## 👨‍💻 开发者接口

### 🏗️ 核心模块API

#### 1. 主控制器 (`main_controller.py`)

```python
class InstallationController:
    """安装流程主控制器"""

    def __init__(self):
        """初始化控制器，创建各个模块实例"""

    def run_installation(self) -> bool:
        """运行完整的安装流程

        Returns:
            bool: 安装是否成功
        """

    def cleanup(self):
        """清理资源，关闭UI窗口"""
```

#### 2. 云端下载器 (`core/cloud_downloader.py`)

```python
class CloudDownloader:
    """云端文件下载器"""

    def __init__(self, app_path: Path, progress_callback=None, log_callback=None):
        """初始化下载器

        Args:
            app_path: 应用程序路径
            progress_callback: 进度回调函数 (message: str) -> None
            log_callback: 日志回调函数 (message: str) -> None
        """

    def download_packages(self, packages: list) -> list:
        """下载包列表

        Args:
            packages: 包配置列表

        Returns:
            list: 下载成功的文件路径列表
        """

    def download_file_with_fallback(self, filename: str, local_path: Path, expected_size: int = None) -> bool:
        """使用主源和备用源下载文件

        Args:
            filename: 文件名
            local_path: 本地保存路径
            expected_size: 期望文件大小

        Returns:
            bool: 下载是否成功
        """
```

#### 3. 系统检查器 (`core/system_checker.py`)

```python
class SystemChecker:
    """系统环境检查器"""

    def __init__(self, progress_callback=None, log_callback=None):
        """初始化检查器

        Args:
            progress_callback: 进度回调函数
            log_callback: 日志回调函数
        """

    def check_python_installation(self) -> dict:
        """检查Python安装状态

        Returns:
            dict: {
                'installed': bool,
                'version': str,
                'path': str,
                'needs_install': bool
            }
        """

    def check_wechat_installation(self) -> dict:
        """检查微信安装状态

        Returns:
            dict: {
                'installed': bool,
                'version': str,
                'path': str,
                'needs_install': bool
            }
        """
```

#### 4. 软件安装器 (`core/installer.py`)

```python
class SoftwareInstaller:
    """软件安装器"""

    def __init__(self, progress_callback=None, log_callback=None):
        """初始化安装器"""

    def install_python(self, installer_path: Path) -> bool:
        """安装Python

        Args:
            installer_path: Python安装程序路径

        Returns:
            bool: 安装是否成功
        """

    def install_wechat(self, installer_path: Path) -> bool:
        """安装微信

        Args:
            installer_path: 微信安装程序路径

        Returns:
            bool: 安装是否成功
        """
```

#### 5. 脚本启动器 (`core/launcher.py`)

```python
class ScriptLauncher:
    """脚本启动器"""

    def __init__(self, app_path: Path, progress_callback=None, log_callback=None):
        """初始化启动器

        Args:
            app_path: 应用程序路径
            progress_callback: 进度回调函数
            log_callback: 日志回调函数
        """

    def find_and_launch_script(self) -> bool:
        """查找并启动run.bat脚本

        Returns:
            bool: 是否成功找到并启动脚本
        """
```

#### 6. 热更新器 (`core/hot_updater.py`)

```python
class HotUpdater:
    """云端配置热更新器"""

    def __init__(self, config_url: str, local_config_path: str, progress_callback=None, log_callback=None):
        """初始化热更新器

        Args:
            config_url: 云端配置文件URL
            local_config_path: 本地配置文件路径
            progress_callback: 进度回调函数
            log_callback: 日志回调函数
        """

    def check_and_update(self) -> bool:
        """检查并更新配置文件

        Returns:
            bool: 是否有更新
        """
```

### 🎨 UI模块API

#### 进度窗口 (`ui/progress_window.py`)

```python
class ProgressWindow:
    """进度显示窗口"""

    def __init__(self, title="KouriChat安装向导"):
        """初始化进度窗口

        Args:
            title: 窗口标题
        """

    def set_progress(self, percentage: int, status: str):
        """设置进度条

        Args:
            percentage: 进度百分比 (0-100)
            status: 状态文本
        """

    def update_detail(self, message: str):
        """更新详细信息

        Args:
            message: 详细信息文本
        """

    def close(self):
        """关闭窗口"""
```

### 🔧 回调函数接口

#### 进度回调函数
```python
def progress_callback(message: str) -> None:
    """进度更新回调函数

    Args:
        message: 进度信息
    """
    pass
```

#### 日志回调函数
```python
def log_callback(message: str) -> None:
    """日志记录回调函数

    Args:
        message: 日志信息
    """
    pass
```

### 📋 配置文件接口

#### 云端配置文件结构
```python
{
    "base_url": str,                    # 基础下载URL
    "packages": [                       # 包列表
        {
            "name": str,                # 文件名
            "url": str,                 # 下载URL
            "size": int,                # 文件大小(字节)
            "md5": str,                 # MD5校验值(可选)
            "description": str,         # 描述
            "extract_to": str,          # 解压目录(ZIP文件)
            "post_download": str        # 下载后处理("extract")
        }
    ],
    "fallback_urls": {                  # 备用URL映射
        "filename": [str, ...]          # 备用URL列表
    },
    "version": str,                     # 配置版本号
    "last_updated": str,                # 最后更新时间(ISO格式)
    "description": str                  # 配置描述
}
```

### 🚀 使用示例

#### 1. 创建自定义安装流程
```python
from main_controller import InstallationController

# 创建控制器
controller = InstallationController()

# 运行安装
success = controller.run_installation()

# 清理资源
controller.cleanup()
```

#### 2. 单独使用下载器
```python
from core.cloud_downloader import CloudDownloader
from pathlib import Path

def progress_callback(message):
    print(f"进度: {message}")

def log_callback(message):
    print(f"日志: {message}")

# 创建下载器
downloader = CloudDownloader(
    app_path=Path.cwd(),
    progress_callback=progress_callback,
    log_callback=log_callback
)

# 下载包
packages = [
    {
        "name": "test.zip",
        "url": "https://example.com/test.zip",
        "size": 1024000,
        "post_download": "extract"
    }
]

downloaded_files = downloader.download_packages(packages)
```

#### 3. 系统检查
```python
from core.system_checker import SystemChecker

checker = SystemChecker()

# 检查Python
python_info = checker.check_python_installation()
print(f"Python已安装: {python_info['installed']}")
print(f"版本: {python_info['version']}")

# 检查微信
wechat_info = checker.check_wechat_installation()
print(f"微信已安装: {wechat_info['installed']}")
```

### 🔌 扩展开发

#### 添加新的下载源
```python
# 在 cloud_downloader.py 中扩展
def add_custom_source(self, source_name: str, base_url: str):
    """添加自定义下载源"""
    self.custom_sources[source_name] = base_url
```

#### 添加新的软件检查
```python
# 在 system_checker.py 中扩展
def check_custom_software(self, software_name: str) -> dict:
    """检查自定义软件安装状态"""
    # 实现检查逻辑
    return {
        'installed': False,
        'version': '',
        'path': '',
        'needs_install': True
    }
```

#### 自定义UI主题
```python
# 在 progress_window.py 中扩展
def set_custom_theme(self, theme_config: dict):
    """设置自定义UI主题"""
    self.colors.update(theme_config.get('colors', {}))
    self._setup_styles()
```

## 📦 打包部署

### 🚀 **一键打包**

使用提供的自动化打包脚本：

```bash
# 在项目根目录运行
build_installer.bat
```

### 📋 **打包流程**

脚本会自动完成以下步骤：

1. **环境检查**
   - 检查Python安装
   - 安装/更新uv包管理器
   - 安装必要依赖：`pyinstaller` `pywin32` `pillow` `requests` `urllib3`

2. **项目验证**
   - 验证`install_all_new.py`存在
   - 验证`cloud_config.json`存在
   - 验证`ui/`和`core/`目录存在

3. **构建执行**
   - 清理旧的构建文件
   - 使用PyInstaller打包为单文件EXE
   - 自动包含配置文件和隐藏导入

### ⚙️ **打包参数**

```bash
--onefile              # 单文件打包
--noconsole            # 无控制台窗口
--uac-admin            # 请求管理员权限
--name "KouriInstaller" # 输出文件名
--add-data "cloud_config.json;."  # 包含配置文件
--hidden-import "tkinter"          # 确保GUI正常工作
```

### 📁 **输出结果**

```
生成文件:
├── dist/
│   └── KouriInstaller.exe  # 最终可执行文件
└── 部署目录/
    └── KouriInstaller.exe  # 自动复制的文件
```

### 🎯 **部署优势**

- **单文件部署**：所有依赖打包在一个EXE中
- **管理员权限**：自动请求确保安装成功
- **云端架构**：不依赖本地文件，从云端下载
- **完整功能**：包含所有模块和配置

## 🐛 故障排除

### 常见问题

#### Q: 进度条不动？
A: 检查网络连接，确保云端文件可访问。程序会自动切换到备用源。

#### Q: 下载失败？
A: 
1. 检查阿里云OSS文件是否已上传
2. 验证文件权限设置为公共读
3. 检查网络连接
4. 查看详细错误信息

#### Q: 安装失败？
A: 
1. 确保以管理员权限运行
2. 检查系统兼容性
3. 查看安装日志

#### Q: 配置文件错误？
A:
1. 验证JSON格式是否正确
2. 检查云端配置文件是否可访问
3. 参考示例配置文件

#### Q: 如何以管理员权限运行？
A:
1. **自动方式**：直接运行程序，会自动请求管理员权限
2. **批处理文件**：运行 `run_as_admin.bat`
3. **PowerShell**：运行 `run_as_admin.ps1`
4. **手动方式**：右键程序选择"以管理员身份运行"
5. **EXE文件**：打包后的EXE会自动请求管理员权限

#### Q: 管理员权限请求失败？
A:
1. 确保当前用户有管理员权限
2. 检查UAC设置是否过于严格
3. 尝试手动以管理员身份运行
4. 使用提供的批处理或PowerShell脚本

#### Q: exe文件图标不显示？
A:
1. 确保final_exe目录中的图标文件存在
2. 重新打包exe文件，确保资源文件被正确包含
3. 检查图标文件格式是否正确（.ico格式）
4. 验证图标文件没有损坏

#### Q: run.bat不会自动启动？
A:
1. 确保kourichat文件夹与exe文件在同一目录
2. 检查run.bat文件是否存在且可执行
3. 查看安装详情中的日志信息
4. 手动运行exe文件，观察搜索路径
5. 确保文件夹名称包含"kourichat"、"kouri"或"exploration"关键词

#### Q: 打包后的exe文件无法运行？
A:
1. 检查是否缺少必要的依赖文件
2. 确保Python环境正确
3. 查看PyInstaller的警告信息
4. 尝试在命令行中运行查看错误信息
5. 检查杀毒软件是否误报

### 🔍 调试技巧
1. 每个模块可以独立运行和测试
2. 使用回调函数输出调试信息
3. 检查downloads目录中的缓存文件

## 📈 性能优化

### 下载速度对比 (国内)
```
阿里云OSS:    10-50 MB/s  (主源)
GitHub:       1-10 MB/s   (备用源)
Python官方:   0.5-5 MB/s  (最终备用)
```

### 可用性对比
```
阿里云OSS:    99.9% (国内优秀)
GitHub:       99.5% (全球稳定)
官方源:       95%   (偶有限制)
```

## 🔄 更新日志

### v2.1.0 (2025-07-10)
- ✅ **修复exe文件资源路径问题**：支持打包后的exe在任意目录正确显示图标和图片
- ✅ **修复run.bat启动问题**：改进路径搜索逻辑，确保解压后能正确找到并运行run.bat
- ✅ **优化打包配置**：添加所有必要资源文件到exe打包中
- ✅ **改进启动逻辑**：无论Python安装状态如何都尝试启动run.bat
- ✅ **增强路径检测**：优先搜索exe文件所在目录，支持递归查找
- ✅ **完善开发者接口文档**：添加详细的API文档和使用示例

### v2.0.4 (2025-07-10)
- ✅ 实现智能系统检测，跳过已安装的软件
- ✅ 优化下载逻辑，根据检测结果决定下载内容
- ✅ 修改启动脚本为 `run.bat`（原 `fast_run.bat`）
- ✅ 更新主源URL为最新的1.4.2-fix版本
- ✅ 简化热更新机制，直接替换配置文件

### v2.0.3 (2024-07-10)
- ✅ 全新云端配置热更新机制
- ✅ 简化热更新流程，直接更新配置文件
- ✅ 优化文件结构，移除冗余代码
- ✅ 提高系统稳定性和可维护性

### v2.0.2 (2024-07-09)
- ✅ 配置阿里云OSS为主要下载源
- ✅ GitHub Release作为备用源
- ✅ 智能多源下载和自动切换
- ✅ 完善的错误处理和重试机制

### v2.0.1 (2024-07-09)
- ✅ 新增ZIP文件自动下载和解压功能
- ✅ 支持大型项目文件云端分发
- ✅ 智能文件类型识别和处理
- ✅ 增强的配置管理界面

### v2.0.0 (2024-07-09)
- ✅ 完全重构为模块化架构
- ✅ 实现高内聚、低耦合设计
- ✅ 移除日志文件依赖
- ✅ 优化UI和用户体验

### v1.0.0
- ✅ 基础云端下载功能
- ✅ Python和微信自动安装
- ✅ 基本的进度显示

## 🎯 总结

这个云端安装器通过优秀的架构设计，为用户和开发者提供了：

### 👥 用户体验
- 🚀 **极速下载**：阿里云OSS国内高速访问
- 🔄 **高可靠性**：多源备用和自动切换
- 📦 **完整环境**：一键获得软件+项目文件
- 🎨 **优秀体验**：流畅UI和实时反馈
- 🔥 **灵活更新**：云端配置热更新机制

### 👨‍💻 开发者友好
- 🛠️ **模块化架构**：高内聚、低耦合的设计
- 📚 **完整API**：详细的开发者接口文档
- 🔌 **易于扩展**：标准化的回调和接口
- 🧪 **独立测试**：每个模块可单独测试
- 📖 **清晰文档**：完整的使用示例和最佳实践

### 🔧 技术优势
- 💾 **资源管理**：智能的资源路径处理
- 🔍 **智能搜索**：递归文件查找算法
- 🛡️ **错误处理**：完善的异常处理机制
- 📊 **状态管理**：实时的进度和状态反馈
- 🎯 **精确控制**：细粒度的安装流程控制

通过云端分发，用户只需下载一个小的安装程序，就能自动获得完整的项目环境！
开发者可以轻松基于现有架构扩展功能，创建自定义的安装解决方案！

---

**🎉 享受云端安装的便捷体验！**

