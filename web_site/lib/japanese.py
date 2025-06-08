import unicodedata


def is_japanese(string):
    """与えられた文字列が日本語かどうか判定する関数"""
    string = string.replace('\r', '')
    string = string.replace('\n', '')
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return True
    return False


def is_all_katakana(string):
    """与えられた文字列がすべてカタカナかどうか判定する関数"""
    string = string.replace('\r', '')
    string = string.replace(' ', '')
    for ch in string:
        name = unicodedata.name(ch)
        if "KATAKANA" not in name:
            return False
    return True
