from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F, Prefetch
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.mail import send_mail

from pastvina.models import Contribution, Round, Tick, Crop, Livestock, CropMarketHistory, LivestockMarketHistory, \
    TeamHistory, TeamCropActionHistory, TeamLivestockActionHistory, TeamCropHistory, TeamLivestockHistory


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


def time_check(request):
    """
    Renders the page for checking time with frontend.
    """
    return render(request, 'pastvina/time_check.html', {'navbar_absolute_pos': True,})


def time_check_ping(request):
    """
    Returns the time of request and server time.
    """
    try:
        request_time = int(request.POST.get('request_time'))
    except KeyError:
        return HttpResponseBadRequest('Chybí čas požadavku')

    data = {
        "request_time": request_time,
        "server_time": int(timezone.now().timestamp() * 1000),
    }

    return JsonResponse(data)


@login_required
def page_rules(request):
    """
    Renders the page with rules.
    """
    return render(request, 'pastvina/rules.html', {})


@login_required
def page_game_overview(request):
    """
    Renders the game overview page from template.
    """
    context = {
        'rounds': Round.objects.filter().order_by(F('index').asc(nulls_last=True), 'id').all(),
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
    tick = Tick.objects.filter(round=round_).order_by('index').last()

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
    team_livestock_actions = TeamLivestockActionHistory.objects.filter(tick=tick, user=request.user).values(
        'livestock',
        'bought',
        'sold',
        'killed',
    )

    livestock_data = {}
    for ls in livestock:
        livestock_data[ls.livestock.id] = {
            'id': ls.livestock.id,
            'buy': ls.current_price_buy,
            'sell': ls.current_price_sell,
            'product_price': ls.product_current_price,
            'by_age': [0 for _ in range(ls.livestock.life_time + ls.livestock.growth_time)],
            'bought': 0,
            'sold': 0,
            'killed': 0,
        }

    for tls_action in team_livestock_actions:
        ls_data = livestock_data[tls_action['livestock']]
        if ls_data:
            ls_data['bought'] = tls_action['bought']
            ls_data['sold'] = tls_action['sold']
            ls_data['killed'] = tls_action['killed']

    for tls in team_livestock:
        tls_data = livestock_data[tls['livestock']]
        if tls_data:
            if tls['age'] <= len(tls_data['by_age']):
                tls_data['by_age'][tls['age']-1] = tls['amount']


    crops = CropMarketHistory.objects.filter(tick=tick).select_related('crop').all()
    team_crops = TeamCropHistory.objects.filter(tick=tick, user=request.user).values(
        'crop',
        'age',
        'amount',
    )
    team_crop_actions = TeamCropActionHistory.objects.filter(tick=tick, user=request.user).values(
        'crop',
        'bought',
        'sold',
    )

    crops_data = {}
    for crop in crops:
        crops_data[crop.crop.id] = {
            'id': crop.crop.id,
            'buy': crop.current_price_buy,
            'sell': crop.current_price_sell,
            'by_age': [0 for _ in range(crop.crop.rotting_time + crop.crop.growth_time)],
            'bought': 0,
            'sold': 0,
        }

    for tcrop_action in team_crop_actions:
        crop_data = crops_data[tcrop_action['crop']]
        if crop_data:
            crop_data['bought'] = tcrop_action['bought']
            crop_data['sold'] = tcrop_action['sold']

    for tcrop in team_crops:
        tcrop_data = crops_data[tcrop['crop']]
        if tcrop_data:
            if tcrop['age'] <= len(tcrop_data['by_age']):
                tcrop_data['by_age'][tcrop['age']-1] = tcrop['amount']

    if round_.reload_time:
        reload_time = int(max(round_.start, round_.reload_time).timestamp() * 1000)
    else:
        reload_time = int(round_.start.timestamp() * 1000)

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


def game_buy(commodity_state, commodity, max_age, last_tick, user_state, count, get_or_create):
    total_price = commodity_state.current_price_buy * count
    if total_price > user_state.money:
        return HttpResponseBadRequest('Nemáte dostatek peněz.')

    c, _ = get_or_create(last_tick, user_state.user, commodity, max_age)
    c.amount += count
    c.save()

    # commodity_state.amount_sold -= total_price
    # commodity_state.save()
    user_state.money -= total_price
    user_state.save()
    return HttpResponse("Obchod uskutečněn.")


def game_sell(commodity_state, active_time, last_tick, user_state, count, klass, query):
    total_price = commodity_state.current_price_sell * count
    by_age = query.filter(tick=last_tick, user=user_state.user, age__lte=active_time).order_by('age')
    rest = count
    pos = 0
    while rest > 0:
        if pos >= len(by_age):
            return HttpResponseBadRequest('Nemáte dostatek komodity na prodej.')
        a = min(by_age[pos].amount, rest)
        by_age[pos].amount -= a
        rest -= a
        pos += 1
    klass.objects.bulk_update(by_age, ['amount'])
    user_state.money += total_price
    user_state.save()
    commodity_state.amount_sold += total_price
    commodity_state.save()
    return HttpResponse("Obchod uskutečněn.")


def game_trade_crop(trade_type, count, prod_id, last_tick, user_state):
    lock, _ = TeamCropActionHistory.objects.get_or_create(tick=last_tick, user=user_state.user, crop_id=prod_id)
    try:
        crop_state = CropMarketHistory.objects.filter(tick=last_tick, crop=prod_id).select_related('crop').get()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(f"Plodina nenalezena. (tick {last_tick.index})")
    crop = crop_state.crop

    if trade_type == 'buy':
        if lock.bought != 0:
            return HttpResponseBadRequest("Tuto iteraci jste již nakoupili tuto komoditu.")
        get_or_create = lambda tick, user, crop, age: TeamCropHistory.objects.get_or_create(
            tick=tick, user=user, crop=crop, age=age,
        )
        response = game_buy(crop_state, crop, crop.growth_time + crop.rotting_time,
                        last_tick, user_state, count, get_or_create)
        if response.status_code == 200:
            lock.bought = count
            lock.save()
        return response
    elif trade_type == 'sell':
        if lock.sold != 0:
            return HttpResponseBadRequest("Tuto iteraci jste již prodali tuto komoditu.")
        response = game_sell(crop_state, crop.rotting_time, last_tick, user_state, count,
                         TeamCropHistory, TeamCropHistory.objects.filter(crop=crop))
        if response.status_code == 200:
            lock.sold = count
            lock.save()
        return response
    else:
        return HttpResponseBadRequest('Neznámý typ obchodu.')


def game_trade_livestock(trade_type, count, prod_id, last_tick, user_state):
    lock, _ = TeamLivestockActionHistory.objects.get_or_create(tick=last_tick, user=user_state.user,
                                                               livestock_id=prod_id)
    try:
        ls_state = LivestockMarketHistory.objects.filter(tick=last_tick, livestock=prod_id) \
            .select_related('livestock').get()
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(f"Dobytek nenalezen. (tick {last_tick.index})")
    ls = ls_state.livestock

    if trade_type == 'buy':
        if lock.bought != 0:
            return HttpResponseBadRequest("Tuto iteraci jste již nakoupili tuto komoditu.")
        get_or_create = lambda tick, user, ls, age: TeamLivestockHistory.objects.get_or_create(
            tick=tick,
            user=user,
            livestock=ls,
            age=age,
        )
        response = game_buy(ls_state, ls, ls.growth_time + ls.life_time,
                        last_tick, user_state, count, get_or_create)
        if response.status_code == 200:
            lock.bought = count
            lock.save()
        return response
    elif trade_type == 'sell':
        if lock.sold != 0:
            return HttpResponseBadRequest("Tuto iteraci jste již prodali tuto komoditu.")
        if last_tick.round.livestock_slaughter_limit < user_state.slaughtered + count:
            return HttpResponseBadRequest(f'Příliš mnoho poražených zvířat.\n'
                                          f'Limit na iteraci je {last_tick.round.livestock_slaughter_limit}.\n'
                                          f'Již jste porazili {user_state.slaughtered} kusů.')

        response = game_sell(ls_state, ls.life_time, last_tick, user_state, count,
                             TeamLivestockHistory, TeamLivestockHistory.objects.filter(livestock=ls))

        if response.status_code == 200:
            lock.sold = count
            lock.save()
            user_state.slaughtered += count
            user_state.save()
        return response
    elif trade_type == 'kill' or trade_type == 'kill_youngest':
        if lock.killed == 1:
            return HttpResponseBadRequest("Tuto iteraci jste již utratili toto zvíře.")
        by_age = TeamLivestockHistory.objects.filter(tick=last_tick, livestock=ls, user=user_state.user) \
            .order_by('age' if trade_type == 'kill' else '-age')
        rest = count
        for pos in range(len(by_age)):
            if rest <= 0:
                break
            a = min(by_age[pos].amount, rest)
            by_age[pos].amount -= a
            rest -= a
        TeamLivestockHistory.objects.bulk_update(by_age, ['amount'])
        response = HttpResponse("Zvířata utracena.")
        if response.status_code == 200:
            lock.killed = 1
            lock.save()
        return response
    else:
        return HttpResponseBadRequest('Neznámý druh obchodu.')

@login_required
@transaction.atomic
def game_trade(request, round_id):
    """ DATA VALIDATION"""
    try:
        tick_id = int(request.POST['tick_id'])
        trade_type = request.POST['trade_type']
        prod_type = request.POST['prod_type']
        prod_id = int(request.POST['prod_id'])
        count = int(request.POST['count'])
    except KeyError:
        return HttpResponseBadRequest('Trade parameter missing')

    last_tick = Tick.objects.filter(round_id=round_id).order_by('index').select_related('round').last()
    if last_tick is None:
        return HttpResponseNotFound("Kolo neexistuje nebo neobsahuje iteraci.")
    round_ = last_tick.round

    if count <= 0:
        return HttpResponseBadRequest("Nelze obchodovat záporné množství.")

    if tick_id != last_tick.id:
        return HttpResponseBadRequest("Již nastala další iterace.")

    """ TRADE """
    user_state = TeamHistory.objects.filter(tick=last_tick, user=request.user).select_related('user').last()
    if user_state is None:
        return HttpResponseBadRequest("Nebylo možné nalézt data teamu.")

    if prod_type == 'crop':
        return game_trade_crop(trade_type, count, prod_id, last_tick, user_state)

    elif prod_type == 'ls':
        return game_trade_livestock(trade_type, count, prod_id, last_tick, user_state)
    else:
        return HttpResponseBadRequest("Neznámý typ zboží.")


@login_required
def statistics(request, round_id):
    """
    Renders the statistics page from template.
    """
    round = Round.objects.filter(id=round_id).last()
        # .prefetch_related('all_ticks')\
        # .prefetch_related('all_ticks__crop_states')\
        # .prefetch_related('all_ticks__livestock_states')\
        # .values(Prefetch('all_ticks__crop_states__current_price_sell', to_attr))

    if round is None:
        return HttpResponseNotFound("Dané kolo neexistuje")

    crops = Crop.objects.prefetch_related(
        Prefetch('states', CropMarketHistory.objects.filter(tick__round=round).order_by('tick'))
    ).all()
    livestock = Livestock.objects.prefetch_related(
        Prefetch('states', LivestockMarketHistory.objects.filter(tick__round=round).order_by('tick'))
    ).all()

    # for tick in round.all_ticks.order_by('index').all():
    #     for crop_state in tick.crop_states.all():
    #         crop
        # crop.data_prices = [tick.crop_states.filter(crop=crop).last() for tick in round.all_ticks.all()]

    context = {
        'ticks': round.all_ticks,
        'crops': crops,
        'livestock': livestock,
    }

    return render(request, 'pastvina/game_statistics.html', context)


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


def user_activate(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        user = User.objects.filter(username=username).last()

        if user is None:
            messages.error(request, "Takový uživatel neexistuje")
            return render(request, 'pastvina/user_activate.html', {'navbar_absolute_pos': True})

        if user.is_superuser and (not request.user or not request.user.is_superuser):
            messages.error(request, "Tohoto uživatele nelze změnit")
            return render(request, 'pastvina/user_activate.html', {'navbar_absolute_pos': True})

        if user.is_active:
            messages.error(request, "Tento uživatel již byl aktivován.")
            return render(request, 'pastvina/user_activate.html', {'navbar_absolute_pos': True})

        user.is_active = True
        user.pwd = (User.objects.make_random_password(), )
        user.set_password(user.pwd[0])
        user.save()

        send_mail(
            f'[N-trophy 2021] Logika: přístupové údaje',
            (f'Přístupové údaje k webu https://logika.ntrophy.cz/ pro tým {user.get_full_name()} '
             f'jsou:\n\n  * login: {user.username} \n  * heslo: {user.pwd[0]}\n\nS pozdravem,\n'
             f'tým logiky N-trophy'),
            'logika@ntrophy.cz',
            [user.email],
        )

        messages.info(request, f"Uživatel { user.get_full_name() } (login id { user.username }) byl aktivován.")
        messages.info(request, f"Na adresu { user.email } byly odeslány přihlašovací údaje.")

        return render(request, 'pastvina/user_activate.html', {'navbar_absolute_pos': True})
    else:
        return render(request, "pastvina/user_activate.html", {'navbar_absolute_pos': True})
