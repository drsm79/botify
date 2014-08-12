import logging
import spotipy
import spotipy.oauth2 as oauth2
import json
import config
from errbot import BotPlugin, botcmd


class BotifyPlugin(BotPlugin):
    def activate(self):
        super(BotifyPlugin, self).activate()
        logging.info('Fetch creds from' + config.__dict__.get("BOTIFY_CREDS"))
        self.botify = Botify(config.__dict__.get("BOTIFY_CREDS"))

    @botcmd
    def botify_list(self, mess, args):
        return mess, args

    @botcmd
    def botify_search(self, mess, args):
        return "http://i.imgur.com/bmfwvDl.gif"

    @botcmd
    def botify_add(self, mess, args):
        return "http://i.imgur.com/bmfwvDl.gif"


class Botify:
    def __init__(self, creds):
        creds = json.load(open(creds))
        client_id = creds.get('CLIENT_ID', 'YOUR_CLIENT_ID')
        client_secret = creds.get('CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
        redirect_uri = creds.get('REDIRECT_URI', 'YOUR_REDIRECT_URI')

        self.username = creds.get('USERNAME', 'USERNAME')

        sp_oauth = oauth2.SpotifyOAuth(
            client_id,
            client_secret,
            redirect_uri,
            scope='playlist-modify-public',
            cache_path=self.username
        )

        token = sp_oauth.get_cached_token()

        self.sp = spotipy.Spotify(auth=token['access_token'])

    def search(self, term, limit=10):
        tracks = self.sp.search(q=term, limit=limit)
        return tracks['tracks']['items']

    def add_track(self, playlist, track_ids):
        self.sp.trace = False
        results = self.sp.user_playlist_add_tracks(
            self.username,
            playlist,
            track_ids
        )
        return results

    def list_tracks(self, playlist):
        return self.sp.user_playlist(
            self.username,
            playlist,
            fields="tracks,next"
        )
