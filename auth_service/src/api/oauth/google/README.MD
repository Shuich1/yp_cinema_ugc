Приложение необходимо зарегистировать на https://console.cloud.google.com/apis/credentials/oauthclient/ и получить client_secret.json
Т.к. в нем ключи, то в репозитории файла не будет, если нужно тестировать, генерируем свой.

Так же необходимо в переменной окружения BASE_URI хранить текущий URI приложения.

После чего в приложении можно будет залогинится по uri https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=$client_id&redirect_uri=$redirect_uri&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile&state=$state&access_type=offline&include_granted_scopes=true