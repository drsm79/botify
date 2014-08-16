botify
======

an IRC bot that can manage a spotify playlist

## Intall and configure

Install via:

    !repos install https://github.com/drsm79/botify
    
where `!` is your errbot control character.

Before you configure the bot you need to go to the [spotify developer area][2] and create an application. The settings of that app then need to be given to the bot, as per below.

Configuration is in two places; the errbot `config.py` where you point to a credentials json file and the corresponding file. That should looke like:

    {
      "CLIENT_ID": "ID from https://developer.spotify.com/my-applications/#!/applications",
      "CLIENT_SECRET":"Secret from https://developer.spotify.com/my-applications/#!/applications",
      "USERNAME": "Your username",
      "REDIRECT_URI":"a URL to a domain you control from https://developer.spotify.com/my-applications/#!/applications",
      "CACHE_PATH": "where you want your OAuth token to be written"
    }

### Note
You may want to install spotipy from [my fork][1] instead of the default from pip, e.g.:

    pip install --upgrade https://github.com/drsm79/spotipy/archive/master.zip
    
This has a few bugfixes that are yet to make it into a release and support for deleting from a playlist.

[1]: https://github.com/drsm79/spotipy
[2]: https://developer.spotify.com/my-applications/#!/applications
