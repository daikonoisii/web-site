from django.http.response import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
import requests
from requests.sessions import session

# Create your views here.
class LightOn(LoginRequiredMixin, View):
	"""ラズパイの照明ONするURLにGETリクエスト
	"""
	def get(self, request, *args, **kwargs):
	    # set Target URL.
	    url = "http://133.44.120.81:5001/light-on"
	    session = requests.Session()
	    session.trust_env = False
	    response = session.get(url)
	    return HttpResponse(response)

# ラズパイの照明OFFするURLにGETリクエスト
class LightOff(LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
	    # set Target URL.
	    url = "http://133.44.120.81:5001/light-off"
	    session = requests.Session()
	    session.trust_env = False
	    response = session.get(url)
	    return HttpResponse(response)
