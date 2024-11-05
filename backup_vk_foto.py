from dotenv import load_dotenv
import os
import requests
from pprint import pprint

# Извлечение из глобальных переменных в операционную систему токенов ВК и Яндекс Диск
dotenv_path = 'config_example.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
vk_token = os.getenv('VK_TOKEN')
ya_token = os.getenv('YA_TOKEN')


# Создание класса для извлечения фотографий профиля из аккаунта ВК
class VKConnektor:
    def __init__(self, access_token, version='5.199'):
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.access_token,
            'v': self.version
        }

# Метод класса для извлечения фотографий профиля из аккаунта ВК
    def photo_info(self, user_id):
        url = f'{self.base_url}photos.get'
        params = {
          **self.params,
          'owner_id': user_id,
          'album_id': 'profile',
          'extended': '1'
        }
        response = requests.get(url, params=params)
        return response.json()


# Создание объекта класса для VKConnektor, передача в класс параметров 
# connector = VKConnektor(vk_token)     
# photos_info = connector.photo_info(581197663)
# pprint(photos_info)

# Создание папки для хранения фотографий на Яндекс Диск
class YDConnektor:
    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_name):
        response = requests.put(url='https://cloud-api.yandex.net/v1/disk/resources',
                                headers=self.headers,
                                params={'path': folder_name})
        return response.status_code

# Запуск создания папки на Яндекс Диск с вводом имени папки    
# yd_connector = YDConnektor(ya_token)
new_folder_name = input('Введите название папки на Яндекс Диск латинскими буквами: ')
# yd_connector.create_folder({new_folder_name})

# Сохранение фотографии с заданным url в папку на Яндекс Диск
photo_url = 'https://sun9-80.userapi.com/s/v1/ig2/jRuAvhhXuT2nXa3Z3EeiyCmFPzXBsrvb7idbLrdqR_cQolm3El909wOC0KI9SkbBHkzQyFmqM2hwKkPTRQwxZDOM.jpg?quality=95&as=32x32,48x48,72x72,108x108,160x160,240x240,360x360,480x480,540x540,640x640,720x720,1000x1000&from=bu&cs=1000x1000'
url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
params = {
    'path': f'/{new_folder_name}/PTRQwxZDOM.jpg',
    'url': photo_url
}
headers = {
    'Authorization': f'OAuth {ya_token}'
}
respons = requests.post(url, params=params, headers=headers)
print(respons.status_code)
pprint(respons.json())
