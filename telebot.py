import requests
import json
from credentials import botToken

offset = 408171066

re = requests.get(f'https://api.telegram.org/bot{botToken}/getMe')
print(json.dumps(re.json(), indent=4))
re = requests.post(f'https://api.telegram.org/bot{botToken}/getUpdates', data={'offset': offset})
print(json.dumps(re.json(), indent=4))
re = requests.post(f'https://api.telegram.org/bot{botToken}/sendMessage', data={'chat_id': 1037787051, 'text': 'Hello, World!', 'disable_notification': True})