# -*- coding: utf-8 -*-
from django.views.generic import UpdateView, CreateView
from .models import StudentPrivate, Teacher
from .forms import StudentPrivateForm, StudentPrivateAddForm, TeacherForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.core.files import File
from django.http import Http404, HttpResponse
from .models import User


class MyAccount(LoginRequiredMixin, UpdateView):
    """自アカウント情報の変更用ページ"""
    model = StudentPrivate
    form_class = StudentPrivateForm
    template_name = "users/my_account.html"
    success_url = settings.URL_PREFIX + "/"  # 成功時にトップページに飛ばす
    title = 'アカウント設定'
    
    def get(self, request, *args, **kwargs):
        if hasattr(self.request.user, 'teacher'):
            return redirect(reverse("users:my_account_teacher"))  # 教員なら教員向けページにリダイレクト
        response = super().get(self, request, *args, **kwargs)
        return response

    def form_valid(self, form):
        """バリデーションに成功したとき"""
        messages.info(self.request, '"%s" の情報を更新しました．' % self.object.get_full_name())
        return super().form_valid(form)
    
    def get_object(self, queryset=None):
        return StudentPrivate.objects.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(MyAccount, self).get_context_data(**kwargs)
        context.update({'title': 'アカウント設定',
                        'has_permission': True})  # contextで渡すデータを追加
        return context


class MyAccountTeacher(LoginRequiredMixin, UpdateView):
    """教員の自アカウント情報の変更用ページ"""
    model = Teacher
    form_class = TeacherForm
    template_name = "users/my_account.html"
    success_url = settings.URL_PREFIX + "/"  # 成功時にトップページに飛ばす
    title = 'アカウント設定'
    
    def form_valid(self, form):
        """バリデーションに成功したとき"""
        messages.info(self.request, '"%s" の情報を更新しました．' % self.object.get_full_name())
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return Teacher.objects.get(pk=self.request.user.pk)
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(MyAccountTeacher, self).get_context_data(**kwargs)
        context.update({'title': 'アカウント設定',
                        'has_permission': True})  # contextで渡すデータを追加
        return context


class AddStudentPrivate(LoginRequiredMixin, CreateView):
    """アカウント追加用ページ
    Studentモデルとして追加すると，StudentPrivateモデルが追加されないため，StudentPrivateモデルとして追加するページを作成した．
    """
    form_class = StudentPrivateAddForm
    template_name = "users/add_user_private.html"
    success_url = settings.URL_PREFIX + "/admin/users/"  # 成功時にユーザ管理ページに飛ばす
    title = 'アカウント追加'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        """contextを渡す関数をオーバーライド"""
        context = super(AddStudentPrivate, self).get_context_data(**kwargs)
        context.update({'title': 'アカウント追加',
                        'has_permission': True})  # contextで渡すデータを追加
        return context
    
    class Meta:
        model = StudentPrivate
        fields = [
            'username',
            'password',
        ]


class AvatarView(View):
    """画像を表示"""
    
    def get(self, request, *args, **kwargs):
        pic = User.objects.get(pk=kwargs['pk'])
        if pic is None:
            raise Http404  # レポートがなければ404エラー
        try:
            response = HttpResponse(File(open(pic.avatar.path, 'rb')), content_type="image/jpeg")
        except FileNotFoundError:
            raise Http404  # レポートがなければ404エラー
        return response
