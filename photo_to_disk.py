import requests
from pprint import pprint
import os
import time
import json


ya_token = "AQAAAABVJsmLAADLW3Qbu3zpx0GhgLQhhGY94qs"
vk_token = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"

ya_disk_path = "fromvkphotos/"
os.mkdir('photos')
os.mkdir('data_json')
os.chdir('photos')
local_path = os.getcwd()


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
        photo_link_dict[item['sizes'][-1]['url']] = [item['likes']['count'],item['sizes'][-1]['type']]
        pprint(item)

    return photo_link_dict


def download_photos(photo_dict):
    '''Сохранить фотографии и назвать фото по количеству лайков '''
    for photo in photo_dict:
        name = photo_dict[photo][0]
        print(f'{name}.jpg')
        resp = requests.get(photo).content
        if os.path.exists(f'{name}.jpg'):
            uniqtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            name = str(name) + uniqtime
            photo_dict[photo][0] = name
        with open(f'{local_path}\{name}.jpg','wb') as f:
            f.write(resp)
    return photo_dict


def progress_bar(filename):
    size = os.path.getsize(filename)
    block = size/10240
    for i in range(1,int(block)+1):
        time.sleep(0.2)
        print("==",end ='')
    print('>',filename, 'is upload!')


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
        progress_bar(filename)

def upload_photo_from_dir():
    photos= os.listdir(local_path)
    os.chdir(local_path)
    for photo in photos:
        upload_to_yadisk(ya_disk_path,photo)

def create_file_info(photo_dict):
    os.chdir('..')
    os.chdir('data_json')
    for item in photo_dict:
        data = [{
            'file_name': f'{photo_dict[item][0]}.jpg',
            'size': photo_dict[item][1]
        }]
        with open(f"{photo_dict[item][0]}.json", "w") as write_file:
            json.dump(data, write_file)
if __name__ == '__main__':
    string_id = 'begemot_korovin'
    int_id = get_integer_id(string_id)
    photo_dict = get_photos(int_id)
    photo_dict_new = download_photos(photo_dict)
    upload_photo_from_dir()
    create_file_info(photo_dict_new)