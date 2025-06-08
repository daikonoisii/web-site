from django.db import models
from users.models import User
from django.core.validators import RegexValidator, FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from lib.japanese import is_japanese, is_all_katakana
from lib.latex import escape_char2ascii
from public.models import Research
import re
import os
import string
import json

MONTH_CHOICE = [(r, r) for r in range(1, 13)]  # 月の選択肢


class Tag(models.Model):
    """タグクラス"""
    name = models.CharField('タグ名', unique=True, max_length=30)  # タグ
    
    def __str__(self):
        return str(self.name)


def get_upload_to(instance, _):
    """PDFのアップロード先を定義"""
    filename = instance.title
    filename = re.sub(r'[\\/:?."<>| ]', '_', filename)  # ファイル名に使えない文字を置き換え
    filename = filename.lower()  # すべて小文字に
    filename = filename + '.pdf'
    return os.path.join('paper/', filename)


def get_upload_to_post_print(instance, _):
    """post-printのPDFアップロード先を定義"""
    return 'post_print_' + get_upload_to(instance, _)


def get_upload_to_pre_print(instance, _):
    """pre-printのPDFアップロード先を定義"""
    return 'pre_print_' + get_upload_to(instance, _)


def get_upload_to_presentation_pdf(instance, _):
    """プレゼンテーションのPDFアップロード先を定義"""
    return 'presentation_pdf_' + get_upload_to(instance, _)


class Reference(models.Model):
    """文献クラス"""
    citation_key = models.CharField('引用コード', default=None, null=True, unique=True, max_length=30,
                                    help_text='第一著者名と出版年から自動で生成されます．')
    # すべて大文字の場合はエラー
    uppercase_validator = RegexValidator(
        regex=r"^[A-Z\s:;\-~?']*$",
        inverse_match=True,
        message="すべて大文字で入力することはできません．"
    )
    title = models.CharField('タイトル',
                             max_length=300,
                             validators = [uppercase_validator],
                             help_text='文献のタイトルを入力してください．\n'
                                       '数式や数学記号を含む場合は，$\\lambda$のように$マークで挟んだLaTeX形式で入力してください．．')
    user = models.ForeignKey(
        User,
        related_name='user_papers',
        on_delete=models.CASCADE,
        verbose_name='登録ユーザ',
        null=True,
    )  # 作成ユーザ
    abstract = models.TextField('メモ', blank=True, help_text='内容に関するメモを記入してください．')
    tag = models.ManyToManyField(Tag, verbose_name='タグ', related_name='tag', blank=True,
                                 help_text='関連するタグを付与してください．一覧になければ，新しく登録してください．')
    pdf_validator = FileExtensionValidator(
        ['pdf', ],
        message="PDFファイルを添付してださい．"
    )
    pdf = models.FileField(
        blank=True,
        upload_to=get_upload_to,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='原稿のファイルを登録してください．'
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='登録日'
    )
    
    preposition = ['a', 'an', 'the', 'and', 'as', 'but', 'for', 'if', 'nor', 'once', 'or', 'so', 'than',
                   'till', 'when', 'yet', 'at', 'by', 'down', 'for', 'from', 'in', 'into', 'like', 'near',
                   'of', 'off', 'on', 'onto', 'out', 'over', 'past', 'to', 'up', 'upon', 'with', 'via']  # 前置詞一覧
    
    def title_capitalize(self, title):
        """タイトルを自動でキャピタライズ"""
        if not is_japanese(title):
            word_list = title.split(' ')
            new_word_list = []
            for i, a_word in enumerate(word_list):
                sub_word_list = a_word.split('-')  # さらにハイフンで分解
                for j, s in enumerate(sub_word_list):
                    if not re.match(r'.*[A-Z].*', s[1:]):  # 2文字目以降に大文字を含まない場合(大文字の略語などではない場合)
                        if not re.match(r'[$\\]', s):  # LaTeX記号などが含まれていない場合
                            if s not in self.preposition or i == 0:  # 先頭でなく，前置詞等でなければ
                                sub_word_list[j] = s.title()  # 先頭を大文字に
                new_word_list.append('-'.join(sub_word_list))  # 再結合して追加
            title = ' '.join(new_word_list)  # 再結合
            self.title = title
            self.save()
    
    def assign_citation_key(self):
        """citation_keyを自動設定"""
        self.citation_key = str(self.id)  # 引用キーを自動入力
        self.save()
    
    def save(self, *args, **kwargs):
        """saveをオーバーライド"""
        super(Reference, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.title)
    
    def reference_title(self):
        """タイトル"""
        return self.title
    
    def reference_citation_key(self):
        """引用キー"""
        return self.citation_key
    
    # 置き換え文字列と関数の対応
    VARIABLES = {'{{ citation_key }}': reference_citation_key,
                 '{{ title }}': reference_title}


# ToDo: migrateが完了したら削除
def yearly_score_validator(value):
    """IFやSNIPなど年ごとのスコアの書式検証"""
    lines = value.split('\r\n')
    for line in lines:
        if not re.match(r'^[0-9]+:[0-9.]+$', line):
            raise ValidationError(
                '2018:1.737 のように，年数とインパクトファクターをコロンで区切って，1行に1年分ずつ記入してください．',
                params={'line': line},
            )


def is_integer_num(n):
    """文字列が整数かどうか判定"""
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def score_json_validator(value):
    """{"年":値, ...} の型のjsonになっているかチェック"""
    try:
        score_dict = json.loads(value)  # jsonを読み込み
    except json.decoder.JSONDecodeError:
        raise ValidationError(
            '{"年":値, "年":値, ...} のJSON形式で値を記入してください．例) {"2018":1.737, "2019":2.000}',
            params={'value': value},
        )
    if not all([is_integer_num(k) for k in score_dict.keys()]):  # 整数でないキーがあれば
        raise ValidationError(
            '年が整数になっていません．'
            '{"年":値, "年":値, ...} のJSON形式で値を記入してください．例) {"2018":1.737, "2019":2.000}',
            params={'value': value},
        )
    if not all([type(v) is float for v in score_dict.values()]):  # floatでない値があれば
        raise ValidationError(
            '値が数値になっていません．'
            '{"年":値, "年":値, ...} のJSON形式で値を記入してください．例) {"2018":1.737, "2019":2.000}',
            params={'value': value},
        )


