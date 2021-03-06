from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.static import serve
from pastvina.models import Contribution, Crop, Livestock, TeamHistory, LivestockMarketHistory, \
    TeamLivestockHistory
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
    tick = request.GET['tick']
    round_id = request.GET['round']

    """
    Returns a json to update the game state
    """
    money = TeamHistory.objects.filter(round=round_id, tick=tick, user=request.user).last()
    livestock = LivestockMarketHistory.objects.filter(round=round_id, tick=tick).select_related('livestock').all()
    team_livestock = TeamLivestockHistory.objects.filter(round=round_id, tick=tick, user=request.user).values(
        'livestock',
        'age',
        'amount',
    )
    livestock_data = {}
    for ls in livestock:
        livestock_data[ls.livestock.id] = {
            'id': ls.livestock.id,
            'buy': ls.current_price_buy,
            'sell': ls.current_price_sell,
            'product_price': ls.product_current_price,
            'by_age': [0 for _ in range(ls.livestock.life_time + ls.livestock.growth_time + 1)],
        }

    for tls in team_livestock:
        livestock_data[tls['livestock']]['by_age'][tls['age']] = tls['amount']

    data = {
        "money": money,
        "time": int(time.time() * 1000) + 15000,
        "livestock": list(livestock_data.values()),
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
