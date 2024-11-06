from dotenv import load_dotenv
import os
import requests
from pprint import pprint
from datetime import datetime, timezone
import json
from tqdm import tqdm

# Извлечение из глобальных переменных в операционную систему токенов ВК и Яндекс Диск
dotenv_path = 'config_example.env'
if os.path.exists(dotenv_path):
  load_dotenv(dotenv_path)

# Токен Яндекс Диска можно вводить или читать из глобальной переменной
user_id = input('Введите id пользователя ВК: ')
# ya_token = input('Введите токен Яндекс Диска: ')
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
  
# Класс - создание папки для хранения фотографий на Яндекс Диск
class YDConnektor:
    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_name):
        response = requests.put(url='https://cloud-api.yandex.net/v1/disk/resources',
                                headers=self.headers,
                                params={'path': folder_name})
        return response.status_code


# Функция - проверка: ответ от ВК без ошибок, в аккаунте ВК есть фотографии профиля 
def validate_photo_info(photo_info, user_id):
  if 'error' in photo_info:
    print("Проверьте токен ВК!")
    return False

  photos = photo_info.get('response', {}).get('items', [])
  if not photos:
    print(f"У id {user_id} нет фотографий профиля.")
    return False

  return True

# Функция принимает json файл ответ от ВК с фотографиями профиля,
# ищет фотографии максимального размера в пикселях и возвращает список из 5 таких фотографий 
def get_largest_photos(photos_info, top_n=5):
  photos = photos_info.get('response', {}).get('items', [])
  largest_photos = []

  # Используем tqdm для отображения прогресса цикла
  for photo in tqdm(photos, desc='Processing photos', unit='photo'):
    max_size = max(photo['sizes'], key=lambda s: s['width'] * s['height'])
    largest_photos.append({
      'url': max_size['url'],
      'likes': photo['likes']['count'],
      'date': photo['date'],
      'area': max_size['width'] * max_size['height']
    })

  largest_photos.sort(key=lambda p: (p['area'], p['likes'], p['date']), reverse=True)
  return largest_photos[:top_n]

# Функция загружает фотографии на Яндекс Диск с проверкой прошла загрузка или нет
def download_photo_to_yandex_disk(photo_info, ya_token):
  base_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
  headers = {
    'Authorization': f'OAuth {ya_token}'
  }
  uploaded_photos_info = []

  for photo in photo_info:
    likes = photo['likes']
    date = photo['date']
  
    date_str = datetime.fromtimestamp(date, timezone.utc).strftime('%d.%m.%Y')

    filename = f"{likes}_{date_str}.jpg"
    params = {
      'path': f'/Image_vk/{filename}',
      'url': photo['url']
    }

    response = requests.post(base_url, params=params, headers=headers)
    if response.status_code == 202:
      print(f"Фото {filename} успешно загружено на Яндекс Диск")
      uploaded_photos_info.append({"file_name": filename, "size": f"{photo['area']} px"})
    else:
      print(f"Ошибка при загрузке фото на Яндекс Диск {filename}: {response.json()}")

  # Сохранение информации о загруженных на Яндекс Диск фотографиях в JSON-файл
  with open('uploaded_photos.json', 'w') as json_file:
    json.dump(uploaded_photos_info, json_file, indent=4)
  # pprint(uploaded_photos_info)


# Создание объекта класса для VKConnektor, передача в класс параметров          
connector = VKConnektor(vk_token)
photos_info = connector.photo_info(user_id)

# Запуск создания папки на Яндекс Диск с вводом имени папки    
# yd_connector = YDConnektor(ya_token)
# new_folder_name = input('Введите название папки на Яндекс Диск латинскими буквами: ')
# yd_connector.create_folder({new_folder_name})

# Запуск загрузки фото на Яндекс Диск в случае когда нет ошибок и есть фотографии
if validate_photo_info(photos_info, user_id):
    largest_photos = get_largest_photos(photos_info)
    download_photo_to_yandex_disk(largest_photos, ya_token)