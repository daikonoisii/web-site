from django.views.generic import DetailView, FormView, ListView, RedirectView, TemplateView, View
from wiki import models
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from wiki.decorators import get_article
from django.views.generic.edit import ModelFormMixin
from wiki.forms import SortForm
from django.contrib.auth.decorators import login_required
import json

# 表示用
class CategoryView(ListView):
    template_name = "wiki/article_list.html"
    model = models.urlpath.URLPath
    form_class = SortForm

    def get_queryset(self):
        return self.object_list

class SoftwareListView(CategoryView):
    label = "software"
    success_url = reverse_lazy("wiki:%s"%(label))

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.model.objects.filter(article__current_revision__tag=0,
                                                     article__current_revision__deleted=0)
        self.object_list = objlist2params(self.object_list)
        return super().get(request, *args, **kwargs)

class ServerListView(CategoryView):
    label = "server"
    success_url = reverse_lazy("wiki:%s"%(label))

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.model.objects.filter(article__current_revision__tag=1,
                                                    article__current_revision__deleted=0)
        self.object_list = objlist2params(self.object_list)
        return super().get(request, *args, **kwargs)

class LabTipsListView(CategoryView):
    label = "lab_tips"
    success_url = reverse_lazy("wiki:%s"%(label))

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.model.objects.filter(article__current_revision__tag=2,
                                                     article__current_revision__deleted=0)
        self.object_list = objlist2params(self.object_list)
        return super().get(request, *args, **kwargs)

class SchoolLifeTipsListView(CategoryView):
    label = "schoollife_tips"
    success_url = reverse_lazy("wiki:%s"%(label))

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.model.objects.filter(article__current_revision__tag=3,
                                                     article__current_revision__deleted=0)
        self.object_list = objlist2params(self.object_list)
        return super().get(request, *args, **kwargs)

class EtceteraListView(CategoryView):
    label = "etcetera"
    success_url = reverse_lazy("wiki:%s"%(label))

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.model.objects.filter(article__current_revision__tag=4,
                                                     article__current_revision__deleted=0)
        self.object_list = objlist2params(self.object_list)
        return super().get(request, *args, **kwargs)

def objlist2params(objlist):
    param_list = []
    for obj in objlist:
        param_list.append({
                "path" : obj.path,
                "name" : obj.article.current_revision.title,
                "parent": str(obj.parent),
                "owner": str(obj.article.owner),
                "created": str(obj.article.created),
                "modified": str(obj.article.modified)
                })
    return json.dumps(param_list, ensure_ascii=False)
