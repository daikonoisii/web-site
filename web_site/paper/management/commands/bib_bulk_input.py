# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from ...models import ConferenceTitle, JournalTitle, JournalPaper, \
    ConferencePaper, OurJournalPaper, OurConferencePaper
from users.models import User
from lib.japanese import is_japanese
from lib.latex import latex2escape_char
from django.core.files import File
import argparse
import regex
import re
import datetime


def reformat_address(item):
    """開催地のフォーマットを整える"""
    pattern_address = regex.compile(r'^address\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                    flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_address, item)
    venue = ''
    country = ''
    if match:
        address = match.group(2)
        match2 = regex.search(r'^(.*?), (.*)$', address)  # 開催地を都市名と国名に分離
        if match2:
            venue = match2.group(1)
            country = match2.group(2)
        else:
            venue = address
            if is_japanese(address):
                country = '日本'
    # print('{} -- {}'.format(venue, country))
    return venue, country


def reformat_annote(item):
    """メモのフォーマットを整える"""
    pattern_annote = regex.compile(r'^annote\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                   flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_annote, item)
    abstract = ''
    if match:
        abstract = match.group(2)
    # print(abstract)
    return abstract


def reformat_author(item):
    """著者のフォーマットを整える"""
    pattern_author = regex.compile(r'^author\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                   flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_author, item)
    if match:
        authors_list = []
        bib_authors = match.group(2).split(' and ')
        for a in bib_authors:
            match2 = regex.search(r'^(.*?), (.*)$', a)  # 姓と名前に分離
            if match2:
                name = match2.group(2) + ' ' + match2.group(1)
            else:
                raise Exception('author format "{}" in bib is not supported. ' % a)
            name = latex2escape_char(name)  # LaTeXの拡張文字をUTFに変換
            authors_list.append(name)
    else:
        raise Exception('The author field is required. ')
    # print(authors_list)
    return authors_list  # 第一著者の名字と著者のリストを返す


def reformat_booktitle(item):
    """会議名のフォーマットを整える"""
    pattern_booktitle = regex.compile(r'^booktitle\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                      flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_booktitle, item)
    presentation_id = ''
    organizer = ''
    if match:
        conference_name = match.group(2)
        conference_name = conference_name.replace('Proceedings of ', '')  # Proceedings of を削除
        conference_name = re.sub(r'^the (.*)$', r'The \1', conference_name)  # 先頭の the を The に
        conference_name = latex2escape_char(conference_name)  # LaTeXの拡張文字をUTFに変換
        if '信学技報' in conference_name \
                or 'ソサイエティ大会' in conference_name \
                or '総合大会' in conference_name \
                or '信越支部大会' in conference_name:
            match2 = regex.search(r'^(.*), (.*?)$', conference_name)  # 会議名と研究会などのIDを分離
            if match2:
                conference_name = match2.group(1)
                presentation_id = match2.group(2)
            else:
                raise Exception('Paper ID is not found. ')
        if '信越支部大会' in conference_name:
            organizer = '電子情報通信学会 信越支部'
        elif re.match(r'^IEEE', conference_name) or ' IEEE' in conference_name:
            organizer = 'IEEE'
        elif re.match(r'^IFIP', conference_name) or ' IFIP' in conference_name:
            organizer = 'IFIP'
        elif re.match(r'^ACM', conference_name) or ' ACM' in conference_name or 'SoICT' in conference_name:
            organizer = 'ACM'
        elif re.match(r'^USENIX', conference_name) or ' USENIX' in conference_name:
            organizer = 'USENIX'
        elif '情報ネットワーク研究会' in conference_name:
            organizer = '電子情報通信学会 情報ネットワーク研究会'
        elif 'ネットワークシステム研究会' in conference_name:
            organizer = '電子情報通信学会 情報ネットワーク研究会'
        elif 'インターネットアーキテクチャ研究会' in conference_name:
            organizer = '電子情報通信学会 インターネットアーキテクチャ研究会'
        elif 'コミュニケーションクオリティ' in conference_name:
            organizer = '電子情報通信学会 コミュニケーションクオリティ研究会'
        elif 'クラウドネットワークロボット研究会' in conference_name:
            organizer = '電子情報通信学会 クラウドネットワークロボット研究会'
        elif 'NetSci' in conference_name:
            organizer = '電子情報通信学会 ネットワーク科学研究会'
        elif '電子情報通信学会 総合大会' in conference_name:
            organizer = '電子情報通信学会'
        elif '電子情報通信学会 ソサイエティ大会' in conference_name:
            organizer = '電子情報通信学会'
        elif '待ち行列研究部会' in conference_name:
            organizer = '日本オペレーションズ・リサーチ学会 待ち行列研究部会'
        elif 'ISITA' in conference_name or 'STW' in conference_name:
            organizer = 'IEICE SITA'
        elif 'SITA' in conference_name or 'STW' in conference_name:
            organizer = '電子情報通信学会 基礎・境界ソサイエティ 情報理論とその応用サブソサイエティ'
        elif 'SAINT' in conference_name:
            organizer = 'IEEE Computer Society'
        elif 'International Teletraffic Congress' in conference_name or 'APNOMS' in conference_name:
            organizer = 'IEEE Communication Society'
        elif 'CNSM' in conference_name:
            organizer = 'IFIP'
        elif 'ISAC' in conference_name:
            organizer = 'IEEE Tainan Section'
        elif 'INCoS' in conference_name:
            organizer = 'IEEE Systems, Man and Cybernetics Society Technical Committee on Soft Computing'
        elif '科研費シンポジウム' in conference_name:
            organizer = '日本数学会 統計数学分科会'
    else:
        raise Exception('The booktitle field is required. ')
    # print('{} -- {} -- {}'.format(conference_name, presentation_id, organizer))
    return conference_name, presentation_id, organizer


def reformat_file(item):
    """ファイルのフォーマットを整える"""
    file = None
    pattern_file = regex.compile(r'^file\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                 flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_file, item)
    if match:
        text = match.group(2)
        file_name_list = text.split(';')  # 複数ファイルを分割
        for file_name in file_name_list:
            if ':pdf' in file_name:
                file_name = file_name.replace(':pdf', '')
                file_name = file_name.replace(':', '')
                file_name = '/' + file_name
                if file is None:
                    if regex.match(r'.*\.pdf$', file_name):
                        file = open(file_name, 'rb')
                else:
                    print("WARNING: Multiple pdf files exist. ")
    # print(file)
    return file


def reformat_month(item):
    """月のフォーマットを整える"""
    month2number = {'jan': 1,
                    'feb': 2,
                    'mar': 3,
                    'apr': 4,
                    'may': 5,
                    'jun': 6,
                    'jul': 7,
                    'aug': 8,
                    'sep': 9,
                    'oct': 10,
                    'nov': 11,
                    'dec': 12}
    pattern_month = regex.compile(r'^month\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                  flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_month, item)
    month_num = None
    if match:
        month = match.group(2)
        month_num = month2number[month]  # 文字列を数字に変更
    # print(month_num)
    return month_num


def reformat_page(item):
    """タイトルのフォーマットを整える"""
    pattern_page = regex.compile(r'^pages\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                 flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_page, item)
    page = ''
    if match:
        page = match.group(2)
        page = page.replace('--', '-')
    # print(page)
    return page


def reformat_title(item):
    """タイトルのフォーマットを整える"""
    pattern_title = regex.compile(r'^title\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                  flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_title, item)
    title = ''
    if match:
        title = match.group(2)
    pattern_title = regex.compile(r'^(?<rec>{((?:[^{}]+|(?&rec))*)})$')
    match = regex.search(pattern_title, title)
    if match:
        title = match.group(2)
    # print(title)
    return title


def reformat_journal(item):
    """論文誌名のフォーマットを整える"""
    pattern_journal = regex.compile(r'^journal\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                    flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_journal, item)
    journal = ''
    if match:
        journal = match.group(2)
        journal = latex2escape_char(journal)
    print(journal)
    return journal


def reformat_year(item):
    """年のフォーマットを整える"""
    pattern_year = regex.compile(r'^year\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                 flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_year, item)
    year = ''
    if match:
        year = int(match.group(2))
    # print(year)
    return year


def reformat_publisher(item):
    """出版社のフォーマットを整える"""
    pattern_publisher = regex.compile(r'^publisher\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                      flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_publisher, item)
    publisher = ''
    if match:
        publisher = match.group(2)
        publisher = latex2escape_char(publisher)
    # print(publisher)
    return publisher


def reformat_number(item):
    """Noのフォーマットを整える"""
    pattern_number = regex.compile(r'^number\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                   flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_number, item)
    number = ''
    if match:
        number = match.group(2)
    # print(number)
    return number


def reformat_volume(item):
    """Noのフォーマットを整える"""
    pattern_volume = regex.compile(r'^volume\s*=\s*(?<rec>{((?:[^{}]+|(?&rec))*)})',
                                   flags=(re.MULTILINE | re.DOTALL))
    match = regex.search(pattern_volume, item)
    volume = ''
    if match:
        volume = match.group(2)
    # print(volume)
    return volume


class Command(BaseCommand):
    help = 'Bulk create paper objects with reference.bib input. '  # ヘルプメッセージ
    
    def add_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'))  # 引数を定義
    
    def handle(self, *args, **options):  # 実際の挙動
        data_num = 0
        with options['input'][0] as infile:
            bib = infile.read()
            
            # 会議の抽出
            re_pattern = r"@inproceedings(?<rec>{(?:[^{}]+|(?&rec))*})"
            match_list = regex.findall(re_pattern, bib)

            for item in match_list:
                match = regex.search(r'^{(.*?),$', item, flags=(re.MULTILINE | re.DOTALL))  # citation IDを抽出
                print('\n')
                print(match.group(1))  # citation IDを表示
                venue, country = reformat_address(item)
                abstract = reformat_annote(item)
                authors_list = reformat_author(item)
                conference_name, presentation_id, organizer = reformat_booktitle(item)
                file = reformat_file(item)
                month = reformat_month(item)
                page = reformat_page(item)
                title = reformat_title(item)
                year = reformat_year(item)
                
                # 会議名の追加
                conference_title, created = ConferenceTitle.objects.update_or_create(
                    name=conference_name,
                    defaults={'year': year,
                              'month': month,
                              'venue': venue,
                              'country': country,
                              'organizer': organizer},
                )  # オブジェクトを作成または更新
                conference_title.save()  # データを保存
                
                # 会議論文の追加
                user = User.objects.get(username='kwatabe')
                if '渡部 康平' in authors_list or '渡部康平' in authors_list \
                        or 'Kohei Watabe' in authors_list or 'K. Watabe' in authors_list:  # 研究室内論文
                    author_user = []
                    presenter = authors_list[0]  # 最初のユーザをpresenterに
                    for a in authors_list:
                        a_list = a.split(' ')
                        if len(a_list) > 2:
                            # ToDo: 外国人著者に非対応
                            print('WARNING: This script is not support international students. ')
                        try:
                            temp = User.objects.get(last_name=a_list[0], first_name=a_list[1])
                            author_user.append(temp)
                        except User.DoesNotExist:
                            pass
                        try:
                            temp = User.objects.get(first_name_eng=a_list[0], last_name_eng=a_list[1])
                            author_user.append(temp)
                        except User.DoesNotExist:
                            pass
                    published_date = datetime.date(year, month, 1)
                    # print(author_user)
                    obj, created = OurConferencePaper.objects.update_or_create(
                        title=title,
                        conference_title=conference_title,
                        defaults={'title': title,
                                  'user': user,
                                  'abstract': abstract,
                                  'pdf': File(file),
                                  'author': '\n'.join(authors_list),
                                  'conference_title': conference_title,
                                  'presentation_id': presentation_id,
                                  'page': page,
                                  'published_date': published_date},
                    )  # オブジェクトを作成または更新
                    obj.save()  # データを保存
                    obj.user = user  # ユーザを登録
                    obj.presenter = presenter  # プレセンタを登録
                    for a in author_user:
                        obj.author_user.add(a)  # 研究室内著者を追加
                    pass
                    obj.save()
                else:  # 研究室以外の論文
                    obj, created = ConferencePaper.objects.update_or_create(
                        title=title,
                        conference_title=conference_title,
                        defaults={'title': title,
                                  'user': user,
                                  'abstract': abstract,
                                  'pdf': File(file),
                                  'author': '\n'.join(authors_list),
                                  'conference_title': conference_title,
                                  'presentation_id': presentation_id,
                                  'page': page},
                    )  # オブジェクトを作成または更新
                    obj.save()  # データを保存
                obj.assign_citation_key()  # citation_keyを自動設定
                data_num += 1
            
            # 論文誌の抽出
            re_pattern = r"@article(?<rec>{(?:[^{}]+|(?&rec))*})"
            match_list = regex.findall(re_pattern, bib)
            
            for item in match_list:
                match = regex.search(r'^{(.*?),$', item, flags=(re.MULTILINE | re.DOTALL))  # citation IDを抽出
                print('\n')
                print(match.group(1))  # citation IDを表示
                abstract = reformat_annote(item)
                authors_list = reformat_author(item)
                file = reformat_file(item)
                month = reformat_month(item)
                page = reformat_page(item)
                title = reformat_title(item)
                journal_name = reformat_journal(item)
                year = reformat_year(item)
                publisher = reformat_publisher(item)
                number = reformat_number(item)
                volume = reformat_volume(item)
                
                # 論文誌名の追加
                journal_title, created = JournalTitle.objects.update_or_create(
                    name=journal_name,
                    defaults={'publisher': publisher},
                )  # オブジェクトを作成または更新
                journal_title.save()  # データを保存
                
                # 論文誌論文の追加
                user = User.objects.get(username='kwatabe')
                if '渡部 康平' in authors_list or '渡部康平' in authors_list \
                        or 'Kohei Watabe' in authors_list or 'K. Watabe' in authors_list:  # 研究室内論文
                    author_user = []
                    for a in authors_list:
                        a_list = a.split(' ')
                        if len(a_list) > 2:
                            # ToDo: 外国人著者に非対応
                            print('WARNING: This script is not support international students. ')
                        try:
                            temp = User.objects.get(last_name=a_list[0], first_name=a_list[1])
                            author_user.append(temp)
                        except User.DoesNotExist:
                            pass
                        try:
                            temp = User.objects.get(first_name_eng=a_list[0], last_name_eng=a_list[1])
                            author_user.append(temp)
                        except User.DoesNotExist:
                            pass
                    published_date = datetime.date(year, month, 1)
                    # print(author_user)
                    obj, created = OurJournalPaper.objects.update_or_create(
                        title=title,
                        journal_title=journal_title,
                        defaults={'title': title,
                                  'user': user,
                                  'abstract': abstract,
                                  'pdf': File(file),
                                  'author': '\n'.join(authors_list),
                                  'journal_title': journal_title,
                                  'volume': volume,
                                  'number': number,
                                  'year': year,
                                  'month': month,
                                  'page': page,
                                  'published_date': published_date},
                    )  # オブジェクトを作成または更新
                    obj.save()  # データを保存
                    for a in author_user:
                        obj.author_user.add(a)  # 研究室内著者を追加
                    obj.save()
                else:  # 研究室以外の論文
                    obj, created = JournalPaper.objects.update_or_create(
                        title=title,
                        journal_title=journal_title,
                        defaults={'title': title,
                                  'user': user,
                                  'abstract': abstract,
                                  'pdf': File(file),
                                  'author': '\n'.join(authors_list),
                                  'journal_title': journal_title,
                                  'volume': volume,
                                  'number': number,
                                  'year': year,
                                  'month': month,
                                  'page': page},
                    )  # オブジェクトを作成または更新
                    obj.save()  # データを保存
                obj.assign_citation_key()  # citation_keyを自動設定
                data_num += 1
        self.stdout.write(self.style.SUCCESS('%s data are created without error. ' % data_num))
