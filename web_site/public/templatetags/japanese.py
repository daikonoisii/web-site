from django import template
from lib.japanese import is_japanese

register = template.Library()


def is_ja(string):
    """与えられた文字列が日本語かどうか判定する関数"""
    return is_japanese(string)


register.filter('is_ja', is_ja)
