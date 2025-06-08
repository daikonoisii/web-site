# -*- coding: utf-8 -*-
#
# FileName      : slack_webhooks.py
# CreatedDate   : 2019/03/29
#

import sys
import requests
import json


def webhook(*args):
    proxies = {
        'http': 'http://proxy.nagaokaut.ac.jp:8080',
        'https': 'http://proxy.nagaokaut.ac.jp:8080',
    }

    WEB_HOOK_URL = "https://hooks.slack.com/services/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"

    msg = '投稿情報：{category}\n\n'

    if args[0] == 'コメント':
        msg += 'To：{to_user}\nFrom：{user}\n'
        msg += '> 内容：\n> {body}'

        msg = msg.format(category=args[0], to_user=args[1], user=args[2], body=findn_newline(args[3]))

    elif args[0] == 'レポート':
        category = {
            '1': 'ゼミ資料',
            '2': '論文レポート',
            '6': 'サイドプロジェクト',
            '9': 'その他',
        }

        msg += 'From：{user}\n\nCategory：{post_category}\n'
        msg += '> Title：{title}\n> \n'
        msg += '> Abstract：\n> {abstract}'

        msg = msg.format(category=args[0], user=args[1], post_category=category[args[2]], title=args[3], abstract=findn_newline(args[4]))

    data = json.dumps({'text': msg})

    requests.post(WEB_HOOK_URL, data, proxies=proxies)


def findn_newline(msg):
    new_text = []
    for s in list(msg):
        if s == "\n":
            new_text += ">"
        else:
            new_text += s

    return ''.join(new_text)


def main(args):
    webhook(args[1])


if __name__ == '__main__':
    main(sys.argv)
