from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from pastvina.models import Contribution, Crop, Livestock, TeamHistory, LivestockMarketHistory, \
    TeamLivestockHistory, CropMarketHistory, TeamCropHistory, Round, Tick


@login_required
def page_index(request):
    """
    Renders the index page from template.

    template: pastvina/index.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    contribs = Contribution.objects.filter(published=True).filter(public_from__lte=timezone.now()).order_by('-public_from')[:5]
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
def page_rules(request):
    """
    Page with rules.
    """
    return render(request, 'pastvina/rules.html', {})


@login_required
def page_game_overview(request):
    """
    Renders the game overview page from template.
    """
    real_rounds = Round.objects.filter(is_test=False).all()
    test_rounds = Round.objects.filter(is_test=True).all()

    context = {
        'real_rounds': real_rounds,
        'test_rounds': test_rounds,
    }

    return render(request, 'pastvina/game_overview.html', context)


@login_required
def page_game(request, round_id):
    """
    Renders the game page from template.

    template: pastvina/game.html

    Privacy policy: PUBLIC

    :param request: HTTP request
    :return: HTTP response
    """
    crops = Crop.objects.all()
    livestock = Livestock.objects.all()
    round_ = Round.objects.filter(id=round_id).last()
    context = {
        'crops': crops,
        'livestock': livestock,
        'round': round_
    }

    # Prevent endless empty requests from frontend
    if round_ is None:
        return HttpResponseNotFound("Dané kolo neexistuje")

    return render(request, 'pastvina/game.html', context)


@login_required
def game_update(request, round_id):
    """
    Returns a json to update the game state
    """
    round_ = Round.objects.filter(id=round_id).last()
    tick = Tick.objects.filter(round=round_).last()

    if round_ is None:
        return HttpResponseNotFound("Neexistuje kolo s daným id")
    if tick is None:
        return HttpResponseNotFound("V daném kole neexistuje iterace")

    team_history = TeamHistory.objects.filter(tick=tick, user=request.user).last()
    money = None
    slaughtered = None
    if team_history:
        money = team_history.money
        slaughtered = team_history.slaughtered
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
            'by_age': [0 for _ in range(ls.livestock.life_time + ls.livestock.growth_time)],
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
            'by_age': [0 for _ in range(crop.crop.rotting_time + crop.crop.growth_time)],
        }

    for tcrop in team_crops:
        if crops_data[tcrop['crop']]:
            crops_data[tcrop['crop']]['by_age'][tcrop['age']] = tcrop['amount']

    if round_.reload_time:
        reload_time = int(max(round_.start, round_.reload_time).timestamp() * 1000)
    else:
        reload_time = int(tick.start.timestamp() * 1000)

    data = {
        "tick_id": tick.id,
        "tick_index": tick.index,
        "time": int(tick.start.timestamp() * 1000) + round_.period * 10000,
        "money": money,
        "slaughtered": slaughtered,
        "livestock": list(livestock_data.values()),
        "crops": list(crops_data.values()),
        "reload_time": reload_time,
    }

    return JsonResponse(data)


@login_required
@transaction.atomic
def game_trade(request, round_id):
    round_ = Round.objects.filter(id=round_id).last()
    last_tick = Tick.objects.filter(round=round_).last()
    if round_ is None:
        return HttpResponseNotFound("Neexistuje kolo s daným id")
    if last_tick is None:
        return HttpResponseNotFound("V daném kole neexistuje iterace")

    if 'tick_id'    not in request.GET \
    or 'trade_type' not in request.GET \
    or 'prod_type'  not in request.GET \
    or 'prod_id'    not in request.GET \
    or 'count'      not in request.GET:
        return HttpResponseBadRequest("Chybí parametr nákupu.")

    tick_id = int(request.GET['tick_id'])
    trade_type = request.GET['trade_type']
    prod_type = request.GET['prod_type']
    prod_id = int(request.GET['prod_id'])
    count = int(request.GET['count'])

    if count <= 0:
        return HttpResponseBadRequest("Nelze obchodovat záporné množství.")

    if tick_id != last_tick.id:
        return HttpResponseBadRequest("Nákup uskutečněn v již uplynulé iteraci.")

    user_state = TeamHistory.objects.get(tick=last_tick, user=request.user)

    if prod_type == 'crop':
        crop = CropMarketHistory.objects.filter(crop=prod_id, tick=last_tick).select_related('crop').last()
        if crop is None:
            return HttpResponseBadRequest(f"Plodina nenalezena. (tick {last_tick.index})")

        if trade_type == 'buy':
            total_price = crop.current_price_buy * count
            if total_price > user_state.money:
                return HttpResponseBadRequest('Nemáte dostatek peněz.')
            max_age = crop.crop.growth_time + crop.crop.rotting_time - 1
            c, _ = TeamCropHistory.objects.get_or_create(
                tick=last_tick,
                user=request.user,
                crop=crop.crop,
                age=max_age,
                defaults={'amount': 0}
            )
            c.amount += count
            c.save()
            crop.amount_sold -= total_price
            crop.save()
            user_state.money -= total_price
            user_state.save()
            return HttpResponse("Obchod uskutečněn.")
        elif trade_type == 'sell':
            total_price = crop.current_price_sell * count
            by_age = TeamCropHistory.objects.filter(tick=last_tick, crop=crop.crop,
                                                    user=request.user, age__lt=crop.crop.rotting_time).order_by('age')
            rest = count
            pos = 0
            while rest > 0:
                if pos >= len(by_age):
                    return HttpResponseBadRequest('Nemáte dostatek plodin.')
                a = min(by_age[pos].amount, rest)
                by_age[pos].amount -= a
                rest -= a
                pos += 1
            TeamCropHistory.objects.bulk_update(by_age, ['amount'])
            user_state.money += total_price
            user_state.save()
            crop.amount_sold += total_price
            crop.save()
            return HttpResponse("Obchod uskutečněn.")
        else:
            return HttpResponseBadRequest('Neznámý typ obchodu.')
    elif prod_type == 'ls':
        ls = LivestockMarketHistory.objects.filter(livestock=prod_id).select_related('livestock').last()
        if ls is None:
            return HttpResponseBadRequest(f"Dobytek nenalezen. (tick {last_tick.index})")

        if trade_type == 'buy':
            total_price = ls.current_price_buy * count
            if total_price > user_state.money:
                return HttpResponseBadRequest('Nemáte dostatek peněz.')
            max_age = ls.livestock.growth_time + ls.livestock.life_time - 1
            c, _ = TeamLivestockHistory.objects.get_or_create(
                tick=last_tick,
                user=request.user,
                livestock=ls.livestock,
                age=max_age,
                defaults={'amount': 0}
            )
            c.amount += count
            c.save()
            user_state.money -= total_price
            user_state.save()
            ls.amount_sold -= total_price
            ls.save()
            return HttpResponse("Obchod uskutečněn.")
        elif trade_type == 'sell':
            total_price = ls.current_price_sell * count
            if round_.livestock_slaughter_limit < user_state.slaughtered + count:
                return HttpResponseBadRequest(f'Příliš mnoho poražených zvířat.\n'
                                              f'Limit na iteraci je {round_.livestock_slaughter_limit}.\n'
                                              f'Již jste porazili {user_state.slaughtered} kusů.')

            by_age = TeamLivestockHistory.objects.filter(tick=last_tick, livestock=ls.livestock, user=request.user,
                                                    age__lt=ls.livestock.life_time).order_by('age')
            rest = count
            pos = 0
            while rest > 0:
                if pos >= len(by_age):
                    return HttpResponseBadRequest('Nemáte dostatek dobytka.')
                a = min(by_age[pos].amount, rest)
                by_age[pos].amount -= a
                rest -= a
                pos += 1
            TeamLivestockHistory.objects.bulk_update(by_age, ['amount'])
            user_state.money += total_price
            user_state.slaughtered += count
            user_state.save()
            ls.amount_sold += total_price
            ls.save()
            return HttpResponse("Obchod uskutečněn.")
        elif trade_type == 'kill':
            by_age = TeamLivestockHistory.objects.filter(tick=last_tick, livestock=ls.livestock, user=request.user).order_by('age')
            rest = count
            for pos in range(len(by_age)):
                if rest <= 0:
                    break
                a = min(by_age[pos].amount, rest)
                by_age[pos].amount -= a
                rest -= a
            TeamLivestockHistory.objects.bulk_update(by_age, ['amount'])
            return HttpResponse("Zvířata utracena.")
        else:
            return HttpResponseBadRequest('Neznámý druh obchodu.')
    else:
        return HttpResponseBadRequest("Neznámý typ zboží.")


@login_required
def statistics(request, round_id):
    """
    Renders the statistics page from template.
    """
    round_ = Round.objects.filter(id=round_id).last()

    if round_ is None:
        return HttpResponseNotFound("Dané kolo neexistuje")

    return HttpResponseNotFound("Daná stránka zatím neexistuje")


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
