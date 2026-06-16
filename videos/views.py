from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Video
from .forms import VideoForm
from .utils import get_video_info, get_best_stream_url, stream_generator, download_and_convert_to_mp3, get_title_from_info
import re
import requests
import os
import shutil
from urllib.parse import quote


def home(request):
    query = request.GET.get('q', '').strip()
    videos = Video.objects.all().order_by('-created_at')
    if query:
        videos = videos.filter(title__icontains=query)
    
    paginator = Paginator(videos, 10)
    page_number = request.GET.get('page')
    videos_page = paginator.get_page(page_number)
    
    return render(request, 'videos/home.html', {
        'videos': videos_page,
        'query': query,
        'paginator': paginator,
        'page_obj': videos_page
    })


def add_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            # Récupérer automatiquement le titre et la description YouTube
            try:
                info = get_video_info(video.url)
                youtube_title = info.get('title', '')
                youtube_description = info.get('description', '')
                if youtube_title:
                    video.title = youtube_title
                if youtube_description:
                    video.description = youtube_description
            except Exception:
                pass
            if not video.title:
                video.title = 'Untitled Video'
            video.save()
            return redirect('home')
    else:
        form = VideoForm()
    return render(request, 'videos/add.html', {'form': form})
def fetch_video_metadata(request):
    """API endpoint: given a URL, return JSON with title and description from YouTube."""
    url = request.GET.get('url', '')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)
    try:
        info = get_video_info(url)
        return JsonResponse({
            'title': info.get('title', ''),
            'description': info.get('description', ''),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#----------------------------------------
def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    titre_video = get_title_from_info(video.url)
    if request.method == 'GET':
            form = get_title_from_info(initial={'video_info': titre_video})
    else:
        form = get_title_from_info(request.POST)

    return render(request, 'mon_template.html', {'form': form})

def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'videos/watch.html', {'video': video})


def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    try:
        info = get_video_info(video.url)
        stream_url = get_best_stream_url(info)
        return StreamingHttpResponse(
            streaming_content=stream_generator(stream_url),
            content_type='video/mp4',
        )
    except Exception as e:
        return HttpResponse(f'Stream error: {e}', status=500)
    
def convert_to_mp3(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    try:
        mp3_path, youtube_title = download_and_convert_to_mp3(video.url)
        if not mp3_path:
            return HttpResponse('Conversion failed: no MP3 file produced', status=500)

        def file_iterator():
            tmpdir = os.path.dirname(mp3_path)
            try:
                with open(mp3_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

        safe_title = re.sub(r'[\\/:*?"<>|]', '', youtube_title)[:100]
        response = StreamingHttpResponse(
            streaming_content=file_iterator(),
            content_type='audio/mpeg',
        )
        encoded_name = quote(safe_title + '.mp3', safe='')
        response['Content-Disposition'] = f'attachment; filename="video.mp3"; filename*=UTF-8\'\'{encoded_name}'
        return response
    except Exception as e:
        return HttpResponse(f'Conversion error: {e}', status=500)

def download_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    try:
        info = get_video_info(video.url)
        youtube_title = info.get('title', video.title)
        stream_url = get_best_stream_url(info)
        response = requests.get(stream_url, stream=True)
        response.raise_for_status()
        safe_title = re.sub(r'[\\/:*?"<>|]', '', youtube_title)[:100]
        encoded_name = quote(safe_title + '.mp4', safe='')
        response_headers = {
            'Content-Disposition': f'attachment; filename="video.mp4"; filename*=UTF-8\'\'{encoded_name}',
            'Content-Type': 'video/mp4',
        }
        return StreamingHttpResponse(
            streaming_content=response.iter_content(chunk_size=8192),
            headers=response_headers,
        )
    except Exception as e:
        return HttpResponse(f'Download error: {e}', status=500)


def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        video.delete()
        return redirect('home')
    return render(request, 'videos/video_confirm_delete.html', {'video': video})

