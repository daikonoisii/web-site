from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.conf import settings
from io import BytesIO
import qrcode
import re
import os


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, first_name_eng, last_name_eng, password, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')
        if not first_name_eng:
            raise ValueError('Users must have an first_name_eng')
        if not last_name_eng:
            raise ValueError('Users must have an last_name_eng')

        user = self.model(
            username=username,
            first_name_eng=first_name_eng,
            last_name_eng=last_name_eng,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, first_name_eng, last_name_eng, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            username,
            first_name_eng, last_name_eng,
            password,
            **extra_fields
        )

    def create_superuser(self, username, first_name_eng, last_name_eng, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            username,
            first_name_eng, last_name_eng,
            password,
            ** extra_fields
        )


def get_upload_to(instance, filename):
    """ファイルのアップロード先を定義"""
    # filename = re.sub(r'[\\/:?."<>| ]', '_', filename)  # ファイル名に使えない文字を置き換え
    extension = os.path.splitext(filename)[-1]
    filename = instance.username + extension
    return os.path.join('users/', filename)


def get_qr_upload_to(instance, filename):
    """QRコードのアップロード先を定義"""
    if not os.path.exists(settings.MEDIA_ROOT + '/market'):
        os.makedirs(settings.MEDIA_ROOT + '/market')  # ディレクトリがなければ作成
    if instance.pk is None:
        pk = User.objects.all().order_by("-id")[0].pk + 1
        return os.path.join('market/', str(pk) + '_qr_' + filename)
    else:
        return os.path.join('market/', str(instance.pk) + '_qr_' + filename)


