from django.urls import path
from . import views

urlpatterns = [
    path('call/<int:user_id>/', views.video_call, name='video_call'),
    path('room/<int:user_id>/', views.chat_room, name='chat_room'),
    path('<int:user_id>/', views.legacy_chat_redirect), # Failsafe for old notification links
    path('voice-note-upload/', views.upload_voice_note, name='voice_note_upload'),
    path('media-upload/', views.upload_chat_media, name='chat_media_upload'),
]