class JournalTitle(models.Model):
    """論文誌名クラス"""
    name = models.CharField('論文誌名', unique=True, max_length=400,
                            help_text='論文誌の名前を入力してください．(例: IEICE Transactions on Communications)')
    publisher = models.CharField('出版元', max_length=300,
                                 help_text='学会や出版社など，出版元を入力してください．(例: IEICE，IEEE，Elsevier)')
    impact_factor = models.TextField('IF', max_length=400,
                                     null=True,
                                     blank=True,
                                     validators=[score_json_validator, ],
                                     help_text='研究室メンバが著者にいる論文の場合は，{"年":値, "年":値, ...} のJSON形式でインパクトファクターが記録されます．'
                                               '例) {"2018":1.737, "2019":2.000}')
    cite_score = models.TextField('CiteScore', max_length=400,
                                  null=True,
                                  blank=True,
                                  validators=[score_json_validator, ],
                                  help_text='研究室メンバが著者にいる論文の場合は，{"年":値, "年":値, ...} のJSON形式でCiteScoreが記録されます．'
                                            '例) {"2018":1.737, "2019":2.000}')
    highest_percentile = models.TextField('Highest percentile', max_length=400,
                                          null=True,
                                          blank=True,
                                          validators=[score_json_validator, ],
                                          help_text='研究室メンバが著者にいる論文の場合は，{"年":"パーセンタイル, 順位/母数, '
                                                    '分野", "年":"パーセンタイル, 順位/母数, 分野", ...} のJSON形式で'
                                                    'ScopusのHighest percentileが記録されます．'
                                                    '例) {"2018":"90.0%, 19/204, General Computer Science", ...}')
    snip = models.TextField('SNIP', max_length=400,
                            null=True,
                            blank=True,
                            validators=[score_json_validator, ],
                            help_text='研究室メンバが著者にいる論文の場合は，{"年":値, "年":値, ...} のJSON形式でSNIPが記録されます．'
                                      '例) {"2018":1.737, "2019":2.000}')
    
    def __str__(self):
        return str(self.name)


def author_year_key(author, year, obj_id):
    """著者と年からcitation_keyを生成"""
    first_author = author.split('\n')[0]
    first_author = first_author.replace('\r', '')
    if is_japanese(first_author):  # 日本語
        if is_all_katakana(first_author):  # カタカナ名 => 外国人
            key_name = first_author.split(' ')[-1]
        else:  # 日本人
            key_name = first_author.split(' ')[0]
    else:
        key_name = first_author.split(' ')[-1]
    name_year = escape_char2ascii(key_name + str(year))  # 名前と年を組み合わせてascii化
    citation_key = name_year
    for x in string.ascii_lowercase:
        same_keys = Reference.objects.filter(citation_key=citation_key)  # 同じcitation_keyのデータ
        same_keys = same_keys.exclude(pk=obj_id)  # 自分自身を除外
        if len(same_keys) == 0:
            break  # 割当可能なキーが見つかれば終了
        citation_key = name_year + x  # 同じものがあった場合はアルファベットを添える
    else:  # citation_keyがなければ
        citation_key = name_year + '_' + str(obj_id)
    return citation_key


