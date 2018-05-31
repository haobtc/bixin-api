from django.urls import (
    path,
)

from . import views


urlpatterns = [
    path('events_callback/', views.events_view),
    path('test/transfer_in/', views.transfer_debug_qr_code),
    path('test/transfer_out/', views.transfer_out),
]
