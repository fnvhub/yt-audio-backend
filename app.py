from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import re

app = Flask(__name__)
CORS(app)

def is_valid_youtube_url(url):
    pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return re.match(pattern, url) is not None

@app.route('/')
def index():
    return jsonify({"status": "ok"})

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "URL no válida"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # 'cookiefile': 'cookies.txt',
        'format': None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)
            return jsonify({
                "title": data.get("title", "Sin título"),
                "thumbnail": data.get("thumbnail", ""),
                "duration": data.get("duration", 0),
                "uploader": data.get("uploader", ""),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio')
def audio():
    url = request.args.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "URL no válida"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # 'cookiefile': 'cookies.txt',
        'format': None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)

            formats = data.get('formats', [])
            audio_url = None

            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f.get('url')
                    break

            if not audio_url:
                for f in formats:
                    if f.get('url') and f.get('acodec') != 'none':
                        audio_url = f.get('url')
                        break

            if not audio_url:
                audio_url = data.get('url')

            if not audio_url:
                return jsonify({"error": "No se encontró audio"}), 500

            return jsonify({"audio_url": audio_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
