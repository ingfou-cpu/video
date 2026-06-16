from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_video, name='add_video'),
    path('watch/<int:video_id>/', views.watch_video, name='watch_video'),
    path('stream/<int:video_id>/', views.stream_video, name='stream_video'),
    path('convert/<int:video_id>/', views.convert_to_mp3, name='convert_to_mp3'),
    path('download/<int:video_id>/', views.download_video, name='download_video'),
    path('delete/<int:video_id>/', views.delete_video, name='delete_video'),
    path('api/fetch-metadata/', views.fetch_video_metadata, name='fetch_video_metadata'),
]
