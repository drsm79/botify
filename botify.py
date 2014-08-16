import logging
import spotipy
import spotipy.oauth2 as oauth2
import json
import datetime
from errbot import BotPlugin, botcmd


class BotifyPlugin(BotPlugin):
    def activate(self):
        from config import BOTIFY_CREDS
        super(BotifyPlugin, self).activate()
        # dict of name: id for playlists, name is the IRC channel
        self.playlists = {}
        creds = json.load(open(BOTIFY_CREDS))

        client_id = creds.get('CLIENT_ID', 'YOUR_CLIENT_ID')
        client_secret = creds.get('CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
        redirect_uri = creds.get('REDIRECT_URI', 'YOUR_REDIRECT_URI')
        self.username = creds.get('USERNAME', 'USERNAME')

        logging.info('Auth cache:' + creds.get('CACHE_PATH', self.username))

        self.sp_oauth = oauth2.SpotifyOAuth(
            client_id,
            client_secret,
            redirect_uri,
            scope='playlist-modify-public',
            cache_path=creds.get('CACHE_PATH', self.username)
        )

    @botcmd(split_args_with=None, admin_only=True)
    def botify_createlist(self, mess, args):
        self.oath_refresh_if_needed()
        playlist = args[0]
        return '%s created? %s' % (playlist, self.create_playlist(playlist))

    @botcmd(split_args_with=None, admin_only=True)
    def botify_auth(self, mess, args):
        """
        Do the oauth challenge and response fandango
        """
        try:
            if args:
                return self.oauth_validate(args[0])
            else:
                ed = "http://imgur.com/A8QOnaR.jpg"
                return "You have 30 seconds to comply %s\n %s" % (
                    ed,
                    self.oauth_challenge()
                )
        except spotipy.SpotifyException, e:
            logging.error(e)
            return 'ruh roh\n http://i.imgur.com/bmfwvDl.gif'

    @botcmd(split_args_with=None, admin_only=True)
    def botify_authcheck(self, mess, args):
        token = self.sp_oauth.get_access_token()
        datetime.datetime.fromtimestamp(token['expires_at'])
        return "Expires @ %s" % expires.strftime('%H:%M:%S')

    @botcmd
    def botify_list(self, mess, args):
        self.oath_refresh_if_needed()
        playlist = self.playlist_id(mess)
        msg = "Listen along: http://open.spotify.com/user/%s/playlist/%s"
        results = [msg % (self.username, playlist), "-----"]
        if playlist:
            playlist_tracks = self.list_tracks(playlist)
            if len(playlist_tracks) == 0:
                results.append("No tracks in playlist")
            else:
                for d in playlist_tracks:
                    logging.info(d)
                    s = '%s : %s (%s) - %s' % (
                        d['track']['name'],
                        d['track']['album']['name'],
                        ', '.join([a['name'] for a in d['track']['artists']]),
                        d['track']['id']
                    )
                    results.append(s)
        else:
            results = ["No playlist for the room"]
        for d in results:
            yield d.encode('ascii', 'ignore')

    @botcmd
    def botify_search(self, mess, args):
        results = []
        try:
            results = self.search(args)
        except spotipy.SpotifyException, e:
            logging.error(e)
            yield 'ruh roh\n http://i.imgur.com/bmfwvDl.gif'
        else:
            for d in results:
                s = '%s : %s (%s)- %s' % (
                    d['name'],
                    d['album']['name'],
                    ', '.join([a['name'] for a in d['artists']]),
                    d['id'])
                yield s.encode('ascii', 'ignore')

    @botcmd
    def botify_add(self, mess, args):
        self.oath_refresh_if_needed()
        playlist = self.playlist_id(mess)
        if not playlist:
            return "No playlist for the room"
        try:
            if playlist:
                return self.add_track(playlist, args.split(' '))
            else:
                return "No playlist for the room"
        except spotipy.SpotifyException, e:
            logging.error(e)
            return 'ruh roh\n http://i.imgur.com/bmfwvDl.gif'

    def search(self, term, limit=10):
        try:
            tracks = self.sp.search(q=term, limit=limit)
        except spotipy.SpotifyException, e:
            logging.error(e)
            return 'ruh roh\n http://i.imgur.com/bmfwvDl.gif'
        return tracks['tracks']['items']

    def add_track(self, playlist, track_ids):
        logging.info("adding tracks: %s" % track_ids)
        track_ids = ["spotify:track:%s" % t for t in track_ids]
        try:
            self.sp.user_playlist_add_tracks(
                self.username,
                playlist,
                track_ids
            )
        except spotipy.SpotifyException, e:
            if e.http_status != 201:
                # there's a bug in spotipy that thinks a 201 is bad...
                logging.error(e)
                return 'ruh roh\n http://i.imgur.com/bmfwvDl.gif'
        return "Track added"

    def list_tracks(self, playlist):
        return self.sp.user_playlist(
            self.username,
            playlist,
            fields="tracks,next"
        )['tracks']['items']

    def check_playlist(self, playlist):
        playlists = self.sp.user_playlists(self.username)['items']
        self.playlists = dict([(p['name'], p['id']) for p in playlists])
        return playlist in self.playlists

    def create_playlist(self, playlist):
        if not self.check_playlist(playlist):
            logging.info('creating playlist: %s' % playlist)

            try:
                playlist = self.sp.user_playlist_create(
                    self.username,
                    playlist
                )
            except spotipy.SpotifyException, e:
                if e.http_status == 201:
                    # there's a bug in spotipy that thinks a 201 is bad...
                    return self.check_playlist(playlist)
                else:
                    return False

    def playlist_id(self, mess):
        playlist = str(mess.getFrom())

        if self.check_playlist(playlist):
            return self.playlists[playlist]
        else:
            return False

    def oauth_challenge(self):
        return self.sp_oauth.get_authorize_url()

    def oauth_validate(self, response):
        try:
            logging.info("botify validating oauth response: %s" % response)
            code = self.sp_oauth.parse_response_code(response)
            logging.info("botify oauth code: %s" % code)
            token = self.sp_oauth.get_access_token(code)
            if token:
                self.sp = spotipy.Spotify(auth=token['access_token'])
                expires = datetime.datetime.fromtimestamp(token['expires_at'])
                return "Authorised. Expires @ %s" % expires.strftime(
                    '%H:%M:%S'
                )
            else:
                return "http://i.imgur.com/s5guP5z.gif"
        except spotipy.SpotifyException, e:
            logging.error(e)
            return "http://i.imgur.com/s5guP5z.gif"

    def oath_refresh_if_needed(self):
        token = self.sp_oauth.get_cached_token()
        self.sp = spotipy.Spotify(auth=token['access_token'])
