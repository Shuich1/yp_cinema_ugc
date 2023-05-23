Приложение необходимо зарегистировать на `https://o2.mail.ru/app/`, указав 2 Callback uri: `$BASE_URI/api/oauth/mailru/login` и `$BASE_URI/api/oauth/mailru/register`
Полученные Client secret и ClientID необходимо сохранить в переменных окружения:
```
MAILRU_CLIENT_ID=$ClientID
MAILRU_CLIENT_SECRET=$Client_secret
```
Так же необходимо в переменной окружения BASE_URI хранить текущий URI приложения

После чего в приложении можно будет залогинится по uri `https://oauth.mail.ru/login?client_id=$MAILRU_CLIENT_ID&response_type=code&redirect_uri=http://127.0.0.1:5000/api/oauth/mailru/login&state=123` и зарегистрироваться по uri `https://oauth.mail.ru/login?client_id=$MAILRU_CLIENT_ID&response_type=code&redirect_uri=http://127.0.0.1:5000/api/oauth/mailru/register&state=123`