import re

def parse_id(link):
    pattern = r'(?:\\/([\d]+)\\/)'
    match = re.search(pattern, link)
    if match:
        target_id = match.group(1)
        return target_id
    else:
        return None

class Anime:
    def __init__(self, anime_id, **kwargs):
        self.id = anime_id
        self.title = kwargs.pop('title', None)
        self.type = kwargs.pop('type', None)
        self.synonyms = kwargs.pop('synonyms', None)
        self.image = kwargs.pop('image', None)
        self.japanese_title = kwargs.pop('japanese', None)
        self.status = kwargs.pop('status', None)
        self.episodes = kwargs.pop('episodes', None)
        self.air_time = kwargs.pop('aired', None)
        self.premiered = kwargs.pop('premiered', None)
        self.broadcast = kwargs.pop('broadcast', None)
        self.synopsis = kwargs.pop('synopsis', None)
        self.producers = kwargs.pop('producer', None)
        self.licensors = kwargs.pop('licensor', None)
        self.studios = kwargs.pop('studio', None)
        self.source = kwargs.pop('source', None)
        self.raw_genres = kwargs.pop('genre', None)
        if self.raw_genres is None:
            self.raw_genres = kwargs.pop('genres', None)
        self.genres = [g[1] for g in self.raw_genres] if self.raw_genres else None
        self.duration = kwargs.pop('duration', None)
        self.link = kwargs.pop('link-canonical', None)
        self.rating = kwargs.pop('rating', None)
        self.score = kwargs.pop('score', None)
        self.rank = kwargs.pop('ranked', None)
        self.popularity = kwargs.pop('popularity', None)
        self.members = kwargs.pop('members', None)
        self.favorites = kwargs.pop('favorites', None)
        self.related = kwargs.pop('related', None)
        if self.related is not None:
            self.adaptation = self.related.get("Adaptation", None)
            self.sequel = self.related.get("Sequel", None)
            self.prequel = self.related.get("Prequel", None)

class Manga:
    def __init__(self, manga_id, **kwargs):
        self.id = manga_id
        self.title = kwargs.pop('title', None)
        self.type = kwargs.pop('type', None)
        self.synonyms = kwargs.pop('synonyms', None)
        self.image = kwargs.pop('image', None)
        self.japanese_title = kwargs.pop('japanese', None)
        self.status = kwargs.pop('status', None)
        self.volumes = kwargs.pop('volumes', None)
        self.chapters = kwargs.pop('chapters', None)
        self.publish_time = kwargs.pop('published', None)
        self.synopsis = kwargs.pop('synopsis', None)
        self.authors = kwargs.pop('authors', None)
        self.serialization = kwargs.pop('serialization', None)
        self.raw_genres = kwargs.pop('genre', None)
        if self.raw_genres is None:
            self.raw_genres = kwargs.pop('genres', None)
        self.genres = [g[1] for g in self.raw_genres] if self.raw_genres else None
        self.link = kwargs.pop('link-canonical', None)
        self.rating = kwargs.pop('rating', None)
        self.score = kwargs.pop('score', None)
        self.rank = kwargs.pop('ranked', None)
        self.popularity = kwargs.pop('popularity', None)
        self.members = kwargs.pop('members', None)
        self.favorites = kwargs.pop('favorites', None)
        self.related = kwargs.pop('related', None)
        if self.related is not None:
            self.adaptation = self.related.get("Adaptation", None)
            self.sequel = self.related.get("Sequel", None)
            self.prequel = self.related.get("Prequel", None)

class Character:
    def __init__(self, char_id, **kwargs):
        self.id = char_id
        self.image = kwargs.pop('image', None)
        self.favorites = kwargs.pop('member-favorites', None)
        self.animeography = kwargs.pop('animeography', None)
        self.mangaography = kwargs.pop('mangaography', None)
        self.name = kwargs.pop('name', None)
        self.japanese = kwargs.pop('name-japanese', None)
        self.about = kwargs.pop('about', None)
        self.raw_voice_actors = kwargs.pop('voice-actors', None)

class Person:
    def __init__(self, person_id, **kwargs):
        self.id = person_id
        self.name = kwargs.pop('name', None)
        self.image = kwargs.pop('image', None)
        self.birthday = kwargs.pop('birthday', None)
        self.more = kwargs.pop('more', None)
        self.favorites = kwargs.pop('member-favorites', None)
        self.website = kwargs.pop('website', None)
        self.voice_acting = kwargs.pop('voice-acting-role', None)
        self.anime = kwargs.pop('anime-staff-position', None)
        self.manga = kwargs.pop('published-manga', None)
