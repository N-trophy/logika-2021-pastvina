from functools import reduce
from math import exp

from pastvina.models import Round, Tick, Livestock, Crop, TeamCropHistory, TeamLivestockHistory, CropMarketHistory, \
    LivestockMarketHistory, TeamHistory


def apply_aging(arr, new_tick):
    for a in arr:
        a.pk = None
        a.age -= 1
        a.tick = new_tick
    return [a for a in arr if a.age > 0]


def cpy_to_next_tick(arr, new_tick):
    for a in arr:
        a.pk = None
        a.tick = new_tick
    return arr


def update_prices(arr, price_field, amount_field, coef_to_price):
    s = reduce(lambda x, y: x + abs(getattr(y, amount_field)), arr, 0)

    vals = [exp(- 1 - getattr(a, amount_field) / (s + 1)) for a in arr]
    exp_s = sum(vals)
    coefs = [len(arr) * v / exp_s for v in vals]

    for i, a in enumerate(arr):
        setattr(a, price_field, coef_to_price(a, coefs[i]))


def new(tick: Tick, new_tick: Tick) -> None:
    crops_states = {crop.crop.id: crop for crop in CropMarketHistory.objects.filter(tick=tick).select_related('crop')}
    livestock_states = {ls.livestock.id: ls for ls in LivestockMarketHistory.objects.filter(tick=tick).select_related('livestock')}

    team_states = {team.user.id: team for team in TeamHistory.objects.filter(tick=tick)}
    team_cons_and_prod = {key: {'cons': 0, 'prod': 0} for key in team_states.keys()}
    team_crop_capacity = {key: tick.round.crop_storage_size for key in team_states.keys()}

    team_crops = TeamCropHistory.objects.filter(tick=tick).order_by('-age')
    team_crops = apply_aging(team_crops, new_tick)
    team_crops_in_storage = []
    for crop in team_crops:
        if crop.age <= crops_states[crop.crop.id].crop.rotting_time:
            amount_stored = min(team_crop_capacity[crop.user.id], crop.amount)
            crop.amount = amount_stored
            team_crop_capacity[crop.user.id] -= amount_stored

        team_crops_in_storage.append(crop)

    TeamCropHistory.objects.bulk_create(team_crops_in_storage)

    team_livestock = TeamLivestockHistory.objects.filter(tick=tick)

    for tls in team_livestock:
        livestock_kind = livestock_states[tls.livestock.id]
        crop_kind = crops_states[livestock_kind.livestock.consumption_type.id]

        cons = tls.amount * livestock_kind.livestock.consumption * crop_kind.current_price_buy
        team_cons_and_prod[tls.user.id]['cons'] += cons

        if tls.age <= tls.livestock.life_time:
            prod = tls.amount * livestock_kind.product_current_price
            team_cons_and_prod[tls.user.id]['prod'] += prod

    team_livestock = [tls for tls in team_livestock if team_cons_and_prod[tls.user.id]['cons'] <= team_states[tls.user.id].money]
    TeamLivestockHistory.objects.bulk_create(apply_aging(team_livestock, new_tick))

    for team_state in team_states.values():
        if team_cons_and_prod[team_state.user.id]['cons'] <= team_state.money:
            team_state.money -= team_cons_and_prod[team_state.user.id]['cons']
            team_state.money += team_cons_and_prod[team_state.user.id]['prod']

    TeamHistory.objects.bulk_create(cpy_to_next_tick([team_state for team_state in team_states.values()], new_tick))

    next_crops_states = cpy_to_next_tick(crops_states.values(), new_tick)
    update_prices(next_crops_states, 'current_price_sell', 'amount_sold',
                  lambda a, coef: a.crop.base_price_sell * coef)
    update_prices(next_crops_states, 'current_price_buy', 'amount_sold',
                  lambda a, coef: a.crop.base_price_buy * coef)
    for crop in next_crops_states:
        crop.amount_sold *= 0.7
    CropMarketHistory.objects.bulk_create(next_crops_states)

    next_livestock_states = cpy_to_next_tick(livestock_states.values(), new_tick)
    update_prices(next_livestock_states, 'current_price_sell', 'amount_sold',
                  lambda a, coef: a.livestock.base_price_sell * coef)
    update_prices(next_livestock_states, 'current_price_buy', 'amount_sold',
                  lambda a, coef: a.livestock.base_price_buy * coef)
    update_prices(next_livestock_states, 'product_current_price', 'product_amount_sold',
                  lambda a, coef: a.livestock.product_price * coef)
    for ls in next_livestock_states:
        ls.amount_sold *= 0.7
        ls.product_amount_sold *= 0.7
    LivestockMarketHistory.objects.bulk_create(next_livestock_states)
