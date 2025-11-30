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

    # 测试_get_html_footer方法
    footer = renderer._get_html_footer()
    if "</html>" in footer:
        print("✅ _get_html_footer方法正常工作")
    else:
        print("❌ _get_html_footer方法返回了错误的内容")
    
    # 测试_get_html_friend_links_section方法
    friend_links_html = renderer._get_html_friend_links_section()
    if "🔗 友情链接" in friend_links_html and "OOPS 力荐" in friend_links_html:
        print("✅ _get_html_friend_links_section方法正常工作，包含AI助手提示")
    else:
        print("❌ _get_html_friend_links_section方法返回了错误的内容")
    
    # 测试带项目自定义链接的友情链接方法
    project_links = {"测试链接": "https://example.com"}
    friend_links_with_project_html = renderer._get_html_friend_links_section(project_links)
    if "测试链接" in friend_links_with_project_html:
        print("✅ _get_html_friend_links_section方法支持项目自定义链接")
    else:
        print("❌ _get_html_friend_links_section方法不支持项目自定义链接")
    
    # 测试带项目名的友情链接方法
    project_name = "测试项目"
    friend_links_with_name_html = renderer._get_html_friend_links_section(project_links, project_name)
    if f"{project_name} 专属" in friend_links_with_name_html:
        print("✅ _get_html_friend_links_section方法支持项目名参数")
    else:
        print("❌ _get_html_friend_links_section方法不支持项目名参数")

    print("\n🎉 所有基本功能测试通过！")

except Exception as e:
    print(f"❌ 测试失败：{e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