class JournalPaper(Reference):
    """論文誌クラス"""
    author = models.TextField('著者', max_length=300,
                              help_text='著者を1行に1人ずつ，姓と名の間に半角スペースを入れて記入してください．'
                                        '必要に応じて以下の拡張文字を使用してください\n'
                                        'áćéǵíḱĺḿńóṕŕśúẃýź ÁĆÉǴÍḰĹḾŃÓṔŔŚÚẂÝŹ őűŐŰ '
                                        'àèìǹòùẁỳÀÈÌǸÒÙẀỲ ăĕğĭŏŭĂĔĞĬŎŬ ǎčěǧȟǩňǒřšǔžǍČĎĚǦȞǨǏŇǑŘŠŤǓŽ\n'
                                        'çḑȩḩķļņŗşţÇḐȨĢḨĶĻŅŖŞŢ âĉêĝĥîĵôŝûŵŷẑÂĈÊĜĤÎĴÔŜÛŴŶẐ '
                                        'äëḧïöüẅẍÿÄËḦÏÖÜẄẌŸ ãẽĩñõũṽỹÃẼĨÑÕŨṼỸ\n'
                                        'ȧḃċḋėḟġḣṁṅȯṗṙṡṫẇẋẏżȦḂĊḊĖḞĠḢİṀṄȮṖṘṠṪẆẊẎŻ '
                                        'ạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒ\n'
                                        'āēḡīōūȳĀĒḠĪŌŪȲ ḇḏḵḻṉṟṯẕḆḎḴḺṈṞṮẔ åÅůŮ ßÆæŒœŁłØøĐđĐðŊŋÞþ', )
    journal_title = models.ForeignKey(
        JournalTitle,
        related_name='journal_title',
        on_delete=models.CASCADE,
        verbose_name='論文誌名',
        help_text='論文誌名を入力してください．一覧になければ，新しく登録してください．'
    )
    volume = models.CharField('vol.', blank=True, max_length=10)
    number = models.CharField('no.', blank=True, max_length=10)
    year = models.IntegerField('出版年', null=True,
                               validators=[MinValueValidator(1900, message='1900年より前の年は入力できません．'),
                                           MaxValueValidator(2100, message='2100年より先の年は入力できません．')],
                               help_text='出版された年を入力してください．'
                               )
    month = models.IntegerField(
        verbose_name='出版月',
        blank=True,
        null=True,
        default=None,
        choices=MONTH_CHOICE,
        help_text='出版された月を入力してください．'
    )
    page_regex = RegexValidator(
        regex=r'^[0-9]+-[0-9]+$|^[0-9]*$',
        message="開始ページ-終了ページ の形式で記入してください (例: 32-41)．"
    )
    page = models.CharField('ページ数', blank=True, max_length=20,
                            help_text='ページ数を入力してください(例: 32-41)．', validators=[page_regex])
    
    def assign_citation_key(self):
        """citation_keyを自動設定"""
        citation_key = author_year_key(self.author, self.year, self.id)
        print(citation_key)
        self.citation_key = citation_key  # 引用キーを自動入力
        self.save()  # データを更新
    
    def comma_author(self):
        """カンマで区切られた著者の文字列を返す"""
        value = self.author.replace('\r\n', ', ')
        value = value.replace('\n', ', ')
        value = value.replace('\r', ', ')
        return value
    
    def and_author(self):
        """andで区切られた著者の文字列を返す"""
        value = self.author.replace('\r\n', ' and ')
        value = value.replace('\n', ' and ')
        value = value.replace('\r', ' and ')
        return value
    
    def formed_authors(self):
        """カンマで区切られ，英語の場合は最後の著者の前にandを付した著者の文字列を返す"""
        value = self.author.replace('\r\n', ', ')
        value = value.replace('\n', ', ')
        value = value.replace('\r', ', ')
        if not is_japanese(self.author):  # 英語の場合
            if value.count(',') == 1:
                value = value.replace(', ', ' and ')  # 著者が2人ならカンマなし
            else:
                value = re.sub(r', ([^,]+)$', r', and \1', value)  # 著者が3人以上ならカンマあり
        return value
    
    def source_text(self):
        """巻号などを含む引用などで一般的に使われるフォーマットのテキストを返す"""
        page_text = ''
        if self.page != '':
            if '-' in self.page:  # 複数ページの場合
                page_text = ', pp. %s' % self.page
            else:  # 単ページの場合
                page_text = ', p. %s' % self.page
        volume_text = ''
        if self.volume != '':
            volume_text = ', vol. %s' % self.volume
        number_text = ''
        if self.number != '':
            number_text = ', no. %s' % self.number
        source_text = '%s%s%s%s' % (self.journal_title.name, volume_text, number_text, page_text)
        return source_text
    
    def authors(self):
        """カンマ区切りの著者"""
        return self.comma_author()
    
    def and_separated_authors(self):
        """and 区切りの著者"""
        return self.and_author()
    
    def formed_author(self):
        """カンマ区切り，英語の場合は最後の著者の前に andを付加した著者"""
        return self.formed_authors()
    
    def journal_name(self):
        """論文誌名"""
        return self.journal_title.name
    
    def publisher(self):
        """出版機関名"""
        return str(self.journal_title.publisher)
    
    def journal_volume(self):
        """Volume (巻)"""
        return self.volume
    
    def formed_journal_volume(self):
        """Vol.とカンマを付けたVolume (巻)"""
        value = self.volume
        if value is None or value == '':
            return ''
        value = 'vol.' + value + ', '
        return value
    
    def journal_number(self):
        """Number (号，Issue)"""
        return self.number
    
    def formed_journal_number(self):
        """No.とカンマを付けたNumber (号，Issue)"""
        value = self.number
        if value is None or value == '':
            return ''
        value = 'no.' + value + ', '
        return value
    
    def first_page_bar(self):
        """最初のページ(情報がなければハイフン)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[0])
        elif page_list[0] == '':  # ページなし
            value = '-'
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def last_page_bar(self):
        """最後のページ(情報がなければハイフン)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[1])
        elif page_list[0] == '':  # ページなし
            value = '-'
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def first_page(self):
        """最初のページ(情報がなければ空欄)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[0])
        elif page_list[0] == '':  # ページなし
            value = ''
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def last_page(self):
        """最後のページ(情報がなければ空欄)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[1])
        elif page_list[0] == '':  # ページなし
            value = ''
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def pages(self):
        """ハイフン1つで区切られたページ数(単一ページの場合はハイフンなし) (例: 24-35，27)"""
        return self.page.replace('-', '--')
    
    def double_hyphen_pages(self):
        """ハイフン2つで区切られたページ数(単一ページの場合はハイフンなし) (例: 24--35，27)"""
        return self.page.replace('-', '--')
    
    def formed_double_hyphen_pages(self):
        """pp.またはp.とカンマを付けたハイフン2つで区切られたページ数(単一ページの場合はハイフンなし) (例: pp.24--35, ，p.27, )"""
        pages = self.double_hyphen_pages()
        if pages is None or pages == '':
            return ''
        if '-' in pages:
            pages = 'pp.' + pages + ', '
        else:
            pages = 'p.' + pages + ', '
        return pages
    
    def journal_year(self):
        """発表年"""
        return str(self.year)
    
    # 置き換え文字列と関数の対応
    VARIABLES = dict(Reference.VARIABLES, **{
        '{{ authors }}': authors,
        '{{ and_separated_authors }}': and_separated_authors,
        '{{ formed_authors }}': formed_authors,
        '{{ journal_name }}': journal_name,
        '{{ publisher }}': publisher,
        '{{ volume }}': journal_volume,
        '{{ formed_volume }}': formed_journal_volume,
        '{{ number }}': journal_number,
        '{{ formed_number }}': formed_journal_number,
        '{{ first_page_bar }}': first_page_bar,
        '{{ last_page_bar }}': last_page_bar,
        '{{ first_page }}': first_page,
        '{{ last_page }}': last_page,
        '{{ pages }}': pages,
        '{{ double_hyphen_pages }}': double_hyphen_pages,
        '{{ formed_double_hyphen_pages }}': formed_double_hyphen_pages,
        '{{ year }}': journal_year,
    })


def kenkyukai_validator(value):
    """研究会のフォーマットを検証"""
    if '研究会' in value:
        if not re.match(r'電子情報通信学会 .*研究会, 信学技報, vol. [0-9]*, no. [0-9]*', value) and '横断型' not in value:
            raise ValidationError('研究会は "電子情報通信学会 情報ネットワーク研究会, 信学技報, vol. 109, no. 119" のようにvolとnoを付記してください．')


