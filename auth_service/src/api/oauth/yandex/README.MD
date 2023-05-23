Приложение необходимо зарегистировать на `https://oauth.yandex.ru/`, указав 2 Callback uri: `$BASE_URI/api/oauth/yandex/login` и `$APP_URI/api/oauth/yandex/register`
Полученные Client secret и ClientID необходимо сохранить в переменных окружения:
```
YANDEX_CLIENT_ID=$ClientID
YANDEX_CLIENT_SECRET=$Client_secret
```
После чего в приложении можно будет залогинится по uri `https://oauth.yandex.ru/authorize?response_type=code&client_id=$YANDEX_CLIENT_ID&redirect_uri=$BASE_URI/api/oauth/yandex/login` и зарегистрироваться по uri `https://oauth.yandex.ru/authorize?response_type=code&client_id=$YANDEX_CLIENT_ID&redirect_uri=$BASE_URI/api/oauth/yandex/register`