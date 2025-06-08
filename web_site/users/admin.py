# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, Teacher, Student, StudentPrivate


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)


class TeacherAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('avatar', 'username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name',
            'first_name_kana', 'last_name_kana',
            'first_name_eng', 'last_name_eng',
            'ieice_id',
            'nlab',
            'visitor',
            'title',
            'room',
            'phone',
            'email',
            'url',
        )}),
        (_('Permissions'), {'fields': ('is_active',
                                       'groups')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        ('payments', {'fields': ('kyash_qr', 'paypay_id',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('username', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)


class StudentAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('avatar', 'username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name',
            'first_name_kana', 'last_name_kana',
            'first_name_eng', 'last_name_eng',
            ('status', 'nlab',),
            'student_id',
            ('assignment_year', 'assignment_month'),
            ('graduation_year', 'graduation_month'),
            'alma_mater',
            'company',
            'thesis_b',
            'thesis_m',
            'thesis_d',
        )}),
        (_('Permissions'), {'fields': ('is_active',
                                       'groups')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        ('payments', {'fields': ('kyash_qr', 'paypay_id',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('username', 'last_name', 'first_name', 'first_name_eng', 'last_name_eng',
                    'status', 'graduation_year')
    list_filter = ('is_superuser', 'is_active', 'groups', 'status', 'assignment_year', 'graduation_year')
    search_fields = ('username', 'first_name', 'last_name', 'first_name_eng', 'last_name_eng',
                     'alma_mater', 'company', 'student_id',)
    ordering = ('status', 'last_name_kana')
    actions = ['graduate', 'upgrade']  # アクションを登録
    
    def upgrade(self, request, queryset):
        """学年を一つ上げる操作のaction"""
        for q in queryset:
            test = q.get_status_display()
            if q.get_status_display() in ('学士課程3年', '修士課程1年', '博士課程1年', '博士課程2年'):  # 進級する学年なら
                q.status += 1
            elif q.get_status_display() in ('学士課程4年', '修士課程2年'):  # 進学する学年なら
                q.status += 9
            q.save()
    upgrade.short_description = "選択された %(verbose_name_plural)s の進級・進学処理"
    
    def graduate(self, request, queryset):
        """卒業・修了操作のaction"""
        for q in queryset:
            if q.get_status_display() == '学士課程4年':  # 学士なら
                q.status = 31
            elif q.get_status_display() == '修士課程2年':  # 修士なら
                q.status = 32
            elif q.get_status_display() in ('博士課程1年', '博士課程2年', '博士課程3年'):  # 博士なら
                q.status = 33
            q.save()
    graduate.short_description = "選択された %(verbose_name_plural)s の卒業・修了処理"


class StudentPrivateAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('avatar', 'username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name',
            'first_name_kana', 'last_name_kana',
            'first_name_eng', 'last_name_eng',
            ('status', 'nlab',),
            'student_id',
            ('assignment_year', 'assignment_month'),
            ('graduation_year', 'graduation_month',),
            'alma_mater',
            'company',
            'email',
            'phone_number',
            'scholarship',
            'thesis_b',
            'thesis_m',
            'thesis_d',
        )}),
        (_('Permissions'), {'fields': ('is_active',
                                       'groups')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        ('payments', {'fields': ('kyash_qr', 'paypay_id', )})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('username', 'student_id', 'last_name', 'first_name', 'first_name_eng', 'last_name_eng',
                    'status', 'graduation_year', 'scholarship')
    list_filter = ('is_superuser', 'is_active', 'groups', 'status', 'assignment_year', 'graduation_year', 'scholarship')
    search_fields = ('username', 'first_name', 'last_name', 'first_name_eng', 'last_name_eng',
                     'alma_mater', 'company', 'student_id',)
    ordering = ('status', 'last_name_kana')


class AwardAdmin(admin.ModelAdmin):
    """Awardクラスのadminをカスタマイズ"""
    list_display = ('date', 'title', 'winner')  # 表示項目を指定
    search_fields = ['title', 'winner', 'org']  # 検索対象
    ordering = ('date',)  # デフォルトのソート順
    list_filter = ['user']  # フィルタを設置


admin.site.register(User)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentPrivate, StudentPrivateAdmin)
