from arm.ui import db


class UISettings(db.Model):
    """
    Class to hold the A.R.M ui settings
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    use_icons = db.Column(db.Boolean)
    save_remote_images = db.Column(db.Boolean)
    bootstrap_skin = db.Column(db.String(64))
    language = db.Column(db.String(4))
    index_refresh = db.Column(db.Integer)
    database_limit = db.Column(db.Integer)
    notify_refresh = db.Column(db.Integer)
    # AI & Metadata settings
    openai_api_key = db.Column(db.String(256))
    tmdb_api_key = db.Column(db.String(128))
    omdb_api_key = db.Column(db.String(128))
    musicbrainz_useragent = db.Column(db.String(128))
    musicbrainz_contact = db.Column(db.String(128))
    discogs_token = db.Column(db.String(128))
    enable_ai_identification = db.Column(db.Boolean, default=False)
    enable_cd_track_renaming = db.Column(db.Boolean, default=False)
    min_clip_duration_seconds = db.Column(db.Integer, default=300)

    def __init__(self, use_icons=None, save_remote_images=None,
                 bootstrap_skin=None, language=None, index_refresh=None,
                 database_limit=None, notify_refresh=None,
                 openai_api_key=None, tmdb_api_key=None, omdb_api_key=None,
                 musicbrainz_useragent=None, musicbrainz_contact=None, discogs_token=None,
                 enable_ai_identification=False, enable_cd_track_renaming=False,
                 min_clip_duration_seconds=300):
        self.use_icons = use_icons
        self.save_remote_images = save_remote_images
        self.bootstrap_skin = bootstrap_skin
        self.language = language
        self.index_refresh = index_refresh
        self.database_limit = database_limit
        self.notify_refresh = notify_refresh
        self.openai_api_key = openai_api_key
        self.tmdb_api_key = tmdb_api_key
        self.omdb_api_key = omdb_api_key
        self.musicbrainz_useragent = musicbrainz_useragent
        self.musicbrainz_contact = musicbrainz_contact
        self.discogs_token = discogs_token
        self.enable_ai_identification = enable_ai_identification
        self.enable_cd_track_renaming = enable_cd_track_renaming
        self.min_clip_duration_seconds = min_clip_duration_seconds

    def __repr__(self):
        return f'<UISettings {self.id}>'

    def __str__(self):
        """Returns a string of the object"""

        return_string = self.__class__.__name__ + ": "
        for attr, value in self.__dict__.items():
            return_string = return_string + "(" + str(attr) + "=" + str(value) + ") "

        return return_string

    def get_d(self):
        """ Returns a dict of the object"""
        return_dict = {}
        for key, value in self.__dict__.items():
            if '_sa_instance_state' not in key:
                return_dict[str(key)] = str(value)
        return return_dict
