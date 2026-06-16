import yt_dlp
import requests
import re
import tempfile
import os


def download_and_convert_to_mp3(video_url):
    tmpdir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'js_runtimes': {'node': {'executable': 'node'}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        title = info.get('title', 'audio')
    mp3_path = os.path.join(tmpdir, f"{title}.mp3")
    if os.path.exists(mp3_path):
        return mp3_path, title
    for f in os.listdir(tmpdir):
        if f.endswith('.mp3'):
            return os.path.join(tmpdir, f), title
    return None, title
    
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'no_color': True,
        'noplaylist': True,
        'skip_download': True,
        'js_runtimes': {'node': {'executable': 'node'}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def get_title_from_info(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'js_runtimes': {'node': {'executable': 'node'}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        infoo=ydl.extract_info(url, download=False)
    minutes, remaining_seconds = divmod( infoo.get('duration'), 60)
    video_info ="title: "+infoo.get('title')+"\n"+"Res: "+infoo.get('resolution')+" Dur: "+(f"{minutes} min: {remaining_seconds} sec") +" Size: "+ f"{'{0:.3g}'.format(int(infoo.get('filesize_approx'))/1000000)} Mb"+" Ext: "+infoo.get('ext')

    return infoo.get('title', 'video')



def get_best_stream_url(info, max_height=None):
    formats = info.get('formats', [])
    # Prefer combined (video+audio), fall back to video-only
    for mode in ('combined', 'video_only'):
        best = None
        for f in formats:
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            ext = f.get('ext', '')
            if ext not in ('mp4', 'webm'):
                continue
            if mode == 'combined' and (vcodec == 'none' or acodec == 'none'):
                continue
            if mode == 'video_only' and vcodec == 'none':
                continue
            height = f.get('height', 0) or 0
            if max_height and height > max_height:
                continue
            if best is None or height > best.get('height', 0):
                best = f
        if best:
            return best['url']
    url_manual = info.get('url')
    if url_manual:
        return url_manual
    for f in formats:
        if f.get('url'):
            return f['url']
    raise ValueError('No playable stream found')


def get_available_resolutions(info):
    formats = info.get('formats', [])
    heights = set()
    for f in formats:
        vcodec = f.get('vcodec', 'none')
        ext = f.get('ext', '')
        if vcodec != 'none' and ext in ('mp4', 'webm'):
            height = f.get('height', 0) or 0
            if height:
                heights.add(height)
    return sorted(heights, reverse=True)


def extract_video_id(url):
    patterns = [
        r'(?:youtube\.(?:com|be)/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)([\w-]+)',
        r'(?:vimeo\.com/|player\.vimeo\.com/video/)(\d+)',
        r'(?:dailymotion\.com/video/|dai\.ly/)([^_/?]+)',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def stream_generator(url, chunk_size=8192):
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            yield chunk
