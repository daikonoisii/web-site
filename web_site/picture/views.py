from django.views.generic import View
from django.core.files import File

from django.http import Http404, HttpResponse
from .models import Picture

from django.conf import settings as django_settings
from wiki.plugins.images import settings as wiki_settings

import os


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


def serve_image_with_cache(request, image_name):
    # 画像ファイルのパスを構築（MEDIA_ROOTからの例）
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)

    if not os.path.exists(image_path):
        # ファイルが存在しない場合は404エラーを返すなど
        return HttpResponse("Image not found", status=404)

    with open(image_path, 'rb') as f:
        image_data = f.read()

    response = HttpResponse(image_data, content_type="image/jpeg") # 画像のMIMEタイプを適切に設定
    
    # ここで Cache-Control ヘッダーを追加する
    response['Cache-Control'] = 'public, max-age=31536000' # 1年間キャッシュ
    # response['Cache-Control'] = 'public, max-age=86400, immutable' # 例えば1日間、不変であることを示す場合

    return response