import requests
from pprint import pprint
import os

ya_token = ""
vk_token = ""
local_path = "D:\\vkphotos"
ya_disk_path = "fromvkphotos/"


def get_integer_id(id):
    '''Получить числовой идентификатор'''
    link = 'https://api.vk.com/method/utils.resolveScreenName'
    params = {
        'screen_name': id,
        'access_token': vk_token,
        'v': 5.131
    }
    response = requests.get(link, params=params).json()
    id_int = response['response']['object_id']
    return id_int


def get_photos(id):
    '''Получить словарь, состоящий из ссылок на фотографий и количество лайков'''
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id' : id,
        'album_id' : 'profile',
        'access_token' : vk_token,
        'v' : 5.131,
        'photo_sizes' : 0,
        'extended': 1
    }
    response = requests.get(url,params=params).json()
    count = response['response']['count']
    photo_link_dict = {}
    for item in response['response']['items']:
        photo_link_dict[item['sizes'][-1]['url']] = item['likes']['count']

    return photo_link_dict


def download_photos(photo_dict):
    '''Сохранить фотографии и назвать фото по количеству лайков '''
    for photo in photo_dict:
        name = photo_dict[photo]
        print(name)
        resp = requests.get(photo).content
        with open(f'{local_path}\{name}.jpg','wb') as f:
            f.write(resp)

def upload_to_yadisk(ya_disk_path,filename):
    '''Загрузить фотографию на яндекс диск'''
    ya_disk_path = ya_disk_path + filename
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Content-Type": "application/json", "Authorization": "OAuth {}".format(ya_token)}
    params = {"path": ya_disk_path, "overwrite": "true"}
    href_response = requests.get(upload_url, headers=headers, params=params)
    href = href_response.json().get("href", "")
    upload_response = requests.put(href, data=open(filename, "rb"))
    upload_response.raise_for_status()
    if upload_response.status_code == 201:
        print(f"{filename} is uploaded")

def upload_photo_from_dir():
    photos= os.listdir(local_path)
    os.chdir(local_path)
    for photo in photos:
        upload_to_yadisk(ya_disk_path,photo)

if __name__ == '__main__':
    string_id = 'begemot_korovin'
    int_id = get_integer_id(string_id)
    photo_dict = get_photos(int_id)
    download_photos(photo_dict)
    upload_photo_from_dir()

