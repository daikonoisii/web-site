from django.urls import path
from .views import QrcodeView


app_name = "market"

urlpatterns = [
    path(r'media/market/<int:pk>_qr_<str:service>', QrcodeView.as_view(), name='qr'),
]
