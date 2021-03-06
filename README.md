# Finálová úloha Logiky N-Trophy 2021

## Howto

### Initialize environment

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

### Create db structure

```bash
$ ./manage.py makemigrations pastvina --settings=pastvina.settings.development
$ ./manage.py migrate pastvina --settings=pastvina.settings.development
```

### Run development server

```bash
$ cp pastvina/settings/development.py.txt pastvina/settings/development.py
Edit pastvina/settings/development.py as you wish.
$ ./manage.py collectstatic --settings=pastvina.settings.development
$ ./manage.py runserver --settings=pastvina.settings.development
```

### Deploy to production

```bash
$ cp pastvina/settings/production.py.txt pastvina/settings/production.py
Edit pastvina/settings/development.py as you wish.
$ ./manage.py collectstatic --settings=pastvina.settings.production
```
