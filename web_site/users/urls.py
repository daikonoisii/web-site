from django.conf.urls import url
from django.urls import path
from .views import MyAccount, MyAccountTeacher, AddStudentPrivate, AvatarView


app_name = "users"

urlpatterns = [
    url(r'^myaccount$', MyAccount.as_view(), name='my_account'),
    url(r'^myaccount_teacher$', MyAccountTeacher.as_view(), name='my_account_teacher'),
    url(r'^add_user_private', AddStudentPrivate.as_view(), name='add_user_private'),
    path(r'media/avatar/<int:pk>', AvatarView.as_view(), name='avatar'),
]
