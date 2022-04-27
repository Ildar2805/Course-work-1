import requests
import urllib.request
import os
import datetime
import json
import time
from progress.bar import IncrementalBar

from pprint import pprint

with open('Token.TXT') as file:
    tokenVK = file.read().strip()

class VkPhoto:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photo(self, user_id):
        photo_get_url = self.url + 'photos.get'
        photo_get_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': '1',
            'count': '5'
        }
        req = requests.get(photo_get_url, params={**self.params, **photo_get_params})
        return req.json()['response']['items']

    def selection(self):
        list_photos = []
        for photo in self.get_photo(user_id):
            add_photo = {}
            add_photo['likes'] = photo['likes']['count']
            add_photo['sizes'] = photo['sizes'][-1]
            add_photo['date'] = photo['date']
            list_photos.append(add_photo)
        return list_photos

    def file_download(self):
        list_photos_name = []
        bar = IncrementalBar('Скачено фоток: ', max = 5)
        for photo in self.selection():
            add_photo = {}
            url = photo['sizes']['url']
            img = urllib.request.urlopen(url).read()
            file_name = str(photo['likes']) + '.jpg'
            if os.path.isfile(file_name):
                date = str(datetime.datetime.utcfromtimestamp(photo['date']))
                file_name = f"{photo['likes']}_{date.split()[0]}.jpg"
                with open(file_name, 'wb') as file:
                    file.write(img)
                add_photo['file_name'] = file_name
                add_photo['size'] = photo['sizes']['type']
                with open('Info.json', 'a') as info:
                    json.dump(add_photo, info)
                list_photos_name.append(file_name)
                bar.next()
            else:
                with open(file_name, 'wb') as file:
                    file.write(img)
                add_photo['file_name'] = file_name
                add_photo['size'] = photo['sizes']['type']
                with open('Info.json', 'a') as info:
                    json.dump(add_photo, info)
                list_photos_name.append(file_name)
                bar.next()
        bar.finish()
        return list_photos_name

class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, folder_name):
        create_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": folder_name}
        response = requests.put(create_folder_url, params=params, headers=headers)
        return response

    def _get_upload_link(self, file):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": file, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload(self):
        folder_name = 'Photos from VK'
        self.create_folder(folder_name)
        bar = IncrementalBar('Загружено на Яндекс Диск: ', max= 5)
        for ph in photo.file_download():
            href_json = self._get_upload_link(folder_name + '/' + ph)
            href = href_json['href']
            response = requests.put(href, data=open(ph, 'rb'))
            response.raise_for_status()
            bar.next()
        bar.finish()

if __name__ == '__main__':
    user_id = input('Введите id пользователя VK: ')
    tokenYaDisk = input('Введите токен YaDisk: ')
    photo = VkPhoto(tokenVK, '5.131')
    ya_disk_uploader = YaUploader(tokenYaDisk)
    ya_disk_uploader.upload()