class User(AbstractBaseUser, PermissionsMixin):
    username_regex = RegexValidator(
        regex=r'[A-Za-z0-9_]{1,15}',
        message="半角英数字とアンダースコアで入力してください．（3文字以上，15文字以内）"
    )
    username = models.CharField(
        verbose_name='ユーザID',
        max_length=30,
        unique=True,
        validators=[username_regex]
    )
    
    email = models.EmailField(
        verbose_name='メールアドレス',
        blank=True,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        default='',
        upload_to=get_upload_to,
        verbose_name='画像ファイル',
        help_text='プロフィール写真のファイルを登録してください．'
    )
    
    name_regex = RegexValidator(
        regex=r'^[^\x21-\x7E]+$',
        message="全角文字と半角スペースで入力してください．"
    )
    first_name = models.CharField(
        verbose_name='名',
        max_length=30,
        blank=True,
        validators=[name_regex],
        help_text = "名前を日本語で入力してください．留学生の場合は，アルファベットではなく，カタカナを使ってください．ミドルネームがある場合は，ここには記載しないでください．"
    )
    last_name = models.CharField(
        verbose_name='姓',
        max_length=150,
        blank=True,
        validators=[name_regex],
        help_text = "名字を日本語で入力してください．留学生の場合は，アルファベットではなく，カタカナを使ってください．ミドルネームがある場合は，半角スペースで区切ってここに記載してください．"
    )

    name_kana_regex = RegexValidator(
        regex=r'^[\u30A1-\u30F6 ー]+$',
        message="姓名(フリガナ)は，全角カタカナと半角スペースで入力してください．"
    )
    first_name_kana = models.CharField(
        verbose_name='名(フリガナ)',
        max_length=30,
        validators=[name_kana_regex],
        blank=True,
        help_text='全角カタカナと半角スペースで入力してください．'
    )
    last_name_kana = models.CharField(
        verbose_name='姓(フリガナ)',
        validators=[name_kana_regex],
        max_length=150,
        blank=True,
        help_text='全角カタカナと半角スペースで入力してください．'
    )

    name_eng_regex = RegexValidator(
        regex=r'^[A-Z][a-z]+([ \-A-Za-z]*)$',
        message="姓名(英語)は，半角英字と半角スペース，ハイフンで，最初の文字を大文字にして入力してください．"
    )
    first_name_eng = models.CharField(
        verbose_name='名(英語)',
        validators=[name_eng_regex],
        max_length=30,
        # blank=True,
        help_text='半角英字と半角スペースで，最初の文字を大文字にして入力してください．'
    )
    last_name_eng = models.CharField(
        verbose_name='姓(英語)',
        validators=[name_eng_regex],
        max_length=150,
        # blank=True,
        help_text='半角英字と半角スペースで，最初の文字を大文字にして入力してください．'
    )
    nlab = models.BooleanField('中川研', default=False, help_text='所属が中川研の場合，チェックを入れてください．')
    thesis_b = models.CharField(
        verbose_name='卒業論文',
        max_length=300,
        blank=True,
        help_text='卒業論文のタイトルを入力してください．'
    )
    thesis_m = models.CharField(
        verbose_name='修士論文',
        max_length=300,
        blank=True,
        help_text='修士論文のタイトルを入力してください．'
    )
    thesis_d = models.CharField(
        verbose_name='博士論文',
        max_length=300,
        blank=True,
        help_text='博士論文のタイトルを入力してください．'
    )
    
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=True, null=False)
    
    # kyash_url = models.URLField('Kyash 請求リンク', blank=True, max_length=200,
    #                             help_text='ComNets Marketで物品を販売し，支払いをKyashで受け取る場合は，'
    #                                       'Kyashアプリから請求リンクを生成して，ここに登録してください．')
    kyash_qr = models.ImageField(
        upload_to=get_qr_upload_to,
        verbose_name='決済QRコード (Kyash)',
        help_text='ComNets Marketで物品を販売し，支払いをKyashで受け取る場合は，'
                  'KyashアプリからQRコードを保存して，ここに登録してください．',
        blank=True,
    )
    paypay_id = models.CharField('PayPay ID', blank=True, max_length=20,
                                 help_text='ComNets Marketで物品を販売し，支払いをPayPayで受け取る場合は，'
                                           'PayPayアプリでPayPay IDを設定して，ここに登録してください．')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        'first_name_eng',
        'last_name_eng',
    ]
    objects = UserManager()

    class Meta:
        verbose_name = 'USER'
        verbose_name_plural = 'USER'

    def __str__(self):
        if self.last_name == '':
            return self.username
        else:
            return self.last_name + ' ' + self.first_name

    def get_short_name(self):
        if self.last_name == '':
            return self.username
        else:
            if re.match(r'^[\u30A1-\u30F6 ー]+$', self.last_name):  # 名字がカタカナなら(≒留学生)なら
                return self.first_name
            else:  # それいがいなら
                return self.last_name

    def get_short_name_eng(self):
        if self.last_name_eng == '':
            return self.username
        else:
            if re.match(r'^[\u30A1-\u30F6 ー]+$', self.last_name):  # 名字がカタカナなら(≒留学生)なら
                return self.first_name_eng
            else:  # それいがいなら
                return self.last_name_eng

    def get_full_name(self):
        if self.last_name == '':
            return self.username
        else:
            return self.last_name + ' ' + self.first_name
    
    def get_full_name_eng(self):
        if self.last_name_eng == '':
            return self.username
        else:
            return self.last_name_eng + ' ' + self.first_name_eng

    @staticmethod
    def qr_generate(content):
        """
        QRをインメモリで生成してbyteで返す
        :param content: QRコードの中身 (str)
        :return: 生成したQRのbyte
        """
        stream = BytesIO()
        qr_img = qrcode.make(content)  # QRコード生成
        qr_img.save(stream, "PNG")
        stream.seek(0)
        byte_img = stream.read()
        stream.close()
        return byte_img

    # def save(self, *args, **kwargs):
    #     if self.kyash_url:  # urlがあれば
    #         byte_img = self.qr_generate(self.kyash_url)
    #         self.kyash_qr = ContentFile(byte_img, 'kyash.png')  # qrコードをインメモリで保存
    #     obj = super(User, self).save(*args, **kwargs)
    #     return obj


class Teacher(User):
    """教員のユーザクラス"""
    ieice_id_regex = RegexValidator(
        regex=r'[0-9]{7,7}',
        message="7桁の半角英数字で入力してください．"
    )
    ieice_id = models.CharField(
        verbose_name='電子情報通信学会 会員番号',
        default='',
        blank=True,
        max_length=7,
        validators=[ieice_id_regex,],
        help_text='電子情報通信学会の会員番号を入力してください．'
    )
    title = models.CharField(
        verbose_name='職位',
        default='',
        blank=True,
        max_length=5,
    )
    room = models.CharField(
        verbose_name='居室',
        default='',
        blank=True,
        max_length=20,
    )
    phone = models.CharField(
        verbose_name='電話番号',
        default='',
        blank=True,
        max_length=20,
    )
    #email = models.EmailField(
    #    verbose_name='メールアドレス',
    #    blank=True,
    #)
    url = models.URLField('URL', max_length=400,
                          blank=True,
                          null=True,
                          help_text='個人のウェブページURL')
    visitor = models.BooleanField('外部連携研究者', default=True, help_text='外部の連携研究者の場合，チェックを入れてください．')


