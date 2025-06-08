from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormMixin
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from users.models import User, Teacher, Student
from paper.models import OurJournalPaper, OurConferencePaper
from activity.models import ProfessionalActivity, Fund, Collaboration
from award.models import Award
from market.models import Item
from .models import Information, Skill, Internship, QAndA, Schedule, Research
from .forms import ExamForm
from picture.models import Picture
from django.db.models import Q
from django.contrib import messages
from lib.japanese import is_japanese
import datetime
import hashlib
import random
import os


class PublicTop(TemplateView):
    """トップページ"""
    template_name = 'public/public_top.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicTop, self).get_context_data(**kwargs)
        information_list = Information.objects.all().order_by('-date')[0:6]  # 最大6個まで表示
        pub_list = PublicAchievements.get_achievement_list('2014-04-01', 'ja', user='kwatabe', journal=True, conference=True)
        watabe_journal_num = len(pub_list[0]['list'])
        watabe_e_conf_num = len(pub_list[1]['list'])
        watabe_j_conf_num = len(pub_list[2]['list'])
        masters_num = Student.objects.filter(status__gte=10, status__lt=30, nlab=False).count()  # 大学院生数
        bachelor_num = Student.objects.filter(status__lt=10, nlab=False).count()  # 学部生数
        print("object_cuunt:"+str(Picture.objects.count()))
        print("*********")
        # 追加: リストが空でないか確認
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
            # 他のコンテキストデータ
        })
        context.update({
            'information_list': information_list,
            'watabe_journal_num': watabe_journal_num,
            'watabe_e_conf_num': watabe_e_conf_num,
            'watabe_j_conf_num': watabe_j_conf_num,
            'masters_num': masters_num,
            'bachelor_num': bachelor_num,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicInformation(TemplateView):
    """過去の情報ページ"""
    template_name = 'public/public_information.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicInformation, self).get_context_data(**kwargs)
        information_list = Information.objects.all().order_by('-date')[6:]  # 最大6個まで表示
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'information_list': information_list,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicAboutUs(TemplateView):
    """研究室紹介ページ"""
    template_name = 'public/public_about_us.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicAboutUs, self).get_context_data(**kwargs)
        companies = Student.objects.filter(Q(status=31) | Q(status=32) | Q(status=33)).values('company')  # 就職先リスト
        companies = [x['company'] for x in companies]  # リスト化
        company_dist = {}
        for c in companies:  # 企業名毎の人数をカウント
            if c != '':
                if c in company_dist:
                    company_dist[c] += 1
                else:
                    company_dist[c] = 1
        company_items = sorted(company_dist.items(), key=lambda x: x[1], reverse=True)  # 人数で並び替え

        researches = Research.objects.all().order_by('weight')  # 研究テーマリスト
        
        skills = Skill.objects.all()  # 就職先リスト
        
        internship = Internship.objects.all().order_by('weight')  # 実務訓練先リスト
        
        q_and_a = QAndA.objects.all().order_by('weight')  # Q&Aリスト
        
        schedule = {}
        for i in range(1, 13):
            schedule[str(i)] = Schedule.objects.filter(month=i).order_by('weight')  # イベントリスト
            if len(schedule[str(i)]) == 0:
                schedule[str(i)] = [None]
        
        pictures = Picture.objects.filter(web=True)
        
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({'company_items': company_items,
                        'researches': researches,
                        'skills': skills,
                        'internship': internship,
                        'q_and_a': q_and_a,
                        'schedule': schedule,
                        'pictures': pictures,
                        'background_image': background_image})  # contextで渡すデータを追加
        return context


class PresentationList(DetailView):
    """プレゼンテーションリストページ"""
    model = Research
    template_name = 'public/public_presentation_list.html'

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PresentationList, self).get_context_data(**kwargs)
        report_list = context['object'].related_research.all().order_by('-created_date')
        paper_list = context['object'].conference_subject.all().exclude(presentation_pdf='').order_by('-created_date')
        presentation_list = []
        for r in report_list:
            presentation_list.append({'title': r.title,
                                      'url': reverse('report:media_pdf', kwargs=dict(pk=r.pk))})
        for p in paper_list:
            presentation_list.append({'title': p.title,
                                      'url': reverse('paper:presentation_pdf', kwargs=dict(pk=p.pk))})
        background_image = Picture.objects.filter(top_page = True).order_by('?')[:1][0]  # 背景のランダムな画像データ
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'presentation_list': presentation_list,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicAchievements(TemplateView):
    """業績ページ"""
    template_name = 'public/public_achievements.html'
    
    @staticmethod
    def get_achievement_list(since, language, user=None, journal=True, conference=True):
        """
        sinceで指定した期日以降の業績リストを出力する関数
        Args:
            since (str): この引数で指定した日以降の業績を取得する．テキスト形式の日付で与える (例: 2014-04-01)
            language (str): 'ja'を与えると日本語の業績を含んで返す．
            user (str): このユーザの業績のみに絞ってリストを返す．Noneを指定するとすべての業績を返す．
            journal (bool): Trueを与えると論文を含んで返す．
            conference (bool): Trueを与えると会議論文を含んで返す．
        Returns:
            辞書形式の業績のリスト
            [
            {'title': 'Journal Articles', 'j_title': '論文誌', 'list': <論文誌業績リスト>}
            {'title': 'International Conference Proceedings', 'j_title': '国際会議', 'list': <国際会議業績リスト>}
            {'title': 'Domestic Conference', 'j_title': 'その他国内発表', 'list': <国内会議業績リスト>}
            ]
        """
        achievements_list = []
        if journal:
            journal_list = []
            if user is not None:
                query = OurJournalPaper.objects.filter(published_date__gte=since,
                                                       author_user__username=user).order_by('-published_date')
            else:
                query = OurJournalPaper.objects.filter(published_date__gte=since).order_by('-published_date')
            for paper in query:
                journal = {
                    'class': 'journal_paper',
                    'pk': paper.pk,
                    'title': paper.title,
                    'author': paper.formed_authors(),
                    'source': paper.source_text(),
                    'year': paper.year,
                    'pdf_publish': paper.pdf_publish(),
                    'post_print_publish': paper.post_print_publish(),
                    'pre_print_publish': paper.pre_print_publish(),
                    'link_publish': paper.link_publish(),
                    'url': paper.url,
                    'publisher': paper.publisher
                }
                journal_list.append(journal)
            achievements_list.append({'title': 'Journal Articles', 'j_title': '論文誌', 'list': journal_list})
        
        if conference:
            domestic_conference_list = []
            international_conference_list = []
            if user is not None:
                query = OurConferencePaper.objects.filter(published_date__gte=since, author_user__username=user) \
                    .order_by('-conference_title__year', '-conference_title__month')
            else:
                query = OurConferencePaper.objects.filter(published_date__gte=since) \
                    .order_by('-conference_title__year', '-conference_title__month')
            for paper in query:
                if is_japanese(paper.conference_title.name):
                    domestic_conference = {
                        'class': 'domestic_conference_paper',
                        'pk': paper.pk,
                        'title': paper.title,
                        'author': paper.formed_authors(),
                        'source': paper.source_text(),
                        'year': paper.conference_title.year,
                        'pdf_publish': paper.pdf_publish(),
                        'post_print_publish': paper.post_print_publish(),
                        'pre_print_publish': paper.pre_print_publish(),
                        'link_publish': paper.link_publish(),
                        'url': paper.url,
                        'publisher': paper.conference_title.organizer
                    }
                    domestic_conference_list.append(domestic_conference)
                else:
                    international_conference = {
                        'class': 'international_conference_paper',
                        'pk': paper.pk,
                        'title': paper.title,
                        'author': paper.formed_authors(),
                        'source': paper.source_text(),
                        'year': paper.conference_title.year,
                        'pdf_publish': paper.pdf_publish(),
                        'post_print_publish': paper.post_print_publish(),
                        'pre_print_publish': paper.pre_print_publish(),
                        'link_publish': paper.link_publish(),
                        'url': paper.url,
                        'publisher': paper.conference_title.organizer
                    }
                    international_conference_list.append(international_conference)
            achievements_list.append({'title': 'International Conference Proceedings', 'j_title': '国際会議',
                                      'list': international_conference_list})
        if language == 'ja' and conference:
            achievements_list.append({'title': 'Domestic Conference', 'j_title': 'その他国内発表',
                                      'list': domestic_conference_list})
        return achievements_list
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicAchievements, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'list': self.get_achievement_list("2014-04-01", self.request.LANGUAGE_CODE, user='kwatabe'),
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicMembers(TemplateView):
    """メンバー一覧ページ"""
    template_name = 'public/public_members.html'
    nlab = False
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicMembers, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        members_list = []
        teacher_list = []
        for m in Teacher.objects.filter(nlab=self.nlab, visitor=False):
            teacher = {
                'class': 'teacher',
                'pk': m.pk,
                'name': m.get_full_name(),
                'title': m.title,
                'room': m.room,
                'phone': m.phone,
                'mail': m.email.replace('@', '[at]'),
                'url': m.url,
                'image': m.avatar,
            }
            teacher_list.append(teacher)
        members_list.append({'title': 'Teachers', 'j_title': '教員', 'list': teacher_list})
        
        master_list = []
        bachelor_list = []
        for m in Student.objects.filter(nlab=self.nlab).order_by('-status', 'last_name_kana'):
            student = {
                'class': m.status,
                'pk': m.pk,
                'name': m.get_full_name(),
                'grade': dict(Student.STATUS)[m.status],
                'alma_mater': m.alma_mater,
                'image': m.avatar,
            }
            if m.status == 11 or m.status == 12 or m.status == 21 or m.status == 22 or m.status == 23:  # 大学院
                master_list.append(student)
            elif m.status == 1 or m.status == 2:  # 学士
                bachelor_list.append(student)
        members_list.append({'title': 'Graduate Student Members', 'j_title': '博士・修士課程', 'list': master_list})
        members_list.append({'title': 'Undergraduate Student Members', 'j_title': '学士課程', 'list': bachelor_list})
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'list': members_list,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicNakagawaLabMembers(PublicMembers):
    """中川研メンバー一覧ページ"""
    template_name = 'public/public_nakagawa_lab_members.html'
    nlab = True


class PublicFormerMembers(TemplateView):
    """過去のメンバー一覧ページ"""
    template_name = 'public/public_former_members.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicFormerMembers, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        members_list = []
        doctor_list = []
        master_list = []
        bachelor_list = []
        exchange_list = []
        dropout_list = []
        for m in Student.objects.all().order_by('-status', '-graduation_year', '-graduation_month', 'last_name_kana'):
            if m.thesis_d != '':
                thesis_type = '博士論文'
                thesis = m.thesis_d
            elif m.thesis_m != '':
                thesis_type = '修士論文'
                thesis = m.thesis_m
            elif m.thesis_b != '':
                thesis_type = '学士論文'
                thesis = m.thesis_b
            else:
                thesis_type = None
                thesis = None
            student = {
                'class': m.status,
                'pk': m.pk,
                'name': m.get_full_name(),
                'assignment_year': m.assignment_year,
                'assignment_month': m.assignment_month,
                'graduation_year': m.graduation_year,
                'graduation_month': m.graduation_month,
                'alma_mater': m.alma_mater,
                'company': m.company,
                'thesis_type': thesis_type,
                'thesis': thesis,
                'image': m.avatar,
                'nlab': m.nlab,
            }
            if m.status == 33:  # 博士修了
                doctor_list.append(student)
            elif m.status == 32:  # 修士修了
                master_list.append(student)
            elif m.status == 31:  # 学士卒業
                bachelor_list.append(student)
            elif m.status == 72:  # 期間修了短期留学生
                exchange_list.append(student)
            elif m.status == 91 or m.status == 92:  # 休学・退学・除籍
                dropout_list.append(student)
        members_list.append({'title': 'Ph.D. Holders', 'j_title': '博士課程修了生', 'list': doctor_list})
        members_list.append({'title': "Master's Degree Holders", 'j_title': '修士課程修了生', 'list': master_list})
        members_list.append({'title': "Bachelor's Degree Holders", 'j_title': '学士課程卒業生', 'list': bachelor_list})
        members_list.append({'title': "Short-Term Exchange Students", 'j_title': '短期留学生', 'list': exchange_list})
        members_list.append({'title': "Absence/dropout", 'j_title': '休学・退学・除籍', 'list': dropout_list})
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'list': members_list,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicContacts(TemplateView):
    """連絡先一覧ページ"""
    template_name = 'public/public_contacts.html'

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicContacts, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabe(TemplateView):
    """教員ページ"""
    template_name = 'public/public_kwatabe.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabe, self).get_context_data(**kwargs)
        watabe = User.objects.get(username='kwatabe')
        researches = Research.objects.all().order_by('weight')  # 研究テーマリスト
        pub_list = PublicAchievements.get_achievement_list('2008-04-01', 'ja', user='kwatabe', journal=True, conference=True)
        watabe_journal_num = len(pub_list[0]['list'])
        watabe_e_conf_num = len(pub_list[1]['list'])
        watabe_j_conf_num = len(pub_list[2]['list'])
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'researches': researches,
            'watabe_journal_num': watabe_journal_num,
            'watabe_e_conf_num': watabe_e_conf_num,
            'watabe_j_conf_num': watabe_j_conf_num,
            'watabe': watabe,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabeProfile(TemplateView):
    """教員プロフィールページ"""
    template_name = 'public/public_kwatabe_profile.html'

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabeProfile, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        awards = []
        student_awards = []
        watabe = User.objects.get(last_name='渡部', first_name='康平')
        nakagawa = User.objects.get(last_name='中川', first_name='健治')
        professional_activity = ProfessionalActivity.objects.all().order_by('-start_date')
        fund = Fund.objects.all().order_by('-start_date')
        collaboration = Collaboration.objects.all().order_by('-start_date')
        all_awards = Award.objects.all().order_by('-date')
        for a in all_awards:
            if watabe in a.user.all():
                awards.append(a)
            if len(a.user.exclude(pk=watabe.pk).exclude(pk=nakagawa.pk).all()) > 0:
                student_awards.append(a)
        context.update({
            'awards': awards,
            'professional_activity': professional_activity,
            'fund': fund,
            'collaboration': collaboration,
            'student_awards': student_awards,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabePublications(PublicAchievements):
    """個人業績ページ"""
    template_name = 'public/public_kwatabe_publications.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabePublications, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'list': self.get_achievement_list("2000-04-01", self.request.LANGUAGE_CODE, user='kwatabe'),
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKNakagawaPublications(PublicAchievements):
    """中川先生個人業績ページ"""
    template_name = 'public/public_knakagawa_publications.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKNakagawaPublications, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None

        list_ = self.get_achievement_list("1900-04-01", self.request.LANGUAGE_CODE,
                                         user='nakagawa', journal=True, conference=False)
        context.update({
            'url_prefix': settings.URL_PREFIX,
            'list': list_,
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class LimitedUrlMixin(TemplateView):
    """期間限定URLを発行するMixin"""
    def get_hash(self, expire):
        """日付からハッシュを返す関数"""
        return hashlib.md5((expire + self.__class__.__name__).encode()).hexdigest()
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super().get_context_data(**kwargs)
        login = False
        limited_auth = False
        if self.request.user.username != '':
            login = True  # ログインしていればTrue
        else:
            if 'expire' in self.request.GET and 'hash' in self.request.GET:
                expire_str = self.request.GET['expire']
                date_hash = self.get_hash(expire_str)  # 日付のハッシュを生成
                if date_hash == self.request.GET['hash']:  # 日付から生成したハッシュが一致するか調べる
                    if datetime.datetime.today().date() <= datetime.datetime.strptime(expire_str, '%Y-%m-%d').date():  # 有効期限内か調べる
                        limited_auth = True  # 時間限定で表示を許可する場合はTrue
                    else:
                        messages.info(self.request, 'このURLは有効期限が切れています．ページを閲覧したい場合は，管理者に連絡して有効なURLを発行してもらってください．')
                else:
                    messages.info(self.request, 'このURLは無効なURLです．ページを閲覧したい場合は，管理者に連絡して有効なURLを発行してもらってください．')
            else:
                messages.info(self.request, 'このページは限定公開ページです．'
                                            'ページを閲覧したい場合は，ログインするか，管理者に連絡して有効なURLを発行してもらってください．')
        today = datetime.datetime.today()
        host = self.request.get_host()
        path = self.request.path
        key_list = []
        for d in (1, 14, 30, 365):
            expire = today + datetime.timedelta(days=d-1)
            date_str = str(expire.strftime('%Y-%m-%d'))
            date_hash = self.get_hash(date_str)  # 日付のハッシュを生成
            key_list.append('https://{}{}?expire={}&hash={}'.format(host, path, date_str, date_hash))
        context.update({
            'limited_auth': limited_auth,
            'login': login,
            'key_list': key_list,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabeSchedule(LimitedUrlMixin, TemplateView):
    """渡部の予定ページ"""
    template_name = 'public/public_kwatabe_schedule.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabeSchedule, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicSchedule(LimitedUrlMixin, TemplateView):
    """研究室全体の予定ページ"""
    template_name = 'public/public_schedule.html'
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicSchedule, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page = True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabeExam(LimitedUrlMixin, FormMixin, TemplateView):
    """試験問題のページ"""
    template_name = 'public/public_kwatabe_exam.html'
    form_class = ExamForm
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            student_id = self.request.POST['student_id']
            exam_id = random.randint(1, 6)  # 問題を決める乱数を生成
            print('Exam: {},{},{}\r'.format(str(datetime.datetime.today()), student_id, exam_id))
            with open(settings.MEDIA_ROOT + '/exam.csv', "a") as f:
                f.write('{},{},{}\r'.format(str(datetime.datetime.today()), student_id, exam_id))
            if exam_id == 1:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSfvo5-SPak5aQpleG0-96Hjc1heiezMbUuRl9Mol7TQc4Q47g/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            elif exam_id == 2:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSf909V5A5evKwE64fO4ZyK4H8YSJ3UWDuR2pCRvtWaJ-GxgZQ/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            elif exam_id == 3:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdRBKIdFXMrhi9QVM8vpERLM-nGNUW5twuu2tI8U0TSd_rsuw/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            elif exam_id == 4:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSc_Bm2R0mk7dct9xJc92muSqH6Cf80tPV00-2isCne8rEr_Tw/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            elif exam_id == 5:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeW514Ze0JEd7dieUvQ1XsDF3bhZvPCLQ95xxAbzojIGhqkTw/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            elif exam_id == 6:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSduAfRx7zLwFx2i3jHuLceDRHZsdzGt5N64wEK0GhpnTBcVNA/viewform?usp=sf_link&entry.1639829601={}'.format(student_id)
            else:
                raise Http404  # URLがなければ404エラー
            return HttpResponseRedirect(exam_url)
        raise Http404  # URLがなければ404エラー

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabeExam, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicKWatabeExam2(LimitedUrlMixin, FormMixin, TemplateView):
    """試験問題のページ"""
    template_name = 'public/public_kwatabe_exam2.html'
    form_class = ExamForm
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            student_id = self.request.POST['student_id']
            exam_id = random.randint(1, 3)  # 問題を決める乱数を生成
            print('Exam: {},{},{}\r'.format(str(datetime.datetime.today()), student_id, exam_id))
            with open(settings.MEDIA_ROOT + '/exam.csv', "a") as f:
                f.write('{},{},{}\r'.format(str(datetime.datetime.today()), student_id, exam_id))
            if exam_id == 1:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdjfntOesX1vhiarfQf59STzxSYZ5ERoCG0zLBwcneneeLewA/viewform?usp=sf_link&entry.1639829601={}'.format(
                    student_id)
            elif exam_id == 2:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeRmBzCoQglTzQmz-ocI77d_unSkX_CJAWGmA2bHZ9Pu8-wgQ/viewform?usp=sf_link&entry.1639829601={}'.format(
                    student_id)
            elif exam_id == 3:
                exam_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeFweuP6dbDEnVsA1kDKaLGHBiwWUf0LCxHChTe70My1IM1dA/viewform?usp=sf_link&entry.1639829601={}'.format(
                    student_id)
            else:
                raise Http404  # URLがなければ404エラー
            return HttpResponseRedirect(exam_url)
        raise Http404  # URLがなければ404エラー
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicKWatabeExam2, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PublicMarket(ListView):
    """マーケットのページ"""
    template_name = 'public/public_market.html'
    model = Item
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(PublicMarket, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        context.update({
            'background_image': background_image,
        })  # contextで渡すデータを追加
        return context


class PhotoGalleryView(LoginRequiredMixin, TemplateView):
    template_name = 'public/public_photo_gallery.html'

    def get_context_data(self, **kwargs):
        context = super(PhotoGalleryView, self).get_context_data(**kwargs)
        picture_list = Picture.objects.filter(top_page=True).order_by('?')[:1]  # 背景のランダムな画像データ
        if picture_list:
            background_image = picture_list[0]
        else:
            background_image = None
        picture_list = []
        # 研究室の活動写真については表示条件要検討
        lab_picture = Picture.objects.filter(category=1).order_by('-created_date')
        picture_list.append({'title': 'Lab Events.', 'j_title': '研究室イベント', 'picture_list': lab_picture})
        # 飯テロ写真は取扱要注意
        dish_picture = Picture.objects.filter(private=True, category=6).order_by('-created_date')
        picture_list.append({'title': "Food Porn.", 'j_title': '飯テロ', 'picture_list': dish_picture})

        context.update({
            'url_prefix': settings.URL_PREFIX,
            'background_image': background_image,
            'list': picture_list,
        })  # contextで渡すデータを追加
        return context
