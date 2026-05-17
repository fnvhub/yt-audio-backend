from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import yt_dlp
import subprocess
import os
import re

app = Flask(__name__)
CORS(app)

def is_valid_youtube_url(url):
    pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return re.match(pattern, url) is not None

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "YT Audio Backend funcionando"})

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "URL de YouTube no válida"}), 400

   ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'cookiefile': 'cookies.txt',
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title", "Sin título"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", ""),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio')
def audio():
    url = request.args.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "URL de YouTube no válida"}), 400

    ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'cookiefile': 'cookies.txt',
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Buscar el mejor formato de audio
            audio_url = None
            for f in reversed(formats):
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f.get('url')
                    break
            
            if not audio_url:
                # Fallback: usar la URL del mejor formato disponible
                audio_url = info.get('url')

            if not audio_url:
                return jsonify({"error": "No se pudo obtener el audio"}), 500

            return jsonify({"audio_url": audio_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
