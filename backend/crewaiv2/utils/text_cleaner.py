# text_cleaner.py - 文本清理工具函数

def clean_escape_chars(text):
    """清理字符串中的转义字符（只清理一次）"""
    if not text:
        return ""

    # 只做一次清理，避免叠加
    replacements = [
        ('\\\\n', '\n'),  # 双重转义的换行符
        ('\\n', '\n'),    # 转义的换行符
        ('\\\\t', '\t'),  # 双重转义的制表符
        ('\\t', '\t'),    # 转义的制表符
        ('\\\\"', '"'),   # 双重转义的双引号
        ('\\"', '"'),     # 转义的双引号
        ("\\\\'", "'"),   # 双重转义的单引号
        ("\\'", "'"),     # 转义的单引号
    ]

    cleaned = text
    for old, new in replacements:
        cleaned = cleaned.replace(old, new)

    return cleaned