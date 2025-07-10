#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热更新功能使用示例
演示如何在自己的项目中集成热更新功能
"""

from core.hot_updater import HotUpdater


def simple_progress_callback(callback_type: str, data):
    """简单的进度回调函数"""
    if callback_type == 'progress':
        progress, status = data
        print(f"进度: {progress:.1f}% - {status}")
    elif callback_type == 'detail':
        print(f"详情: {data}")


def main():
    """主函数"""
    print("🔥 热更新功能使用示例")
    print("=" * 50)
    
    # 创建热更新器
    updater = HotUpdater(simple_progress_callback)
    
    # 执行热更新
    success = updater.perform_hot_update()
    
    if success:
        print("✅ 热更新检查完成")
    else:
        print("❌ 热更新检查失败")
    
    print("🎉 示例运行完成！")
    return 0


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)

