# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from ...models import JournalTitle
import argparse
import csv
import json
import re
from collections import OrderedDict
from django.db.models.functions import Upper


class Command(BaseCommand):
    help = 'Update Impact Factor with csv input. '  # ヘルプメッセージ
    
    def add_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'))  # 引数を定義
    
    def handle(self, *args, **options):  # 実際の挙動
        data_num = 0
        with options['input'][0] as infile:
            # next(infile)  # 一行スキップ
            line = infile.readline()  # 1行目を読む
            match_obj = re.match(r'.*JCR Year: ([0-9]*) .*', line)  # 年を抽出
            year = match_obj.group(1)
            reader = csv.DictReader(infile)  # csvを辞書として読み込む
            for i, row in enumerate(reader):  # 行毎に処理
                try:
                    journal_title = JournalTitle.objects.annotate(name_upper=Upper('name'))\
                        .get(name_upper=row['Full Journal Title'].upper())  # 論文誌を探す
                except JournalTitle.DoesNotExist:
                    continue  # なければスキップ
                score_dict = {}  # 初期化
                if journal_title.impact_factor is not None:
                    try:
                        score_dict = json.loads(journal_title.impact_factor)  # jsonを辞書として読み込み
                    except json.decoder.JSONDecodeError:
                        pass  # エラーなら空の辞書のまま
                print(journal_title.name)
                score_dict[year] = float(row['Journal Impact Factor'])  # IFを追加
                ordered_score_dict = OrderedDict(sorted(score_dict.items(), reverse=True))  # 並べ替え
                journal_title.impact_factor = json.dumps(ordered_score_dict)
                journal_title.save()
                data_num += 1
        self.stdout.write(self.style.SUCCESS('%s data are updated without error. ' % data_num))