class ConferenceTitle(models.Model):
    """会議名クラス"""
    name = models.CharField('会議名', unique=True, max_length=400,
                            validators=[kenkyukai_validator, ],
                            help_text='会議名を記入してください．研究会では下記の例のように，信学技報のvolとnoを付記してください．'
                                      '会議名は正式名称で，国際会議は()で略称を記入してください．'
                                      'Workshop, Poster, Mini-conferenceなどは本会議とは分けて登録してください．\n'
                                      'The 31st IEEE International Conference '
                                      'on Computer Communication (INFOCOM 2012)\n'
                                      'The 15th Annual International Conference '
                                      'on Mobile Computing and Networking (MobiCom 2009) Workshop\n'
                                      '2003 IEEE International Conference on Communications (ICC 2003)\n'
                                      '電子情報通信学会 情報ネットワーク研究会, 信学技報, vol. 109, no. 119\n'
                                      '2015年 電子情報通信学会 信越支部大会\n')
    year = models.IntegerField('開催年',
                               validators=[MinValueValidator(1900, message='1900年より前の年は入力できません．'),
                                           MaxValueValidator(2100, message='2100年より先の年は入力できません．')],
                               help_text='開催された年を入力してください．'
                               )
    month = models.IntegerField(
        verbose_name='開催月',
        blank=True,
        null=True,
        default=None,
        choices=MONTH_CHOICE,
        help_text='開催された月を入力してください．'
    )
    venue = models.CharField('開催都市', max_length=100, blank=True,
                             help_text='開催都市を入力してください(例1: Kyoto，例2: Miami，例3: Shanghai，例4: 神奈川)．')
    country = models.CharField('開催国', max_length=100, blank=True,
                               help_text='開催国(米国，カナダ等の場合は州の略号と開催国)を入力してください(例1: Japan，例2: 日本, 例3: FL, USA，例4: China)．')
    organizer = models.CharField('主催者', null=True, blank=True, max_length=400,
                                 help_text='会議の主催者を入力してください(例: IEEE，ACM，IFIP，IEICE，電子情報通信学会)．')
    cite_score = models.FloatField('CiteScore', max_length=400,
                                   null=True,
                                   blank=True,
                                   help_text='研究室メンバが著者にいる論文でCiteScoreが記録されている会議の場合は，この年の会議のCiteScoreが記録されます．')
    highest_percentile = models.CharField('Highest percentile', null=True, blank=True, max_length=200,
                                          help_text='研究室メンバが著者にいる論文でHighest percentileが記録されている会議の場合は，'
                                                    'この年の会議のHighest percentileが記録されます．')
    snip = models.FloatField('SNIP', max_length=400,
                             null=True,
                             blank=True,
                             help_text='研究室メンバが著者にいる論文でSNIPが記録されている会議の場合は，この年の会議のSNIPが記録されます．')
    acceptance_ratio = models.FloatField('採択率', max_length=400,
                                         null=True,
                                         blank=True,
                                         help_text='研究室メンバが著者にいる論文で採択率が公開されている場合は，この年の会議の採択率を記入してください．')
    
    def __str__(self):
        return str(self.name)


