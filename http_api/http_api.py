import os

import requests
from tqdm import tqdm

from vk_worker import VKPhotoWorker, VKException


def download_images(urls: list, path_to_download: str):
    """
    Downloads all images from the links in the transmitted path.
    :param urls: pictures urls list
    :param path_to_download:
    """
    for index, url in tqdm(enumerate(urls), total=len(urls),
                           desc="Downloading images"):
        try:
            response = requests.get(url)
            with open(
                    os.path.join(path_to_download, str(index) + '.jpg'),
                    'wb'
            ) as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print(e.strerror)


def main():
    access_token = input('Enter access token:')
    try:
        vk_worker = VKPhotoWorker(access_token)
        albums = vk_worker.request_albums_list()
        print(' '.join(albums.keys()))
        album_name = input('Choose album name:')
        while album_name not in albums.keys():
            album_name = input('Choose correct album name:')
        album_id = albums[album_name]

        path_to_download = input('Enter path to download')
        urls_list = vk_worker.request_photos_from_album(album_id)
        download_images(urls_list, path_to_download)
    except VKException as e:
        print(e.message)


if __name__ == '__main__':
    main()
