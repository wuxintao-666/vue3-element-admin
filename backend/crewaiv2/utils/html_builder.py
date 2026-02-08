# html_builder.py - HTML构建工具函数

def build_html_from_code_dict(code_dict):
    """从代码字典构建完整的HTML"""
    if not isinstance(code_dict, dict):
        return str(code_dict)

    html_code = code_dict.get("html", "")
    css_code = code_dict.get("css", "")
    js_code = code_dict.get("js", "")

    # 如果html_code已经是完整的HTML文档，直接返回
    if html_code.strip().startswith("<!DOCTYPE") or html_code.strip().startswith("<html"):
        # 但可能需要插入CSS和JS
        full_html = html_code

        # 插入CSS
        if css_code and "<style>" not in full_html:
            if "</head>" in full_html:
                head_end = full_html.find("</head>")
                full_html = full_html[:head_end] + f"\n<style>\n{css_code}\n</style>" + full_html[head_end:]
            else:
                # 在html标签后添加head
                if "<html" in full_html and ">" in full_html:
                    html_end = full_html.find(">", full_html.find("<html")) + 1
                    full_html = full_html[:html_end] + f"\n<head>\n<style>\n{css_code}\n</style>\n</head>" + full_html[html_end:]

        # 插入JS
        if js_code and "<script>" not in full_html:
            if "</body>" in full_html:
                body_end = full_html.find("</body>")
                full_html = full_html[:body_end] + f"\n<script>\n{js_code}\n</script>" + full_html[body_end:]
            else:
                full_html += f"\n<script>\n{js_code}\n</script>"

        return full_html

    # 构建完整的HTML文档
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>练习页面</title>
"""

    if css_code:
        full_html += f"    <style>\n{css_code}\n    </style>\n"

    full_html += f"""</head>
<body>
{html_code}
"""

    if js_code:
        full_html += f"""    <script>
{js_code}
    </script>
"""

    full_html += "</body>\n</html>"

    return full_html