class ConferencePaper(Reference):
    """会議クラス"""
    author = models.TextField('著者', max_length=300,
                              help_text='著者を1行に1人ずつ，姓と名の間に半角スペースを入れて記入してください．'
                                        '必要に応じて以下の拡張文字を使用してください\n'
                                        'áćéǵíḱĺḿńóṕŕśúẃýź ÁĆÉǴÍḰĹḾŃÓṔŔŚÚẂÝŹ őűŐŰ '
                                        'àèìǹòùẁỳÀÈÌǸÒÙẀỲ ăĕğĭŏŭĂĔĞĬŎŬ ǎčěǧȟǩňǒřšǔžǍČĎĚǦȞǨǏŇǑŘŠŤǓŽ\n'
                                        'çḑȩḩķļņŗşţÇḐȨĢḨĶĻŅŖŞŢ âĉêĝĥîĵôŝûŵŷẑÂĈÊĜĤÎĴÔŜÛŴŶẐ '
                                        'äëḧïöüẅẍÿÄËḦÏÖÜẄẌŸ ãẽĩñõũṽỹÃẼĨÑÕŨṼỸ\n'
                                        'ȧḃċḋėḟġḣṁṅȯṗṙṡṫẇẋẏżȦḂĊḊĖḞĠḢİṀṄȮṖṘṠṪẆẊẎŻ '
                                        'ạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒ\n'
                                        'āēḡīōūȳĀĒḠĪŌŪȲ ḇḏḵḻṉṟṯẕḆḎḴḺṈṞṮẔ åÅůŮ ßÆæŒœŁłØøĐđĐðŊŋÞþ')
    conference_title = models.ForeignKey(
        ConferenceTitle,
        related_name='conference_title',
        on_delete=models.CASCADE,
        verbose_name='会議名',
        help_text='会議名を入力してください．一覧になければ，新しく登録してください．必要に応じて Poster，Poster Track，Mini-conferenceなどを付記してください．'
    )
    presentation_id = models.CharField('発表ID', max_length=20,
                                       blank=True,
                                       null=True,
                                       help_text='研究会，および総合大会，ソサイエティ大会，信越支部大会等の場合は発表IDを入力してください'
                                                 '(例1: NS2017-198，例2: IN2018-131，例3: B-7-23，例4: 3D-1)．')
    page_regex = RegexValidator(
        regex=r'^[0-9]+-[0-9]+$|^[0-9]*$',
        message="開始ページ-終了ページ の形式で記入してください (例: 32-41)．"
                "1ページの原稿の場合はハイフンは不要です(例: 56)．"
    )
    page = models.CharField('ページ数', blank=True, max_length=20, help_text='ページ数を入力してください(例1: 32-41，例2: 56)．',
                            validators=[page_regex])
    
    def assign_citation_key(self):
        """citation_keyを自動設定"""
        citation_key = author_year_key(self.author, self.conference_title.year, self.id)
        print(citation_key)
        self.citation_key = citation_key  # 引用キーを自動入力
        self.save()  # データを更新
    
    def comma_author(self):
        """カンマで区切られた著者の文字列を返す"""
        value = self.author.replace('\r\n', ', ')
        value = value.replace('\n', ', ')
        value = value.replace('\r', ', ')
        return value
    
    def and_author(self):
        """and で区切られた著者の文字列を返す"""
        value = self.author.replace('\r\n', ' and ')
        value = value.replace('\n', ' and ')
        value = value.replace('\r', ' and ')
        return value
    
    def formed_authors(self):
        """カンマで区切られ，最後の著者の前にandを付した著者の文字列を返す"""
        value = self.author.replace('\r\n', ', ')
        value = value.replace('\n', ', ')
        value = value.replace('\r', ', ')
        if not is_japanese(self.author):  # 英語の場合
            if value.count(',') == 1:
                value = value.replace(', ', ' and ')  # 著者が2人ならカンマなし
            else:
                value = re.sub(r', ([^,]+)$', r', and \1', value)  # 著者が3人以上ならカンマあり
        return value
    
    def source_text(self):
        """巻号などを含む引用などで一般的に使われるフォーマットのテキストを返す"""
        page_text = ''
        if self.page != '':
            if '-' in self.page:  # 複数ページの場合
                page_text = ', pp. %s' % self.page
            else:  # 単ページの場合
                page_text = ', p. %s' % self.page
        presentation_id_text = ''
        if self.presentation_id is not None and self.presentation_id != '':
            presentation_id_text = ', %s' % self.presentation_id
        venue_text = ''
        if self.conference_title.venue != '':
            venue_text = ', %s' % self.conference_title.venue
        country_text = ''
        if self.conference_title.country != '' and self.conference_title.country != '日本':
            country_text = ', %s' % self.conference_title.country
        source_text = '%s%s%s%s%s ' % (self.conference_title.name,
                                        presentation_id_text,
                                        venue_text,
                                        country_text,
                                        page_text)
        return source_text
    
    def conference_authors(self):
        """カンマ区切りの著者"""
        return self.comma_author()
    
    def conference_and_separated_authors(self):
        """and 区切りの著者"""
        return self.and_author()
    
    def conference_formed_authors(self):
        """カンマ区切り，英語の場合は最後の著者の前に andを付加した著者"""
        return self.formed_authors()
    
    def conference_name(self):
        """会議名"""
        return self.conference_title.name
    
    def uncapitalized_conference_name(self):
        """最初の単語が前置詞なら小文字化した会議名"""
        words = self.conference_title.name.split(' ')  # 単語に分割
        if words[0].lower() in Reference.preposition:  # 最初が前置詞か確認
            return ' '.join([words[0].lower()] + words[1:])  # 前置詞なら小文字に
        return self.conference_title.name
    
    def venue(self):
        """開催都市"""
        return self.conference_title.venue
    
    def country(self):
        """開催国"""
        return self.conference_title.country
    
    def venue_country(self):
        """カンマで区切られた開催都市と開催国(日本の場合は国名は空欄)"""
        if self.conference_title.country == '日本' or self.conference_title.country == '':
            return self.conference_title.venue
        return self.conference_title.venue + ', ' + self.conference_title.country

    def formed_presentation_id(self):
        """カンマ付き発表ID(ない場合は空欄)"""
        if self.presentation_id != '' and self.presentation_id is not None:
            return self.presentation_id + ', '
        return ''

    def first_page_bar(self):
        """最初のページ(情報がなければハイフン)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[0])
        elif page_list[0] == '':  # ページなし
            value = '-'
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def last_page_bar(self):
        """最後のページ(情報がなければハイフン)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[1])
        elif page_list[0] == '':  # ページなし
            value = '-'
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def first_page(self):
        """最初のページ(情報がなければ空欄)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[0])
        elif page_list[0] == '':  # ページなし
            value = ''
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def last_page(self):
        """最後のページ(情報がなければ空欄)"""
        page_list = self.page.split('-')
        if len(page_list) > 1:  # 複数ページの場合
            value = str(page_list[1])
        elif page_list[0] == '':  # ページなし
            value = ''
        else:  # 単一ページ
            value = str(page_list[0])
        return value
    
    def pages(self):
        """ハイフン1つで区切られたページ数(単一ページの場合はハイフンなし) (例: 24-35，27)"""
        return self.page.replace('-', '--')
    
    def double_hyphen_pages(self):
        """ハイフン2つで区切られたページ数(単一ページの場合はハイフンなし) (例: 24--35，27)"""
        return self.page.replace('-', '--')
    
    def formed_double_hyphen_pages(self):
        """pp.またはp.とカンマを付けたハイフン2つで区切られたページ数(単一ページの場合はハイフンなし) (例: pp.24--35, ，p.27, )"""
        pages = self.double_hyphen_pages()
        if pages is None or pages == '':
            return ''
        if '-' in pages:
            pages = 'pp.' + pages + ', '
        else:
            pages = 'p.' + pages + ', '
        return pages
    
    def conference_year(self):
        """発表年"""
        return str(self.conference_title.year)
    
    def proceedings_of(self):
        """会議名が英語なら Proceedings of，それ以外ならなし．"""
        if is_japanese(self.conference_title.name):
            return ''
        return 'Proceedings of '
    
    def in_proceedings_of(self):
        """会議名が英語なら in Proceedings of，それ以外ならなし．"""
        if is_japanese(self.conference_title.name):
            return ''
        return 'in Proceedings of '
    
    # 置き換え文字列と関数の対応
    VARIABLES = dict(Reference.VARIABLES, **{
        '{{ authors }}': conference_authors,
        '{{ and_separated_authors }}': conference_and_separated_authors,
        '{{ formed_authors }}': conference_formed_authors,
        '{{ conference_name }}': conference_name,
        '{{ uncapitalized_conference_name }}': uncapitalized_conference_name,
        '{{ venue }}': venue,
        '{{ country }}': country,
        '{{ venue_country }}': venue_country,
        '{{ formed_presentation_id }}': formed_presentation_id,
        '{{ first_page_bar }}': first_page_bar,
        '{{ last_page_bar }}': last_page_bar,
        '{{ first_page }}': first_page,
        '{{ last_page }}': last_page,
        '{{ pages }}': pages,
        '{{ double_hyphen_pages }}': double_hyphen_pages,
        '{{ formed_double_hyphen_pages }}': formed_double_hyphen_pages,
        '{{ year }}': conference_year,
        '{{ proceedings_of }}': proceedings_of,
        '{{ in_proceedings_of }}': in_proceedings_of,
    })


class OurJournalPaper(JournalPaper):
    """研究室メンバが著者の論文誌クラス"""
    # ToDo: default_userをシリアライズ可能にして，defaultをdefault_userに変更．
    # default_user = User.objects.filter(username='kwatabe')  # デフォルトの研究室内著者
    author_user = models.ManyToManyField(User, verbose_name='研究室内著者',
                                         related_name='journal_users', default=None,
                                         help_text='研究室メンバのうち著者に含まれるメンバを登録してください．')
    letter = models.BooleanField('レター', default=False, help_text='レターの場合，チェックを入れてください．')
    invited = models.BooleanField('招待論文', default=False, help_text='招待論文の場合，チェックを入れてください．')
    published_date = models.DateField(default=None, verbose_name='出版年月日',
                                      help_text='出版年月日を入力してください．オンライン版が先に公開されている場合は，そちらの公開日を入力してください．')
    pdf_validator = FileExtensionValidator(
        ['pdf', ],
        message="PDFファイルを添付してださい．"
    )
    post_print = models.FileField(
        blank=True,
        upload_to=get_upload_to_post_print,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='Post-print(出版版ではなく査読後に投稿した際の原稿)のファイルを登録してください．'
    )
    pre_print = models.FileField(
        blank=True,
        upload_to=get_upload_to_pre_print,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='Pre-print(査読前の投稿時原稿)のファイルを登録してください．'
    )
    doi = models.CharField('DOI', max_length=30,
                           blank=True,
                           null=True,
                           help_text='DOIを入力してください．(例: 10.1109/TIT.2016.2636847)')
    url = models.URLField('URL', max_length=400,
                          blank=True,
                          null=True,
                          help_text='IEEE eXplore，ACM Digital Library，ScienceDirect など，'
                                    '公式のPDFが公開されているページのURLを入力してください．'
                                    '(例: https://ieeexplore.ieee.org/document/8526826，'
                                    '例: https://dl.acm.org/citation.cfm?id=2833277，)')
    fwci = models.FloatField('FWCI',
                             null=True,
                             blank=True,
                             default=None,
                             help_text='FWCIを表示します．')
    scopus_cite = models.IntegerField('Scopus引用数',
                                      null=True,
                                      blank=True,
                                      default=None,
                                      help_text='Scopusの引用数を表示します．')
    
    def pdf_publish(self):
        """PDFが公開可能か返す関数"""
        if self.pdf == '':
            return False
        if self.journal_title.publisher == 'IEICE':
            return True
        return False
    
    def post_print_publish(self):
        """post-printが公開可能か返す関数"""
        if self.post_print == '':
            return False
        if self.journal_title.publisher is None:
            return False
        if self.url is None:
            return False
        if self.doi is None:
            return False
        return True
    
    def pre_print_publish(self):
        """pre-printが公開可能か返す関数"""
        if self.pre_print == '':
            return False
        if self.journal_title.publisher is None:
            return False
        if self.url is None:
            return False
        if self.doi is None:
            return False
        return True
    
    def link_publish(self):
        """PDFをリンク先で公開されているか判定する関数"""
        if self.url == '' or self.url is None:
            return False
        if self.journal_title.publisher not in ['IFIP', 'WSEAS', 'Public Library of Science']:
            return False
        return True
    
    def update_url(self):
        """URLを更新"""
        url = None
        if self.journal_title.publisher == 'IEICE':
            if self.volume is None or self.number is None or self.first_page() == '':
                print('Warning: volume, number, or first_page of article is None. ')
            else:
                url = 'https://search.ieice.org/bin/summary.php?id={}_{}_{}'.format(self.volume.lower(),
                                                                                    self.number.lower(),
                                                                                    self.first_page())
        else:
            if self.doi is None or self.doi == '':
                print('Warning: DOI of article is None. ')
            else:
                url = 'https://www.doi.org/' + self.doi
        self.url = url
        self.save()
    
    def get_impact_factor(self):
        """出版年のインパクトファクターを取得"""
        published_year = self.published_date.year
        if self.journal_title.impact_factor is not None and self.journal_title.impact_factor != '':
            score_dict = json.loads(self.journal_title.impact_factor)
            if str(published_year) in score_dict.keys():
                return published_year, float(score_dict[str(published_year)])  # 年とスコアを返す
        return None, None  # なければNoneを返す
    
    def get_recent_impact_factor(self):
        """出版年以前の最も新しいインパクトファクターを取得"""
        published_year = self.published_date.year
        if self.journal_title.impact_factor is not None and self.journal_title.impact_factor != '':
            score_dict = json.loads(self.journal_title.impact_factor)
            for i in range(0, 10):
                if str(published_year - i) in score_dict.keys():
                    return published_year - i, float(score_dict[str(published_year - i)])  # 年とスコアを返す
        return None, None  # なければNoneを返す
    
    def get_cite_score(self):
        """出版年のCiteScoreを取得"""
        published_year = self.published_date.year
        if self.journal_title.cite_score is not None and self.journal_title.cite_score != '':
            score_dict = json.loads(self.journal_title.cite_score)
            if str(published_year) in score_dict.keys():
                return published_year, float(score_dict[str(published_year)])  # 年とスコアを返す
        return None, None  # なければNoneを返す

    def get_recent_cite_score(self):
        """出版年以前の最も新しいCiteScoreを取得"""
        published_year = self.published_date.year
        if self.journal_title.cite_score is not None and self.journal_title.cite_score != '':
            score_dict = json.loads(self.journal_title.cite_score)
            for i in range(0, 10):
                if str(published_year - i) in score_dict.keys():
                    return published_year - i, float(score_dict[str(published_year - i)])  # 年とスコアを返す
        return None, None  # なければNoneを返す
    
    def get_snip(self):
        """出版年のSNIPを取得"""
        published_year = self.published_date.year
        if self.journal_title.snip is not None and self.journal_title.snip != '':
            score_dict = json.loads(self.journal_title.snip)
            if str(published_year) in score_dict.keys():
                return published_year, float(score_dict[str(published_year)])  # 年とスコアを返す
        return None, None  # なければNoneを返す
    
    def get_recent_snip(self):
        """出版年以前の最も新しいSNIPを取得"""
        published_year = self.published_date.year
        if self.journal_title.snip is not None and self.journal_title.snip != '':
            score_dict = json.loads(self.journal_title.snip)
            for i in range(0, 10):
                if str(published_year - i) in score_dict.keys():
                    return published_year - i, float(score_dict[str(published_year - i)])  # 年とスコアを返す
        return None, None  # なければNoneを返す
    
    def invited_1_or_2(self):
        """招待講演ならば1，そうでなければ2"""
        if self.invited:
            value = '1'
        else:
            value = '2'
        return value
    
    def eng_01_or_jap_02(self):
        """英語なら01，日本語なら02"""
        if is_japanese(self.journal_title.name):
            value = '02'
        else:
            value = '01'
        return value
    
    def impact_factor(self):
        """出版年のインパクトファクター (情報がない場合はハイフンを表示)"""
        _, impact_factor = self.get_impact_factor()
        if impact_factor is None:
            return '-'
        else:
            return '{0:.3f}'.format(impact_factor)
    
    def recent_impact_factor(self):
        """出版年以前の最も新しいインパクトファクター (情報がない場合はハイフンを表示)"""
        year, impact_factor = self.get_recent_impact_factor()
        if impact_factor is None:
            return '-'
        else:
            return '{0:.3f} ({1})'.format(impact_factor, str(year))

    def cite_score(self):
        """出版年のCiteScore (情報がない場合はハイフンを表示)"""
        _, cite_score = self.get_cite_score()
        if cite_score is None:
            return '-'
        else:
            return '{0:.3f}'.format(cite_score)
    
    def recent_cite_score(self):
        """出版年以前の最も新しいCiteScore (情報がない場合はハイフンを表示)"""
        year, cite_score = self.get_recent_cite_score()
        if cite_score is None:
            return '-'
        else:
            return '{0:.3f} ({1})'.format(cite_score, str(year))
    
    def snip(self):
        """出版年のSNIP (情報がない場合はハイフンを表示)"""
        _, snip = self.get_snip()
        if snip is None:
            return '-'
        else:
            return '{0:.3f}'.format(snip)
    
    def recent_snip(self):
        """出版年以前の最も新しいSNIP (情報がない場合はハイフンを表示)"""
        year, snip = self.get_recent_snip()
        if snip is None:
            return '-'
        else:
            return '{0:.3f} ({1})'.format(snip, str(year))
    
    def journal_fwci(self):
        """論文のFWCI (情報がない場合はハイフンを表示)"""
        if self.fwci is None:
            return '-'
        else:
            fwci = self.fwci
        return '{0:.2f}'.format(fwci)
    
    def journal_scopus_cite(self):
        """Scopusにおける引用数 (情報がない場合はハイフンを表示)"""
        if self.scopus_cite is None:
            return '-'
        else:
            return str(self.scopus_cite)
    
    def business_year(self):
        """発表年度"""
        value = self.published_date.year
        if self.published_date.month <= 3:
            value -= 1
        return str(value)
    
    def month(self):
        """発表月"""
        return str(self.published_date.month)
    
    def zero_month(self):
        """0詰めの発表月 (例: 01，02，...)"""
        return str(self.published_date.strftime('%m'))
    
    def day(self):
        """発表日"""
        return str(self.published_date.day)
    
    def zero_day(self):
        """0詰めの発表日 (例: 01，02，...)"""
        return str(self.published_date.strftime('%d'))
    
    def journal_doi(self):
        """DOI"""
        if self.doi is None:
            return ''
        return self.doi
    
    # 置き換え文字列と関数の対応
    VARIABLES = dict(JournalPaper.VARIABLES, **{
        '{{ invited_1_or_2 }}': invited_1_or_2,
        '{{ eng_01_or_jap_02 }}': eng_01_or_jap_02,
        '{{ impact_factor }}': impact_factor,
        '{{ recent_impact_factor }}': recent_impact_factor,
        '{{ cite_score }}': cite_score,
        '{{ recent_cite_score }}': recent_cite_score,
        '{{ snip }}': snip,
        '{{ recent_snip }}': recent_snip,
        '{{ fwci }}': journal_fwci,
        '{{ business_year }}': business_year,
        '{{ scopus_cite }}': journal_scopus_cite,
        '{{ month }}': month,
        '{{ zero_month }}': zero_month,
        '{{ day }}': day,
        '{{ zero_day }}': zero_day,
        '{{ doi }}': journal_doi,
    })


class OurConferencePaper(ConferencePaper):
    """研究室メンバが著者の会議クラス"""
    presenter = models.CharField('発表者', max_length=20,
                                 help_text='発表者を入力してください．')
    # ToDo: default_userをシリアライズ可能にして，defaultをdefault_userに変更．
    # default_user = User.objects.filter(username='kwatabe')  # デフォルトの研究室内著者
    author_user = models.ManyToManyField(User, verbose_name='研究室内著者',
                                         related_name='conference_users', default=None,
                                         help_text='研究室メンバのうち著者に含まれるメンバを登録してください．')
    short_paper = models.BooleanField('ショートペーパー', default=False, help_text='ショートペーパーの場合，チェックを入れてください．')
    poster = models.BooleanField('ポスター発表', default=False, help_text='ポスター発表の場合，チェックを入れてください．')
    invited = models.BooleanField('招待講演', default=False, help_text='招待講演の場合，チェックを入れてください．')
    keynote = models.BooleanField('基調講演', default=False, help_text='基調講演の場合，チェックを入れてください．')
    published_date = models.DateField(default=None, verbose_name='公開年月日',
                                      help_text='発表した会議が開会した日付を入力してください．')
    pdf_validator = FileExtensionValidator(
        ['pdf', ],
        message="PDFファイルを添付してださい．"
    )
    post_print = models.FileField(
        blank=True,
        upload_to=get_upload_to_post_print,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='国際会議の場合は，Post-print(出版版ではなく査読後の投稿時原稿)のファイルを登録してください．'
    )
    pre_print = models.FileField(
        blank=True,
        upload_to=get_upload_to_pre_print,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='国際会議の場合は，Pre-print(査読前の投稿時原稿)のファイルを登録してください．'
    )
    presentation_pdf = models.FileField(
        blank=True,
        upload_to=get_upload_to_presentation_pdf,
        verbose_name='添付ファイル',
        validators=[pdf_validator, ],
        help_text='プレゼンテーションまたはポスターのPDFファイルを登録してください．'
    )
    subject = models.ManyToManyField(Research, verbose_name='関連テーマ',
                                     related_name='conference_subject',
                                     default=None,
                                     blank=True,
                                     help_text='関連する研究テーマを登録してください．')
    doi = models.CharField('DOI', max_length=30,
                           blank=True,
                           null=True,
                           help_text='論文誌及び国際会議の場合は，DOIを入力してください．(例: 10.1109/TIT.2016.2636847)')
    url = models.URLField('URL', max_length=400,
                          blank=True,
                          null=True,
                          help_text='IEEE eXplore，ACM Digital Library，ScienceDirect など，'
                                    '公式のPDFが公開されているページのURLを入力してください．'
                                    '(例: https://ieeexplore.ieee.org/document/8526826，'
                                    '例: https://dl.acm.org/citation.cfm?id=2833277，)')
    fwci = models.FloatField('FWCI',
                             null=True,
                             blank=True,
                             default=None,
                             help_text='FWCIを表示します．')
    scopus_cite = models.IntegerField('Scopus引用数',
                                      null=True,
                                      blank=True,
                                      default=None,
                                      help_text='Scopusの引用数を表示します．')
    core_rank = models.CharField('CORE Rank', max_length=3,
                                 null = True,
                                 blank = True,
                                 default = None,
                                 help_text='に掲載されている国際会議の場合は，CORE Rankを記入してください．(例: A*，C)')
    
    def pdf_publish(self):
        """PDFが公開可能か返す関数"""
        return False
    
    def post_print_publish(self):
        """post-printが公開可能か返す関数"""
        if self.post_print == '':
            return False
        if self.conference_title.organizer is None:
            return False
        if self.url is None:
            return False
        if self.doi is None:
            return False
        return True
    
    def pre_print_publish(self):
        """pre-printが公開可能か返す関数"""
        if self.pre_print == '':
            return False
        if self.conference_title.organizer is None:
            return False
        if self.url is None:
            return False
        if self.doi is None:
            return False
        return True

    def link_publish(self):
        """PDFをリンク先で公開されているか判定する関数"""
        if self.url == '' or self.url is None:
            return False
        if self.conference_title.organizer not in ['IFIP', 'WSEAS'] and 'ITC' not in self.conference_title.name:
            return False
        if 'WMNC' in self.conference_title.name:
            return False
        return True
    
    def update_url(self):
        """URLを更新"""
        pass
    
    def invited_1_or_2(self):
        """招待講演ならば1，そうでなければ2"""
        if self.invited:
            value = '1'
        else:
            value = '2'
        return value
    
    def keynote_1_or_invited_2_or_3(self):
        """基調講演なら1，招待講演なら2，どちらでもなければ3"""
        if self.keynote:
            value = '1'
        elif self.invited:
            value = '2'
        else:
            value = '3'
        return value
    
    def invited_2_or_keynote_3_or_poster_4_or_1(self):
        """招待講演なら2，基調講演なら3，ポスターなら4，どれでもなければ1"""
        if self.keynote:
            value = '3'
        elif self.invited:
            value = '2'
        elif self.poster:
            value = '4'
        else:
            value = '1'
        return value
    
    def domestic_1_or_international_2(self):
        """国内会議なら1，国際会議なら2"""
        if is_japanese(self.conference_title.name):
            value = '1'
        else:
            value = '2'
        return value
    
    def presenter_name(self):
        """発表者"""
        return self.presenter
    
    def cite_score(self):
        """会議のCiteScore (情報がない場合はハイフンを表示)"""
        if self.conference_title.cite_score is None:
            return '-'
        else:
            cite_score = self.conference_title.cite_score
        return '{0:.3f}'.format(cite_score)
    
    def snip(self):
        """会議のSNIP (情報がない場合はハイフンを表示)"""
        if self.conference_title.snip is None:
            return '-'
        else:
            snip = self.conference_title.snip
        return '{0:.3f}'.format(snip)
    
    def conference_fwci(self):
        """論文のFWCI (情報がない場合はハイフンを表示)"""
        if self.fwci is None:
            return '-'
        else:
            fwci = self.fwci
        return '{0:.2f}'.format(fwci)
    
    def conference_scopus_cite(self):
        """Scopusにおける引用数 (情報がない場合はハイフンを表示)"""
        if self.scopus_cite is None:
            return '-'
        else:
            return str(self.scopus_cite)
    
    def conference_core_rank(self):
        """CORE Rank (情報がない場合はハイフンを表示)"""
        if self.core_rank is None:
            return '-'
        else:
            return self.core_rank
    
    def acceptance_ratio(self):
        """会議の採択率 (情報がない場合はハイフンを表示)"""
        if self.conference_title.acceptance_ratio is None:
            return '-'
        else:
            acceptance_ratio = self.conference_title.acceptance_ratio
        return '{0:.3f}'.format(acceptance_ratio)
    
    def acceptance_ratio_percent(self):
        """パーセント表示の会議の採択率 (情報がない場合はハイフンを表示)"""
        if self.conference_title.acceptance_ratio is None:
            return '-'
        else:
            acceptance_ratio = self.conference_title.acceptance_ratio
        return '{0:.1f}'.format(acceptance_ratio * 100)
    
    def business_year(self):
        """発表年度"""
        value = self.published_date.year
        if self.published_date.month <= 3:
            value -= 1
        return str(value)
    
    def month(self):
        """発表月"""
        return str(self.published_date.month)
    
    def zero_month(self):
        """0詰めの発表月 (例: 01，02，...)"""
        return str(self.published_date.strftime('%m'))
    
    def day(self):
        """発表日"""
        return str(self.published_date.day)
    
    def zero_day(self):
        """0詰めの発表日 (例: 01，02，...)"""
        return str(self.published_date.strftime('%d'))
    
    def org(self):
        """主催者"""
        return str(self.conference_title.organizer)
    
    def conference_doi(self):
        """DOI"""
        if self.doi is None:
            return ''
        return self.doi
    
    # 置き換え文字列と関数の対応
    VARIABLES = dict(ConferencePaper.VARIABLES, **{'{{ invited_1_or_2 }}': invited_1_or_2,
                                                   '{{ keynote_1_or_invited_2_or_3 }}': keynote_1_or_invited_2_or_3,
                                                   '{{ domestic_1_or_international_2 }}': domestic_1_or_international_2,
                                                   '{{ invited_2_or_keynote_3_or_poster_4_or_1 }}':
                                                       invited_2_or_keynote_3_or_poster_4_or_1,
                                                   '{{ presenter_name }}': presenter_name,
                                                   '{{ cite_score }}': cite_score,
                                                   '{{ snip }}': snip,
                                                   '{{ fwci }}': conference_fwci,
                                                   '{{ scopus_cite }}': conference_scopus_cite,
                                                   '{{ core_rank }}': conference_core_rank,
                                                   '{{ acceptance_ratio }}': acceptance_ratio,
                                                   '{{ acceptance_ratio_percent }}': acceptance_ratio_percent,
                                                   '{{ business_year }}': business_year,
                                                   '{{ month }}': month,
                                                   '{{ zero_month }}': zero_month,
                                                   '{{ day }}': day,
                                                   '{{ zero_day }}': zero_day,
                                                   '{{ org }}': org,
                                                   '{{ doi }}': conference_doi,
                                                   })


class UrlReference(Reference):
    """URLのクラス"""
    url = models.URLField('URL', max_length=400,
                          help_text='引用するサイトのURLを入力してください．')
    
    def url_str(self):
        """引用するサイトのURL"""
        return self.url
    
    # 置き換え文字列と関数の対応
    VARIABLES = dict(Reference.VARIABLES, **{'{{ url }}': url_str, })
