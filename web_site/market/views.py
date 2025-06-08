# -*- coding: utf-8 -*-
from users.models import User
from django.http import Http404, HttpResponse
from django.views.generic import View
from django.core.files import File


class QrcodeView(View):
    """QRコードを表示"""
    
    def get(self, request, *args, **kwargs):
        pic = User.objects.get(pk=kwargs['pk'])
        if pic is None:
            raise Http404  # なければ404エラー
        try:
            if kwargs['service'] == 'kyash':
                response = HttpResponse(File(open(pic.kyash_qr.path, 'rb')), content_type="image/jpeg")
            else:
                raise Http404  # なければ404エラー
        except FileNotFoundError:
            raise Http404  # なければ404エラー
        return response
