import json
import os
import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, send_file, session
from werkzeug.utils import secure_filename
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '' # Secret Key Generated here. Use generatekey.py
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['SPOTIPY_CLIENT_ID'] = '' # Get this from the spotify developer dashboard
app.config['SPOTIPY_CLIENT_SECRET'] = '' # Get this from the spotify developer dashboard
app.config['SPOTIPY_REDIRECT_URI'] = 'http://localhost:5000/callback' # ADD this from the spotify developer dashboard
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oauth_sessions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class OAuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

sp_oauth = SpotifyOAuth(
    client_id=app.config['SPOTIPY_CLIENT_ID'],
    client_secret=app.config['SPOTIPY_CLIENT_SECRET'],
    redirect_uri=app.config['SPOTIPY_REDIRECT_URI'],
    scope="user-read-private",
    cache_path=None
)

with app.app_context():
    db.create_all()

def token_required(f):
    def decorated(*args, **kwargs):
        username = request.args.get('username')
        token_info = get_token(username)
        if not token_info:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def get_token(username):
    token_info = OAuthToken.query.filter_by(username=username).first()
    if token_info:
        return token_info.as_dict()
    return None


def convert_timestamp(timestamp):
    utc_datetime = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    iso_timestamp = utc_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    return iso_timestamp

def extract_song_artist(entry):
    title = entry.get("title", "")
    if title.lower().startswith("watched"):
        title = title[len("watched "):]

    artist_name = ""
    subtitles = entry.get("subtitles", [])
    if subtitles:
        artist_name = subtitles[0].get("name", "").replace(" - Topic", "").strip()

    if " - " in title:
        parts = title.split(" - ", 1)
        song_title = parts[1].split("(", 1)[0].strip()
        if not artist_name:
            artist_name = parts[0].strip()
    else:
        song_title = title.strip()

    if artist_name.lower() == "release":
        artist_name = ""

    words_to_strip = ["(Official Music Video)", "Fan Video", "[Official Music Video]",
                      "Official Music Video", "MUSIC VIDEO", "OFFICIAL", "[Official Video]", "[HD]",
                      "| EPIC VERSION", "(TikTok remix)", "(Music Video)", "Official MV",
                      "[ VIDEO]", "(Official Video)", "(Live)", "(EPIC TRAILER VERSION)",
                      "| EPIC RUSSIAN VERSION", "★ EPIC ORCHESTRAL MIX ★", "VIDEO"]

    for word in words_to_strip:
        song_title = song_title.replace(word, "").strip()
        artist_name = artist_name.replace(word, "").strip()

    return song_title, artist_name

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip_data = response.json()
        return ip_data['ip']
    except requests.RequestException as e:
        return "Unknown"

def process_watch_history(json_file, sp, username, ip_address):
    with open(json_file, 'r', encoding='utf-8') as file:
        watch_history = json.load(file)

    youtube_music_entries = [
        entry for entry in watch_history
        if entry.get("header") == "YouTube Music"
    ]

    processed_entries = []
    for entry in youtube_music_entries:
        song_title, artist_name = extract_song_artist(entry)
        processed_entries.append({
            "title": song_title,
            "artist": artist_name,
            "time": entry.get("time", "")
        })

    output_file = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{username}_spotify_history.json')
    print(f"Creating output file for user: {username} at {output_file}")  # Debug print
    with open(output_file, 'w') as f:
        f.write("[\n")

        first_entry = True
        for entry in processed_entries:
            timestamp = convert_timestamp(entry['time'])
            song_title = entry['title']
            artist_name = entry['artist']

            query = f'track:{song_title} artist:{artist_name}'
            results = sp.search(q=query, type='track', limit=1)

            if not results['tracks']['items'] and artist_name:
                query = f'track:{song_title}'
                results = sp.search(q=query, type='track', limit=1)

            if results['tracks']['items']:
                track_info = results['tracks']['items'][0]
                spotify_uri = track_info['uri']
                album_id = track_info['album']['id']
                album_info = sp.album(album_id)
                album_name = album_info['name']
                track_length_ms = track_info['duration_ms']

                entry_data = {
                    "ts": timestamp,
                    "username": username,
                    "platform": "android",
                    "ms_played": track_length_ms,
                    "conn_country": "US",
                    "ip_addr_decrypted": ip_address,
                    "user_agent_decrypted": None,
                    "master_metadata_track_name": song_title,
                    "master_metadata_album_artist_name": artist_name,
                    "master_metadata_album_album_name": album_name,
                    "spotify_track_uri": spotify_uri,
                    "episode_name": None,
                    "episode_show_name": None,
                    "spotify_episode_uri": None,
                    "reason_start": "trackdone",
                    "reason_end": "trackdone",
                    "shuffle": False,
                    "skipped": False,
                    "offline": False,
                    "offline_timestamp": 0,
                    "incognito_mode": False
                }

                if not first_entry:
                    f.write(",\n")
                else:
                    first_entry = False
                json.dump(entry_data, f, indent=4)

        f.write("\n]")

    return output_file



@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    username = user_info['id']

    token = OAuthToken.query.filter_by(username=username).first()
    if not token:
        token = OAuthToken(
            username=username,
            access_token=token_info['access_token'],
            refresh_token=token_info['refresh_token'],
            expires_at=token_info['expires_at']
        )
        db.session.add(token)
    else:
        token.access_token = token_info['access_token']
        token.refresh_token = token_info['refresh_token']
        token.expires_at = token_info['expires_at']
    db.session.commit()

    return redirect('/upload')




@app.route('/upload', methods=['GET', 'POST'])
@token_required
def upload_file():
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])

    username = session.get('username')
    ip_address = get_public_ip()
    print(f"Processing upload for user: {username}")

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            output_file = process_watch_history(file_path, sp, username, ip_address)
            print(f"File processed for user: {username}, output: {output_file}")
            return send_file(output_file, as_attachment=True)

    return render_template('upload.html')




if __name__ == '__main__':
    app.run(debug=True)
