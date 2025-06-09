from django.views.generic import View
from django.core.files import File

from django.http import Http404, HttpResponse
from .models import Picture

from django.conf import settings as django_settings
from wiki.plugins.images import settings as wiki_settings

from PIL import Image

class PictureView(View):
    """画像を表示"""
    
    def get(self, request, *args, **kwargs):
        pic = Picture.objects.get(pk=kwargs['pk'])
        if pic is None:
            raise Http404  # レポートがなければ404エラー
        try:
            if request.user.is_authenticated:
                response = get_resized_image_response(pic.file.path)
            elif not pic.private:  # メンバー限定公開で設定されていなければ返す
                response = get_resized_image_response(pic.file.path)
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


def get_resized_image_response(path, format='JPEG', size=(800, 600), quality=70):
    im = Image.open(path)
    im = im.convert('RGB')
    im.thumbnail(size)
    im_io = io.BytesIO()
    im.save(im_io, format=format, quality=quality)
    return HttpResponse(im_io.getvalue(), content_type="image/jpeg")