# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from ...models import OurJournalPaper, OurConferencePaper
import argparse
import csv
from django.db.models.functions import Upper


class Command(BaseCommand):
    help = 'Update Scopus citation with csv input. '  # ヘルプメッセージ
    
    def add_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'))  # 引数を定義
    
    def handle(self, *args, **options):  # 実際の挙動
        data_num = 0
        with options['input'][0] as infile:
            self.stdout.write(self.style.SUCCESS('Citad :   FWCI :                            DOI : Title'))
            for _ in range(0, 12):
                next(infile)  # 一行スキップ
                # line = infile.readline()  # 1行目を読む
            reader = csv.DictReader(infile)  # csvを辞書として読み込む
            for i, row in enumerate(reader):  # 行毎に処理
                journal_list = []
                if row['Authors'] is None:
                    break  # 著者カラムが空欄なら最終行なので終了
                title = row['Title'].replace(' ∗', '')  # IEICEのタイトルにたまに入るアスタリスクを削除
                try:
                    journal_list = OurJournalPaper.objects.annotate(title_upper=Upper('title'))\
                        .filter(title_upper=title.upper())  # 論文誌論文を探す
                except OurJournalPaper.DoesNotExist:
                    pass  # なければスキップ
                try:
                    conference_list = OurConferencePaper.objects.annotate(title_upper=Upper('title')) \
                        .filter(title_upper=title.upper())  # 会議論文を探す
                except OurConferencePaper.DoesNotExist:
                    pass  # なければスキップ
                if len(journal_list) + len(conference_list) > 1:  # 該当が複数ある場合
                    self.stdout.write(self.style.WARNING('Warning: Article ``%s\'\' '
                                                         'overlaps in the database. ' % row['Title']))
                    continue  # 複数あれば警告してスキップ
                elif len(journal_list) + len(conference_list) == 0:
                    self.stdout.write(self.style.WARNING('Warning: Article ``%s\'\' '
                                                         'is not found in the database. ' % row['Title']))
                    continue  # 見つからなければスキップ
                fwci_str = row['Field-Weighted Citation Impact']
                if fwci_str == '-':
                    fwci_str = '----'
                else:
                    fwci_str = '{:>6.2f}'.format(float(fwci_str))
                if row['DOI'] == '-':
                    doi_str = ''
                    doi = None
                else:
                    doi_str = row['DOI']
                    doi = row['DOI']
                self.stdout.write(self.style.SUCCESS('{: >5} : {} : {: >30} : {}'.format(row['Citations'], fwci_str,
                                                                                         doi_str, title)))
                if len(journal_list) == 1:  # 論文誌の場合
                    paper = journal_list[0]
                else:  # 会議の場合
                    paper = conference_list[0]
                paper.fwci = float(row['Field-Weighted Citation Impact'])
                paper.scopus_cite = int(row['Citations'])
                paper.doi = doi
                paper.save()
                data_num += 1
                paper.update_url()  # doiの情報を基にurlを登録
        self.stdout.write(self.style.SUCCESS('Citaions: %s data are updated without error. ' % data_num))
