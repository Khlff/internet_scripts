import requests


class VKException(Exception):
    def __init__(self, message):
        self.message = message


class VKPhotoWorker:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.user_id = self.request_user_id()

    def request_user_id(self) -> int:
        """
        Gets the id of the auth token owner.
        :return: User id.
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'fields': 'id',
            'access_token': self.access_token,
            'v': '5.131'
        }

        response = dict(
            requests.get(url, params=params).json()
        )

        if 'error' in response.keys():
            raise VKException(response['error']['error_msg'])

        return int(response['response'][0]['id'])

    def request_albums_list(self) -> dict:
        """
        Gets a dictionary of album titles and ids.
        :return: Dictionary {title : id}.
        """
        albums_url = 'https://api.vk.com/method/photos.getAlbums'
        albums_params = {
            'access_token': self.access_token,
            'owner_id': self.user_id,
            'extended': 1,
            'v': '5.131'
        }

        albums_response = dict(
            requests.get(
                albums_url,
                params=albums_params
            ).json()
        )

        if 'error' in albums_response.keys():
            raise VKException(albums_response['error']['error_msg'])

        albums = {
            item['title']: item['id']
            for item in albums_response['response']['items']
        }
        return albums

    def request_photos_from_album(self, album_id: int) -> list:
        """
        Takes links to photos from the album.
        :param album_id: ID of the album from which we take links to photos.
        :return: list of photo urls
        """
        photos_url = 'https://api.vk.com/method/photos.get'
        photos_params = {
            'access_token': self.access_token,
            'owner_id': self.user_id,
            'album_id': album_id,
            'extended': 1,
            'v': '5.131'
        }

        photos_response = dict(
            requests.get(
                photos_url,
                params=photos_params
            ).json()
        )
        if 'error' in photos_response.keys():
            raise VKException(photos_response['error']['error_msg'])

        photo_urls = [
            item['sizes'][-1]['url']
            for item in photos_response['response']['items']
        ]
        return photo_urls
