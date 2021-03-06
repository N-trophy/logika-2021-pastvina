# Finálová úloha Logiky N-Trophy 2021

## Howto

### Initialize environment

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ export DJANGO_SETTINGS_MODULE=pastvina.settings.development
```

### Create db structure

```bash
$ ./manage.py makemigrations pastvina
$ ./manage.py migrate pastvina
```

### Run development server

```bash
$ cp pastvina/settings/development.py.txt pastvina/settings/development.py
Edit pastvina/settings/development.py as you wish.
$ ./manage.py collectstatic
$ ./manage.py runserver
```

### Deploy to production

```bash
$ cp pastvina/settings/production.py.txt pastvina/settings/production.py
Edit pastvina/settings/development.py as you wish.
$ ./manage.py collectstatic --settings=pastvina.settings.production
```
