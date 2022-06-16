## Readme for developers:

1) You need to copy the following link and download files for practising.

[Data files](https://disk.yandex.ru/d/YRy6chw4OumnOw)

> Download all the files directly in the /static/mat/ folder, they are already added to .gitignore.
> Only files that end to -d3.mat are okay

2) Usage example:

```
git clone https://github.com/Jonny-programmer/PGI
cd PGI
pip install -r requirements.txt
```
3) Starting the app:
```commandline
python3 main.py
```
4) If you want to start the app normally, you need to create .env file (in root dir):
```javascript
HOST=smtp.yandex.ru
PORT=465
FROM=<your-email-address>@yandex.ru
PASSWORD=<your-yandex-app-password>
```
You can get a yandex app password [here](https://passport.yandex.ru/profile/)
> В разделе "Пароли и авторизация" выберите "Включить пароли приложений."
> Подтвердите действие и нажмите "Создать новый пароль."