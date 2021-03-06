from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from pastvina.models import Contribution, Crop, Livestock, TeamHistory, LivestockMarketHistory, \
    TeamLivestockHistory, CropMarketHistory, TeamCropHistory, Round, Tick
from pastvina.templatetags.extras import markdown_to_html


@login_required
def page_index(request):
    """
    Renders the index page from template.

    template: pastvina/index.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    contribs = Contribution.objects.filter(published=True).order_by('-public_from')[:5]
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
    context =  {'crops': crops, 'livestock': livestock}

    if 'round' in request.GET:
        context['round'] = get_object_or_404(Round, id=request.GET['round'])

    return render(request, 'pastvina/game.html', context)


@login_required
def game_update(request):
    """
    Returns a json to update the game state
    """
    tick = Tick.objects.last()

    team_history = TeamHistory.objects.filter(tick=tick, user=request.user).last()
    if team_history:
        money = team_history.money
    livestock = LivestockMarketHistory.objects.filter(tick=tick).select_related('livestock').all()
    team_livestock = TeamLivestockHistory.objects.filter(tick=tick, user=request.user).values(
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
        if livestock_data[tls['livestock']]:
            livestock_data[tls['livestock']]['by_age'][tls['age']] = tls['amount']

    crops = CropMarketHistory.objects.filter(tick=tick).select_related('crop').all()
    team_crops = TeamCropHistory.objects.filter(tick=tick, user=request.user).values(
        'crop',
        'age',
        'amount',
    )
    crops_data = {}
    for crop in crops:
        crops_data[crop.crop.id] = {
            'id': crop.crop.id,
            'buy': crop.current_price_buy,
            'sell': crop.current_price_sell,
            'by_age': [0 for _ in range(crop.crop.rotting_time + crop.crop.growth_time + 1)],
        }

    for tcrop in team_crops:
        if crops_data[tcrop['crop']]:
            crops_data[tcrop['crop']]['by_age'][tcrop['age']] = tcrop['amount']

    data = {
        "tick_id": tick.id,
        "time": int(tick.start.timestamp() * 1000) + tick.round.period * 10000,
        "money": money,
        "livestock": list(livestock_data.values()),
        "crops": list(crops_data.values()),
    }

    data['time'] = int(timezone.now().timestamp() * 1000) + 30000  # TODO remove when new ticks are added automatically

    return JsonResponse(data)

@login_required
def game_trade(request):
    if 'tick_id'    not in request.GET \
    or 'trade_type' not in request.GET \
    or 'prod_type'  not in request.GET \
    or 'prod_id'    not in request.GET \
    or 'count'      not in request.GET:
        return HttpResponse(request, status=404)

    tick_id = int(request.GET['tick_id'])
    trade_type = request.GET['trade_type']
    prod_type = request.GET['prod_type']
    prod_id = int(request.GET['prod_id'])
    count = int(request.GET['count'])

    if count <= 0:
        return HttpResponse(request, status=404)

    if tick_id != Tick.objects.last().id:
        return HttpResponse(request, status=404)

    if prod_type == 'crop':
        crop = Crop.objects.filter(id=prod_id).last()
        if crop is None:
            return HttpResponse(request, status=404)

        if trade_type == 'buy':
            pass  # TODO
        elif trade_type == 'sell':
            pass  # TODO
        else:
            return HttpResponse(request, status=404)
    elif prod_type == 'ls':
        ls = Livestock.objects.filter(id=prod_id).last()
        if ls is None:
            return HttpResponse(request, status=404)

        if trade_type == 'buy':
            pass  # TODO
        elif trade_type == 'sell':
            pass  # TODO
        elif trade_type == 'kill':
            pass  # TODO
        else:
            return HttpResponse(request, status=404)
    else:
        return HttpResponse(request, status=404)

    return HttpResponse(request, status=204)


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
