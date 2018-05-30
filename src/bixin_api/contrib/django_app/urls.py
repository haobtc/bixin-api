from django.urls import (
    path,
)

from . import views


urlpatterns = [
    path('events_callback/', views.events_view),
    path('test/qrcode/', views.transfer_debug_qr_code),
]
