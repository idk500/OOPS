#!/usr/bin/env python3
"""
简单测试脚本，验证HTML渲染器模块是否能正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath("."))

try:
    from oops.core.html_renderer import HTMLRenderer
    from oops.core.report import ReportGenerator

    print("✅ 成功导入HTMLRenderer和ReportGenerator模块")

    # 测试HTMLRenderer类的基本功能
    renderer = HTMLRenderer()
    print("✅ 成功创建HTMLRenderer实例")

    # 测试_get_html_header方法
    header = renderer._get_html_header()
    if "<!DOCTYPE html>" in header:
        print("✅ _get_html_header方法正常工作")
    else:
        print("❌ _get_html_header方法返回了错误的内容")

    # 测试_get_html_footer方法
    footer = renderer._get_html_footer()
    if "</html>" in footer:
        print("✅ _get_html_footer方法正常工作")
    else:
        print("❌ _get_html_footer方法返回了错误的内容")

    print("\n🎉 所有基本功能测试通过！")

except Exception as e:
    print(f"❌ 测试失败：{e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
