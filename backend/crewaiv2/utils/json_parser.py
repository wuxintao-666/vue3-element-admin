# json_parser.py - JSON解析相关工具函数
import json
import html
import re
from json_repair import repair_json

def parse_json_from_text(text):
    """从文本中解析JSON对象，支持json_repair修复"""
    if not text:
        return None

    # 如果是字符串，尝试解析为JSON
    if isinstance(text, str):
        try:
            # 尝试直接解析
            parsed = json.loads(text)
            print(f"✅ JSON直接解析成功")
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON直接解析失败: {str(e)[:100]}...")
            try:
                # 使用json_repair库修复并解析
                print(f"🔧 尝试使用json_repair修复...")
                repaired_json_str = repair_json(text)
                parsed = json.loads(repaired_json_str)
                print(f"✅ JSON修复成功！修复前后长度: {len(text)} → {len(repaired_json_str)}")
                return parsed
            except Exception as e2:
                print(f"❌ json_repair修复失败: {str(e2)[:100]}...")
                # 最后的尝试：提取JSON部分并修复
                try:
                    print(f"🔍 尝试提取JSON片段并修复...")
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = text[start:end]
                        print(f"📄 提取的JSON片段长度: {len(json_str)}")
                        repaired_json_str = repair_json(json_str)
                        parsed = json.loads(repaired_json_str)
                        print(f"✅ JSON片段修复成功！")
                        return parsed
                    else:
                        print(f"❌ 未找到有效的JSON片段")
                except Exception as e3:
                    print(f"❌ JSON片段修复也失败: {str(e3)[:100]}...")

    # 如果已经是字典，直接返回
    elif isinstance(text, dict):
        print(f"✅ 输入已是JSON对象")
        return text

    print(f"❌ 无法解析输入内容 (类型: {type(text)})")
    return None

def extract_answer_code_from_structured_json(data):
    """从结构化数据中提取答案代码"""
    if not data:
        print("❌ 数据为空")
        return ""

    try:
        # 解析数据
        if isinstance(data, str):
            # 如果是字符串，尝试解析
            json_data = parse_json_from_text(data)
            if not json_data:
                print("❌ 无法从字符串解析JSON")
                return ""
        elif isinstance(data, dict):
            json_data = data
        else:
            print(f"❌ 不支持的数据类型: {type(data)}")
            return ""

        # 检查是否包含answer字段
        if "answer" not in json_data:
            # 尝试查找其他可能的字段名
            possible_keys = ["solution", "reference", "code", "result"]
            for key in possible_keys:
                if key in json_data:
                    # 直接返回这个字段的值
                    if isinstance(json_data[key], dict):
                        return build_html_from_code_dict(json_data[key])
                    else:
                        return str(json_data[key])

            print("❌ JSON中没有找到answer字段")
            print(f"JSON内容: {json.dumps(json_data, indent=2)[:500]}...")
            return ""

        answer = json_data["answer"]

        # 如果answer是字符串，直接返回
        if isinstance(answer, str):
            return answer

        # 如果answer是字典，提取各部分
        if isinstance(answer, dict):
            return build_html_from_code_dict(answer)

        # 其他情况，转换为字符串
        return str(answer)

    except Exception as e:
        print(f"❌ 从JSON提取答案代码失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def extract_html_code(text):
    """从文本中提取HTML代码，支持新的JSON格式"""
    if not text:
        return ""

    import re
    import html
    import json

    # 先解码可能的HTML实体
    decoded_text = html.unescape(text)

    # 首先尝试解析JSON格式（新的测试题格式）
    try:
        # 查找JSON对象
        json_start = decoded_text.find('{')
        json_end = decoded_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = decoded_text[json_start:json_end]
            test_data = json.loads(json_str)

            # 从新的JSON格式中提取答案
            if 'answer' in test_data:
                answer = test_data['answer']
                html_code = answer.get('html', '')
                css_code = answer.get('css', '')
                js_code = answer.get('js', '')

                # 组合成完整的HTML
                full_html = html_code
                if css_code:
                    # 如果有CSS，插入到head中
                    if '<head>' in full_html and '</head>' in full_html:
                        head_end = full_html.find('</head>')
                        full_html = full_html[:head_end] + f'\n<style>\n{css_code}\n</style>\n' + full_html[head_end:]
                    else:
                        full_html = f'<style>\n{css_code}\n</style>\n' + full_html

                if js_code:
                    # 如果有JS，插入到body末尾
                    if '</body>' in full_html:
                        body_end = full_html.find('</body>')
                        full_html = full_html[:body_end] + f'\n<script>\n{js_code}\n</script>\n' + full_html[body_end:]
                    else:
                        full_html += f'\n<script>\n{js_code}\n</script>'

                return full_html.strip()
    except (json.JSONDecodeError, KeyError, ValueError):
        # 如果JSON解析失败，继续使用原来的方法
        pass

    # 回退到原来的方法：提取代码块
    patterns = [
        r'```html\s*(.*?)\s*```',  # 首先尝试html标记的代码块
        r'```\s*(.*?)\s*```',      # 然后尝试普通代码块
    ]

    for pattern in patterns:
        matches = re.findall(pattern, decoded_text, re.DOTALL)
        if matches:
            # 取最后一个匹配（通常是答案代码）
            code = matches[-1].strip()
            # 清理常见的转义序列
            code = code.replace('\\\\n', '\n').replace('\\n', '\n')
            code = code.replace('\\\\t', '\t').replace('\\t', '\t')
            return code

    # 如果没有代码块，直接查找HTML结构
    html_start = decoded_text.find('<!DOCTYPE')
    if html_start == -1:
        html_start = decoded_text.find('<html')

    if html_start != -1:
        html_end = decoded_text.find('</html>', html_start)
        if html_end != -1:
            code = decoded_text[html_start:html_end+7].strip()
            # 清理转义
            code = code.replace('\\\\n', '\n').replace('\\n', '\n')
            code = code.replace('\\\\t', '\t').replace('\\t', '\t')
            return code

    # 返回清理后的文本
    cleaned = decoded_text.replace('\\\\n', '\n').replace('\\n', '\n')
    cleaned = cleaned.replace('\\\\t', '\t').replace('\\t', '\t')
    return cleaned.strip()

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