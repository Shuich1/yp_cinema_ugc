Приложение необходимо зарегистировать на: https://vk.com/apps?act=manage и получили id приложения
Полученные Client secret и ClientID необходимо сохранить в переменных окружения:
```
VK_CLIENT_ID=$ClientID
VK_CLIENT_SECRET=$Client_secret
```

Так же необходимо в переменной окружения BASE_URI хранить текущий URI приложения

После чего в приложении можно будет залогинится по uri `https://oauth.vk.com/oauth/authorize?client_id=$client_id&display=page&redirect_uri=$redirect_uri&scope=email&response_type=code&v=5.131`
