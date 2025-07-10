#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度窗口模块 - 负责UI显示和用户交互
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import ctypes
import datetime
import time
import sys
import os
from pathlib import Path
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持打包后的exe环境"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 如果不是打包环境，使用当前脚本的目录
        base_path = os.path.dirname(os.path.abspath(__file__))
        # 回到项目根目录
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, relative_path)


class ProgressWindow:
    """进度窗口类"""
    
    def __init__(self, title="KouriChat安装向导"):
        """初始化进度窗口"""
        self._setup_dpi()
        self._create_window(title)
        self._setup_fonts()
        self._setup_colors()
        self._setup_styles()
        self._create_ui()
        self._init_animation()
        self._bind_events()
        self._start_ui_loop()
    
    def _setup_dpi(self):
        """设置DPI感知"""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    
    def _create_window(self, title):
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x1100")
        self.root.resizable(False, False)
        self.root.configure(bg='#f8f9fa')
        self.closed = False

        try:
            self.root.attributes('-topmost', True)
            self._center_window()
        except Exception:
            pass

        self._setup_icon()
    
    def _center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width, height = 700, 1100
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_icon(self):
        """设置窗口图标"""
        try:
            # 窗口左上角图标使用title.ico
            icon_files = [
                "final_exe/title.ico",
                "final_exe/KouriInstaller.ico",
                "final_exe/KouriInstaller_ico.ico",
                "favicon.ico"
            ]

            for icon_file in icon_files:
                icon_path = get_resource_path(icon_file)
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
        except Exception:
            pass

    def _load_title_icon(self):
        """加载标题中使用的图标"""
        if not PIL_AVAILABLE:
            return None

        try:
            # 优先使用指定的PNG图片
            title_image_files = [
                "final_exe/MenuZhizhi.png",  # 菜单指示图标
                "final_exe/KouriInstaller.ico",  # 窗口图标
                "final_exe/KouriInstaller_ico.ico",  # 打包图标
                "favicon.ico"
            ]

            for image_file in title_image_files:
                image_path = get_resource_path(image_file)
                if os.path.exists(image_path):
                    # 加载图片并调整大小
                    image = Image.open(image_path)
                    # 调整为适合标题的大小
                    image = image.resize((175, 175), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(image)

            return None
        except Exception:
            return None
    
    def _setup_fonts(self):
        """设置字体"""
        try:
            font_families = ["Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", "Arial"]
            self.font_family = "Arial"

            available_fonts = tkfont.families()
            for font in font_families:
                if font in available_fonts:
                    self.font_family = font
                    break

            self.title_font = tkfont.Font(family=self.font_family, size=18, weight="bold")
            self.subtitle_font = tkfont.Font(family=self.font_family, size=12)
            self.status_font = tkfont.Font(family=self.font_family, size=11)
            self.detail_font = tkfont.Font(family=self.font_family, size=9)
            self.progress_font = tkfont.Font(family=self.font_family, size=10)
        except Exception:
            self.title_font = ("Arial", 18, "bold")
            self.subtitle_font = ("Arial", 12)
            self.status_font = ("Arial", 11)
            self.detail_font = ("Arial", 9)
            self.progress_font = ("Arial", 10)

    def _setup_colors(self):
        """设置颜色主题"""
        self.colors = {
            'bg_primary': '#f8f9fa',      # 主背景色 - 浅灰白
            'bg_card': '#ffffff',         # 卡片背景色 - 纯白
            'bg_secondary': '#e9ecef',    # 次要背景色 - 浅灰
            'text_primary': '#212529',    # 主文本色 - 深灰黑
            'text_secondary': '#6c757d',  # 次要文本色 - 中灰
            'accent': '#007bff',          # 强调色 - 蓝色
            'accent_light': '#e3f2fd',    # 浅强调色 - 浅蓝
            'success': '#28a745',         # 成功色 - 绿色
            'warning': '#ffc107',         # 警告色 - 黄色
            'danger': '#dc3545',          # 危险色 - 红色
            'border': '#dee2e6',          # 边框色 - 浅灰
            'shadow': '#00000010'         # 阴影色 - 透明黑
        }
    
    def _setup_styles(self):
        """配置样式"""
        self.style = ttk.Style()

        themes = self.style.theme_names()
        if "vista" in themes:
            self.style.theme_use("vista")
        elif "winnative" in themes:
            self.style.theme_use("winnative")
        elif "clam" in themes:
            self.style.theme_use("clam")

        try:
            # 进度条样式
            self.style.configure("TProgressbar",
                               thickness=30,
                               troughcolor=self.colors['bg_secondary'],
                               background=self.colors['accent'],
                               borderwidth=0,
                               relief='flat')

            self.style.map("TProgressbar",
                          background=[('active', '#0056b3'),
                                    ('!active', self.colors['accent'])])
        except Exception:
            pass
    
    def _create_ui(self):
        """创建UI界面"""
        # 主容器 - 使用新的背景色
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=35, pady=30)

        # 标题区域
        self._create_title_section(main_container)

        # 状态区域
        self._create_status_section(main_container)

        # 进度条区域
        self._create_progress_section(main_container)

        # 详细信息区域
        self._create_detail_section(main_container)
    
    def _create_title_section(self, parent):
        """创建标题区域"""
        # 标题容器 - 添加卡片式背景和阴影效果
        title_container = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        title_container.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        title_container.pack(fill=tk.X, pady=(0, 30))

        # 内部填充框架
        title_frame = tk.Frame(title_container, bg=self.colors['bg_card'])
        title_frame.pack(fill=tk.X, padx=30, pady=25)

        # 图标和主标题容器
        header_frame = tk.Frame(title_frame, bg=self.colors['bg_card'])
        header_frame.pack(fill=tk.X)

        # 尝试加载图标
        title_icon = self._load_title_icon()

        if title_icon:
            # 如果有图标，创建包含图标的标题
            icon_title_frame = tk.Frame(header_frame, bg=self.colors['bg_card'])
            icon_title_frame.pack()

            # 图标标签
            icon_label = tk.Label(icon_title_frame,
                                image=title_icon,
                                bg=self.colors['bg_card'])
            icon_label.pack(side=tk.LEFT, padx=(0, 5))

            # 保持图标引用，防止被垃圾回收
            icon_label.image = title_icon

            # 主标题
            self.title_label = tk.Label(icon_title_frame,
                                       text="KouriInstaller",
                                       font=self.title_font,
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['text_primary'])
            self.title_label.pack(side=tk.LEFT)
        else:
            # 如果没有图标，使用纯文本标题
            self.title_label = tk.Label(header_frame,
                                       text="KouriChat 安装向导",
                                       font=self.title_font,
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['text_primary'])
            self.title_label.pack()

        # 副标题
        self.subtitle_label = tk.Label(title_frame,
                                     text="——理想恋人❀触手可及——",
                                     font=self.subtitle_font,
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_secondary'])
        self.subtitle_label.pack(pady=(8, 0))

        # 装饰性分隔线 - 使用渐变效果
        separator_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=4)
        separator_frame.pack(fill=tk.X, pady=(0, 25))

        # 创建渐变分隔线效果
        gradient_line = tk.Frame(separator_frame, height=3, bg=self.colors['accent'])
        gradient_line.pack(fill=tk.X)

        # 添加浅色装饰线
        light_line = tk.Frame(separator_frame, height=1, bg=self.colors['accent_light'])
        light_line.pack(fill=tk.X)

    def _create_status_section(self, parent):
        """创建状态区域"""
        # 状态容器 - 卡片式设计（保持原有结构）
        status_container = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        status_container.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        status_container.pack(fill=tk.X, pady=(0, 25))

        status_frame = tk.Frame(status_container, bg=self.colors['bg_card'])
        status_frame.pack(fill=tk.X, padx=30, pady=20)

        # 状态标签 - 保持原有样式，仅调整位置
        status_header = tk.Label(status_frame,
                            text="📊 当前状态",
                            font=self.subtitle_font,
                            bg=self.colors['bg_card'],
                            fg=self.colors['text_secondary'])
        status_header.pack(anchor='w', pady=(0, 15))  # 增加下边距与其他部分一致

        # 状态显示区域（保持原有结构）
        status_display_frame = tk.Frame(status_frame, bg=self.colors['accent_light'], relief='flat', bd=0)
        status_display_frame.pack(fill=tk.X, pady=(0, 5))

        self.status_label = tk.Label(status_display_frame,
                                text="正在准备安装...",
                                font=self.status_font,
                                bg=self.colors['accent_light'],
                                fg=self.colors['text_primary'],
                                anchor='w')
        self.status_label.pack(fill=tk.X, padx=15, pady=10)

    def _create_progress_section(self, parent):
        """创建进度条区域"""
        # 进度容器 - 改为卡片式设计与状态区域一致
        progress_container = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        progress_container.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        progress_container.pack(fill=tk.X, pady=(0, 25))

        # 进度标题 - 移到容器内部
        progress_header = tk.Label(progress_container,
                                text="⚡ 安装进度",
                                font=self.subtitle_font,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_secondary'])
        progress_header.pack(anchor='w', padx=30, pady=(20, 15))  # 与状态区域一致

        # 进度条框架（保持原有功能，仅调整样式）
        progress_frame = tk.Frame(progress_container, bg=self.colors['bg_card'])
        progress_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        self.progress = ttk.Progressbar(progress_frame,
                                    length=600,
                                    mode="determinate",
                                    maximum=100,
                                    value=0)
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # 进度信息（保持原有功能）
        progress_info_frame = tk.Frame(progress_frame, bg=self.colors['bg_card'])
        progress_info_frame.pack(fill=tk.X)

        self.progress_percent_label = tk.Label(progress_info_frame,
                                            text="0%",
                                            font=self.progress_font,
                                            bg=self.colors['bg_card'],
                                            fg=self.colors['accent'])
        self.progress_percent_label.pack(side=tk.LEFT)

        self.progress_status_label = tk.Label(progress_info_frame,
                                            text="准备开始...",
                                            font=self.progress_font,
                                            bg=self.colors['bg_card'],
                                            fg=self.colors['text_secondary'])
        self.progress_status_label.pack(side=tk.RIGHT)

    def _create_detail_section(self, parent):
        """创建详细信息区域"""
        # 详情容器 - 改为卡片式设计与前两部分一致
        detail_container = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=1)
        detail_container.configure(highlightbackground=self.colors['border'], highlightthickness=1)
        detail_container.pack(fill=tk.BOTH, expand=True, pady=(0, 25))

        # 详情标题 - 移到容器内部
        detail_header = tk.Label(detail_container,
                            text="📋 安装详情",
                            font=self.subtitle_font,
                            bg=self.colors['bg_card'],
                            fg=self.colors['text_secondary'])
        detail_header.pack(anchor='w', padx=30, pady=(20, 15))  # 与其他部分一致

        # 文本区域（保持原有功能，仅调整容器）
        text_frame = tk.Frame(detail_container, bg=self.colors['bg_card'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        self.detail_text = tk.Text(text_frame,
                                height=50,
                                wrap=tk.WORD,
                                font=self.detail_font,
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'],
                                relief=tk.FLAT,
                                borderwidth=0,
                                padx=15,
                                pady=10,
                                selectbackground=self.colors['accent_light'],
                                selectforeground=self.colors['text_primary'])

        self.scrollbar = ttk.Scrollbar(text_frame, command=self.detail_text.yview)
        self.detail_text.config(yscrollcommand=self.scrollbar.set)

        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 添加欢迎信息
        welcome_text = """🎉 欢迎使用 KouriChat 安装向导！

    ✨ 特色功能：
    • 智能云端配置，自动获取最新软件包
    • 阿里云OSS高速下载 + GitHub备用源
    • 一键安装，无需手动配置
    • 实时进度显示，安装过程透明可见

    🚀 正在初始化安装程序，请稍候...
    """
        self.detail_text.insert(tk.END, welcome_text)
        self.detail_text.config(state=tk.DISABLED)
    
    def _init_animation(self):
        """初始化进度变量和定时器"""
        self.current_progress = 0.0
        self.last_update_time = 0
        # 启动定期UI更新，确保响应性
        self._schedule_ui_update()

    def _bind_events(self):
        """绑定事件"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _start_ui_loop(self):
        """启动UI更新循环"""
        # 简化：不需要复杂的动画循环
        pass

    def _schedule_ui_update(self):
        """定期更新UI以保持响应性"""
        if not self.closed and hasattr(self, 'root') and self.root:
            try:
                # 每20ms处理一次事件，确保UI高响应性
                self.root.after(20, self._schedule_ui_update)
                # 处理用户交互事件，但不阻塞
                self.root.update_idletasks()
                # 定期进行完整更新以防止卡死
                current_time = time.time()
                if not hasattr(self, '_last_full_update'):
                    self._last_full_update = current_time
                if current_time - self._last_full_update > 0.1:  # 每100ms进行一次完整更新
                    self.root.update()
                    self._last_full_update = current_time
            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True
    
    def _on_close(self):
        """处理窗口关闭事件"""
        try:
            # 询问用户是否确认关闭
            result = ctypes.windll.user32.MessageBoxW(
                0,
                "确定要关闭安装程序吗？\n这将中断正在进行的安装过程。",
                "确认关闭",
                0x1034  # MB_YESNO | MB_ICONQUESTION
            )

            # 如果用户选择"是"(返回值为6)，则关闭窗口
            if result == 6:
                self.close()
        except Exception:
            # 如果MessageBox失败，直接关闭窗口
            print("用户请求关闭安装程序")
            self.close()
    
    # 公共接口
    def update_status(self, message: str):
        """更新状态消息"""
        if not self.closed and hasattr(self, 'status_label'):
            try:
                self.status_label.config(text=message)
                # 只更新必要的UI元素，避免频繁的全局更新
                self.root.update_idletasks()
            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True
    
    def update_detail(self, message: str):
        """更新详细信息"""
        if not self.closed and hasattr(self, 'detail_text'):
            try:
                self.detail_text.config(state=tk.NORMAL)
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                formatted_message = f"[{timestamp}] {message}"
                self.detail_text.insert(tk.END, formatted_message + "\n")
                self.detail_text.see(tk.END)
                self.detail_text.config(state=tk.DISABLED)

                # 更频繁的UI更新以保持响应性
                current_time = time.time()
                if not hasattr(self, '_last_detail_update'):
                    self._last_detail_update = 0

                if current_time - self._last_detail_update > 0.01:  # 每10ms更新一次
                    self.root.update_idletasks()
                    self._last_detail_update = current_time

            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True
    
    def set_progress(self, value: float, status: str = None):
        """设置进度条值（改进版本，更好的同步和响应性）"""
        if not self.closed:
            self.current_progress = max(0, min(100, float(value)))

            try:
                # 批量更新UI元素
                if hasattr(self, 'progress') and self.progress:
                    self.progress['value'] = self.current_progress

                if hasattr(self, 'progress_percent_label') and self.progress_percent_label:
                    self.progress_percent_label.config(text=f"{int(self.current_progress)}%")

                if hasattr(self, 'progress_status_label') and self.progress_status_label and status:
                    self.progress_status_label.config(text=status)

                # 更新主状态
                if status and hasattr(self, 'status_label'):
                    self.status_label.config(text=status)

                # 立即更新UI以确保同步
                current_time = time.time()
                if not hasattr(self, '_last_progress_update'):
                    self._last_progress_update = 0

                # 进度更新时立即刷新，但限制频率防止过度更新
                if current_time - self._last_progress_update > 0.02:  # 最多每20ms更新一次
                    self.root.update_idletasks()
                    self._last_progress_update = current_time

                    # 每隔一定时间进行完整更新
                    if current_time - getattr(self, '_last_full_progress_update', 0) > 0.1:
                        self.root.update()
                        self._last_full_progress_update = current_time

            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True
    
    def keep_alive(self):
        """保持窗口响应（改进版本，防止卡死）"""
        if not self.closed and hasattr(self, 'root') and self.root:
            try:
                current_time = time.time()
                # 更频繁的UI更新以防止卡死
                if current_time - self.last_update_time > 0.02:  # 最多每20ms更新一次
                    # 先处理事件队列
                    self.root.update_idletasks()
                    # 然后进行完整更新
                    self.root.update()
                    self.last_update_time = current_time
                else:
                    # 至少处理事件队列
                    self.root.update_idletasks()
            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True

    def force_update(self):
        """强制更新UI，用于长时间操作中保持响应性"""
        if not self.closed and hasattr(self, 'root') and self.root:
            try:
                self.root.update()
                self.last_update_time = time.time()
            except Exception as e:
                if isinstance(e, tk.TclError) and "invalid command name" in str(e):
                    self.closed = True
    
    def close(self):
        """关闭窗口"""
        if not self.closed and hasattr(self, 'root') and self.root:
            self.closed = True
            try:
                self.root.destroy()
            except Exception:
                pass
