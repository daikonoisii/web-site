from django.views.generic import View
from django.core.files import File

from django.http import Http404, HttpResponse
from .models import Picture

from django.conf import settings as django_settings
from wiki.plugins.images import settings as wiki_settings


class PictureView(View):
    """画像を表示"""
    
    def get(self, request, *args, **kwargs):
        pic = Picture.objects.get(pk=kwargs['pk'])
        if pic is None:
            raise Http404  # レポートがなければ404エラー
        try:
            if request.user.is_authenticated:
                response = HttpResponse(File(open(pic.file.path, 'rb')), content_type="image/jpeg")
            elif not pic.private:  # メンバー限定公開で設定されていなければ返す
                response = HttpResponse(File(open(pic.file.path, 'rb')), content_type="image/jpeg")
            # elif pic.web or pic.top_page:  # メンバー限定公開の属性設定につき, 上記の分岐(pic.private)にまとめた
            #     response = HttpResponse(File(open(pic.file.path, 'rb')), content_type="image/jpeg")
            else:
                raise Http404  # ログインしていなければ404エラー
        except FileNotFoundError:
            raise Http404  # レポートがなければ404エラー
        return response

class WikiPictureView(View):
    """画像を表示"""
    
    def get(self, request, *args, **kwargs):
        try:
            path = django_settings.MEDIA_ROOT+"/"
            path += wiki_settings.IMAGE_PATH
            aid = kwargs["aid"]
            pk = kwargs["pk"]
            pic_name = kwargs["pic_name"]
            path = path.replace("%aid", aid)
            path += pk+"/"
            path += pic_name

            if request.user.is_authenticated:
                extension = pic_name.split(".")[1]
                if extension == "png":
                    response = HttpResponse(File(open(path, 'rb')), content_type="image/png")
                elif extension == "jpg":
                    response = HttpResponse(File(open(path, 'rb')), content_type="image/jpeg")
            else:
                raise Http404  # ログインしていなければ404エラー
        except FileNotFoundError:
            raise Http404  # レポートがなければ404エラー
        return response
