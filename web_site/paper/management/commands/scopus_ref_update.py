# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from ...models import JournalTitle, ConferenceTitle
import argparse
import re
import json
import pandas as pd
from collections import OrderedDict


class Command(BaseCommand):
    help = 'Update Scopus journals/conferences impact with xlsx input. '  # ヘルプメッセージ
    
    def add_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'))  # 引数を定義
    
    def handle(self, *args, **options):  # 実際の挙動
        title_relation = {'Proceedings - IEEE INFOCOM': 'IEEE International Conference '
                                                        'on Computer Communication (INFOCOM ',
                          'IEEE Transactions on Information Theory': 'IEEE Transactions on Information Theory',
                          'Simulation Modelling Practice and Theory': 'Simulation Modelling Practice and Theory',
                          'PLoS ONE': 'PLOS ONE',
                          'Proceedings - International Conference on Distributed Computing Systems':
                              'International Conference on Distributed Computing Systems (ICDCS ',
                          'Conference Record - International Conference on Communications':
                              'IEEE International Conference on Communications (ICC ',
                          'Ad-Hoc and Sensor Wireless Networks': 'Ad Hoc & Sensor Wireless Networks',
                          'IEICE Transactions on Communications': 'IEICE Transactions on Communications',
                          'ACM International Conference Proceeding Series':
                              'International Symposium on Information and Communication Technology (SoICT '}
        data_num = 0
        with options['input'][0] as infile:
            self.stdout.write(self.style.SUCCESS('CiteScore : Percentile :  SNIP : Title'))
            xlsx = pd.read_excel(infile.name, engine='openpyxl')
            columns = xlsx.columns
            for c in columns:
                match_obj = re.match(r'([0-9]*) Citations', c)  # SNIPのフィールド名か調べる
                if match_obj:  # 年を抽出
                    year = int(match_obj.group(1))
                    break  # 見つけたら終了
            for line in xlsx.values:
                (scopus_title, cite_score, highest_percentile, _, _, _, snip, sjr, _) = line
                if type(highest_percentile) is str:
                    highest_percentile_short = highest_percentile.split('\n')[0]  # %部分のみ
                    highest_percentile = highest_percentile.replace('\n', ', ')
                else:  # N/Aなどの場合
                    highest_percentile_short = '-----'
                try:
                    journal_list = JournalTitle.objects.filter(name=title_relation[scopus_title])  # 論文誌論文を探す
                except JournalTitle.DoesNotExist:
                    pass  # なければスキップ
                try:
                    conference_list = ConferenceTitle.objects\
                        .filter(name__icontains=title_relation[scopus_title], year=year)  # 会議論文を探す
                except ConferenceTitle.DoesNotExist:
                    pass  # なければスキップ
                for journal in journal_list:  # 該当するすべての論文誌について
                    snip = '{:.3f}'.format(snip)
                    snip = snip.replace('nan', '-----')
                    cite_score = '{:.3f}'.format(cite_score)
                    cite_score = cite_score.replace('nan', '-----')
                    self.stdout.write(self.style.SUCCESS('    {} :      {} : {} : {}'.format(cite_score, highest_percentile_short,
                                                                                    snip, journal.name)))
                    
                    # SNIP更新
                    snip_dict = {}  # 初期化
                    if journal.snip is not None:
                        try:
                            snip_dict = json.loads(journal.snip)  # jsonを辞書として読み込み
                        except json.decoder.JSONDecodeError:
                            pass  # エラーなら空の辞書のまま
                    if snip == '-----':
                        if str(year) in snip_dict:  # キーが存在して
                            del snip_dict[str(year)]  # N/Aなら削除
                    else:
                        snip_dict[str(year)] = float(snip)  # SNIPを追加
                    ordered_snip_dict = OrderedDict(sorted(snip_dict.items(), reverse=True))  # 並べ替え
                    journal.snip = json.dumps(ordered_snip_dict)
                    
                    # CiteScore更新
                    cite_score_dict = {}  # 初期化
                    if journal.cite_score is not None:
                        try:
                            cite_score_dict = json.loads(journal.cite_score)  # jsonを辞書として読み込み
                        except json.decoder.JSONDecodeError:
                            pass  # エラーなら空の辞書のまま
                    if cite_score == '-----':
                        if str(year) in cite_score_dict:  # キーが存在して
                            del cite_score_dict[str(year)]  # N/Aなら削除
                    else:
                        cite_score_dict[str(year)] = float(cite_score)  # CiteScoreを追加
                    ordered_cite_score_dict = OrderedDict(sorted(cite_score_dict.items(), reverse=True))  # 並べ替え
                    journal.cite_score = json.dumps(ordered_cite_score_dict)

                    # Highest percentile更新
                    highest_percentile_dict = {}  # 初期化
                    if journal.highest_percentile is not None:
                        try:
                            highest_percentile_dict = json.loads(journal.highest_percentile)  # jsonを辞書として読み込み
                        except json.decoder.JSONDecodeError:
                            pass  # エラーなら空の辞書のまま
                    if highest_percentile == 'nan':
                        if str(year) in highest_percentile_dict:  # キーが存在して
                            del highest_percentile_dict[str(year)]  # N/Aなら削除
                    else:
                        highest_percentile_dict[str(year)] = highest_percentile  # CiteScoreを追加
                    ordered_highest_percentile_dict = OrderedDict(sorted(highest_percentile_dict.items(), reverse=True))  # 並べ替え
                    journal.highest_percentile = json.dumps(ordered_highest_percentile_dict)
                    
                    journal.save()
                    data_num += 1
                for conference in conference_list:  # 会議の場合
                    conference.snip = snip
                    conference.cite_score = cite_score
                    conference.highest_percentile = highest_percentile
                    snip = '{:.3f}'.format(snip)
                    snip = snip.replace('nan', '-----')
                    cite_score = '{:.3f}'.format(cite_score)
                    cite_score = cite_score.replace('nan', '-----')
                    self.stdout.write(self.style.SUCCESS('    {} :      {} : {} : {}'.format(cite_score, highest_percentile_short,
                                                                                    snip, conference.name)))
                    conference.save()
                    data_num += 1
        self.stdout.write(self.style.SUCCESS('Journals/Conferences: %s data are updated without error. ' % data_num))
