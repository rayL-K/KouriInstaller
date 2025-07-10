#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端软件安装器 - 主程序入口
高内聚、低耦合的模块化架构
"""

import sys
import ctypes
import os
from main_controller import InstallationController


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新运行程序"""
    try:
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                "",
                None,
                1
            )
        else:
            # 如果是Python脚本
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{os.path.abspath(__file__)}"',
                None,
                1
            )
        return True
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False


def main():
    """主函数"""
    # 检查管理员权限
    if not is_admin():
        print("程序需要管理员权限才能正常运行...")
        print("正在请求管理员权限...")

        if run_as_admin():
            print("已请求管理员权限，程序将重新启动")
            return 0
        else:
            print("无法获取管理员权限，程序可能无法正常安装软件")
            input("按Enter键继续以普通权限运行...")

    controller = None

    try:
        # 创建安装控制器
        controller = InstallationController()

        # 运行安装流程
        success = controller.run_installation()
        
        if success:
            print("安装流程完成")
            return 0
        else:
            print("安装流程失败")
            if not getattr(sys, 'frozen', False):
                input("\n程序已完成，请按Enter键退出...")
            return 1
            
    except Exception as e:
        print(f"程序执行过程中发生未捕获的异常: {str(e)}")
        if getattr(sys, 'frozen', False):
            import ctypes
            try:
                ctypes.windll.user32.MessageBoxW(
                    0, 
                    f"程序发生错误: {str(e)}", 
                    "程序错误", 
                    0x10
                )
            except:
                pass
        
        if not getattr(sys, 'frozen', False):
            input("按Enter键退出...")
        return 1
    finally:
        # 清理资源
        if controller:
            controller.cleanup()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"程序发生未捕获的异常: {str(e)}")
        sys.exit(1)
