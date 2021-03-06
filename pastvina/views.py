from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.static import serve
from pastvina.models import Contribution, Crop, Livestock
from pastvina.templatetags.extras import markdown_to_html
import time


@login_required
def page_index(request):
    """
    Renders the index page from template.

    template: pastvina/index.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    contribs = Contribution.public_objects().order_by('-public_from')[:5]
    return render(request, 'pastvina/index.html', {
        'contribs': contribs,
        'navbar_absolute_pos': True,
    })


def page_login(request):
    """
    POST: Logs a user in and redirects to 'index' or reponses HttpResponseBadRequest if data are invalid.

    GET: Renders a login form.

    Template: seminar_contest/login.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            if request.GET.get('text_only'):
                return HttpResponseBadRequest('Přihlašovací jméno nebo heslo není správné.')
            else:
                messages.error(request, 'Přihlašovací jméno nebo heslo není správné.')
                return render(request, "pastvina/login.html", {'navbar_absolute_pos': True})
    else:
        return render(request, "pastvina/login.html", {'navbar_absolute_pos': True})


@login_required
def page_game(request):
    """
    Renders the game page from template.

    template: pastvina/game.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """

    crops = Crop.objects.all()
    livestock = Livestock.objects.all()

    return render(request, 'pastvina/game.html', {'crops': crops, 'livestock': livestock})

@login_required
def game_update(request):
    """
    Returns a json to update the game state
    """
    data = {
        "money": 100,
        "time": int(time.time() * 1000) + 30000,
        "livestock": [
            {
                "name": "Tučňáci",
                "id": 1,
                "buy": 100,
                "sell": 100,
                "production": [4, 2]
            },
            {
                "name": "Kozy",
                "id": 2,
                "buy": 50,
                "sell": 70,
                "production": [0, 2, 4]
            }
        ],
        "crops": [
            {
                "name": "Melouny",
                "id": 1,
                "buy": 10,
                "sell": 10,
                "production": [0, 4, 3, 5],
                "storage": [2, 5, 4, 0]
            },
            {
                "name": "Oves",
                "id": 2,
                "buy": 5,
                "sell": 4,
                "production": [0, 1, 2, 3, 4, 8],
                "storage": [4, 5, 6]
            }
        ]
    }

    return JsonResponse(data)

@login_required
def handler_logout(request):
    """
    Logs a user out and redirects to 'index'.

    Privacy policy: LOGIN_REQUIRED

    :param request: HTTP request
    :return: HTTP response
    """
    logout(request)
    return redirect('/')


def handler_markdown_to_html(request):
    text = request.body.decode('utf-8')
    html = markdown_to_html(text)
    return HttpResponse(html)