class Student(User):
    """学生のユーザクラス"""
    student_id_regex = RegexValidator(
        regex=r'[0-9A-Z]{7,8}',
        message="7桁または8桁の半角英数字で入力してください．"
    )
    student_id = models.CharField(
        verbose_name='学籍番号',
        default='',
        blank=True,
        max_length=8,
        validators=[student_id_regex,],
        help_text='大学における学籍番号を記入してください．'
    )
    STATUS = (
        (1, '学士課程3年'),
        (2, '学士課程4年'),
        (11, '修士課程1年'),
        (12, '修士課程2年'),
        (21, '博士課程1年'),
        (22, '博士課程2年'),
        (23, '博士課程3年'),
        (31, '学部卒業'),
        (32, '修士修了'),
        (33, '博士修了'),
        (71, '短期留学生'),
        (72, '短期留学生 在籍期間終了'),
        (91, '休学'),
        (92, '退学'),
        (1001, 'テストユーザ'),
    )
    status = models.IntegerField(
        verbose_name='状態',
        blank=True,
        null=True,
        default=1,
        choices=STATUS,
        help_text='現在の状態を選択してください．'
    )
    assignment_year = models.IntegerField(
        verbose_name='研究室配属年',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(2000,
                                      message='2000年より前の年は入力できません．'),
                    MaxValueValidator(2060,
                                      message='2060年より先の年は入力できません．')],
        help_text='研究室に配属された年を入力してください．'
    )
    MONTH_CHOICE = [(r, r) for r in range(1, 13)]
    assignment_month = models.IntegerField(
        verbose_name='研究室配属月',
        blank=True,
        null=True,
        default=11,
        choices=MONTH_CHOICE,
        help_text='研究室に配属された月を入力してください．'
    )
    graduation_year = models.IntegerField(
        verbose_name='卒業・修了(予定)年',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(2010,
                                      message='2010年より前の年は入力できません．'),
                    MaxValueValidator(2060,
                                      message='2060年より先の年は入力できません．')],
        help_text='卒業・修了・退学・在籍期間終了の(予定)年を入力してください．大学院に進学希望の場合は，大学院の修了予定年を入力してください．'
    )
    graduation_month = models.IntegerField(
        verbose_name='卒業・修了(予定)月',
        blank=True,
        null=True,
        default=3,
        choices=MONTH_CHOICE,
        help_text='卒業・修了・退学・在籍期間終了の(予定)月を入力してください．'
    )
    alma_mater = models.CharField(
        verbose_name='出身校',
        default='',
        blank=True,
        max_length=150,
        help_text='出身の高校，高専，大学を入力してください．短期留学生は元々の所属大学を入力してください．'
    )
    company = models.CharField(
        verbose_name='就職先',
        max_length=150,
        blank=True,
        default='',
        help_text='就職先が決まったら就職先の会社名を入力してください．'
    )

    # マルチテーブル継承のrelated_nameを変更
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, parent_link=True, related_name='user_private')


class StudentPrivate(Student):
    """センシティブな情報を含むユーザクラス"""
    private_email = models.EmailField(
        verbose_name='メールアドレス',
        blank=True,
        help_text='学外のメールアドレスがあれば入力してください．[教員以外には非公開]'
    )
    phone_number_regex = RegexValidator(
        regex=r'^[+0-9]+$',
        message="携帯電話番号は，ハイフン抜き15桁以上の半角数字の列で入力してください．"
    )
    phone_number = models.CharField(
        verbose_name='携帯電話番号',
        validators=[phone_number_regex],
        max_length=15,
        default='',
        blank=True,
        help_text='ハイフン抜きの半角数字の列で入力してください．[教員以外には非公開]'
    )
    scholarship = models.BooleanField('奨学金',
                                      default=False,
                                      null=False,
                                      help_text='日本学生支援機構の奨学金を大学院で取得している場合はチェックを入れてください．[教員以外には非公開]'
                                      )


def add_default_group(sender, instance, **kwargs):
    """デフォルトグループを追加"""
    default_group = Group.objects.get(name='normal')
    instance.groups.add(default_group)  # デフォルトのグループをnormalに指定


# Student 追加後にデフォルトグループを追加
post_save.connect(add_default_group, sender=StudentPrivate)
