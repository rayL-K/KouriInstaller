#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云下发配置管理工具
用于配置和管理云端下载源
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sys

class CloudConfigManager:
    """云下发配置管理器GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("云下发配置管理器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 配置文件路径
        self.config_path = Path("cloud_config.json")
        
        # 当前配置
        self.config = self.load_config()
        
        # 创建UI
        self.create_ui()
        
        # 加载配置到UI
        self.load_config_to_ui()
    
    def load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {e}")
        
        # 返回默认配置
        return {
            "base_url": "",
            "packages": [],
            "version": "1.0.0"
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置根目录
        ttk.Label(main_frame, text="基础URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.base_url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.base_url_var, width=60).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 包列表
        ttk.Label(main_frame, text="安装包配置:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        
        # 包列表框架
        packages_frame = ttk.Frame(main_frame)
        packages_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 创建Treeview
        columns = ('name', 'url', 'size', 'description', 'type')
        self.packages_tree = ttk.Treeview(packages_frame, columns=columns, show='headings', height=15)

        # 设置列标题
        self.packages_tree.heading('name', text='文件名')
        self.packages_tree.heading('url', text='下载URL')
        self.packages_tree.heading('size', text='大小(MB)')
        self.packages_tree.heading('description', text='描述')
        self.packages_tree.heading('type', text='类型')

        # 设置列宽
        self.packages_tree.column('name', width=150)
        self.packages_tree.column('url', width=250)
        self.packages_tree.column('size', width=80)
        self.packages_tree.column('description', width=120)
        self.packages_tree.column('type', width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(packages_frame, orient=tk.VERTICAL, command=self.packages_tree.yview)
        self.packages_tree.configure(yscrollcommand=scrollbar.set)
        
        self.packages_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 按钮框架
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=1, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="添加包", command=self.add_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="编辑包", command=self.edit_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="删除包", command=self.delete_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="保存配置", command=self.save_config_from_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="加载配置", command=self.load_config_from_file).pack(side=tk.LEFT, padx=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        packages_frame.columnconfigure(0, weight=1)
        packages_frame.rowconfigure(0, weight=1)
    
    def load_config_to_ui(self):
        """将配置加载到UI"""
        self.base_url_var.set(self.config.get("base_url", ""))
        
        # 清空现有项目
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        # 添加包到树视图
        for package in self.config.get("packages", []):
            size_mb = package.get("size", 0) // (1024 * 1024)

            # 确定文件类型
            file_name = package.get("name", "")
            if file_name.lower().endswith('.zip'):
                file_type = "ZIP压缩包"
            elif file_name.lower().endswith('.exe'):
                file_type = "可执行文件"
            else:
                file_type = "其他文件"

            self.packages_tree.insert('', 'end', values=(
                package.get("name", ""),
                package.get("url", ""),
                f"{size_mb}",
                package.get("description", ""),
                file_type
            ))
    
    def save_config_from_ui(self):
        """从UI保存配置"""
        self.config["base_url"] = self.base_url_var.get()
        
        # 收集包信息
        packages = []
        for item in self.packages_tree.get_children():
            values = self.packages_tree.item(item, 'values')
            if len(values) >= 4:
                try:
                    size_mb = int(values[2]) if values[2].isdigit() else 0
                    size_bytes = size_mb * 1024 * 1024
                except:
                    size_bytes = 0

                package_info = {
                    "name": values[0],
                    "url": values[1],
                    "size": size_bytes,
                    "description": values[3],
                    "md5": ""
                }

                # 如果是ZIP文件，添加解压配置
                if values[0].lower().endswith('.zip'):
                    package_info["extract_to"] = "."
                    package_info["post_download"] = "extract"

                packages.append(package_info)
        
        self.config["packages"] = packages
        self.save_config()
    
    def add_package(self):
        """添加新包"""
        self.edit_package_dialog()
    
    def edit_package(self):
        """编辑选中的包"""
        selection = self.packages_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个包")
            return
        
        item = selection[0]
        values = self.packages_tree.item(item, 'values')
        self.edit_package_dialog(item, values)
    
    def delete_package(self):
        """删除选中的包"""
        selection = self.packages_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个包")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的包吗？"):
            for item in selection:
                self.packages_tree.delete(item)
    
    def edit_package_dialog(self, item=None, values=None):
        """包编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑包" if item else "添加包")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 变量
        name_var = tk.StringVar(value=values[0] if values else "")
        url_var = tk.StringVar(value=values[1] if values else "")
        size_var = tk.StringVar(value=values[2] if values else "0")
        desc_var = tk.StringVar(value=values[3] if values else "")

        # 检测文件类型
        is_zip = name_var.get().lower().endswith('.zip') if values else False
        
        # 创建表单
        ttk.Label(dialog, text="文件名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=name_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="下载URL:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=url_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="大小(MB):").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=size_var, width=50).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="描述:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(dialog, textvariable=desc_var, width=50).grid(row=3, column=1, padx=10, pady=5)

        # 如果是ZIP文件，显示提示
        if is_zip:
            info_label = ttk.Label(dialog, text="注意: ZIP文件将自动解压到程序目录", foreground="blue")
            info_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # 按钮
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_package():
            if not name_var.get() or not url_var.get():
                messagebox.showerror("错误", "文件名和URL不能为空")
                return
            
            # 确定文件类型
            file_name = name_var.get()
            if file_name.lower().endswith('.zip'):
                file_type = "ZIP压缩包"
            elif file_name.lower().endswith('.exe'):
                file_type = "可执行文件"
            else:
                file_type = "其他文件"

            new_values = (name_var.get(), url_var.get(), size_var.get(), desc_var.get(), file_type)

            if item:
                self.packages_tree.item(item, values=new_values)
            else:
                self.packages_tree.insert('', 'end', values=new_values)
            
            dialog.destroy()
        
        ttk.Button(buttons_frame, text="保存", command=save_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_config_from_file(self):
        """从文件加载配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.load_config_to_ui()
                messagebox.showinfo("成功", "配置文件加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {e}")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = CloudConfigManager()
    app.run()
