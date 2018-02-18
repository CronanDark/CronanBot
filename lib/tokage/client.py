from .http import HTTPClient
from .abc import *
from .errors import *

class Client:
    BASE_URL = 'https://jikan.me/api/v1.1/'
    ANIME_URL = BASE_URL + 'anime/'
    MANGA_URL = BASE_URL + 'manga/'
    PERSON_URL = BASE_URL + 'person/'
    CHARACTER_URL = BASE_URL + 'character/'

    def __init__(self):
        self.client = HTTPClient()

    async def get_anime(self, target_id):
        response_json = await self.client.request(self.ANIME_URL + str(target_id))
        if response_json is None:
            raise AnimeNotFound("Anime with the given ID was not found")
        result = Anime(target_id, **response_json)
        return result
    async def get_manga(self, target_id):
        response_json = await self.client.request(self.MANGA_URL + str(target_id))
        if response_json is None:
            raise MangaNotFound("Manga with the given ID was not found")
        result = Manga(target_id, **response_json)
        return result
    async def get_character(self, target_id):
        response_json = await self.client.request(self.CHARACTER_URL + str(target_id))
        if response_json is None:
            raise CharacterNotFound("Character with the given ID was not found")
        result = Character(target_id, **response_json)
        return result
    async def get_person(self, target_id):
        response_json = await self.client.request(self.PERSON_URL + str(target_id))
        if response_json is None:
            raise PersonNotFound("Person with the given ID was not found")
        result = Person(target_id, **response_json)
        return result