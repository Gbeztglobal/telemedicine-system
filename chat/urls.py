from django.urls import path
from . import views

urlpatterns = [
    path('call/<int:user_id>/', views.video_call, name='video_call'),
]
