from functools import reduce
from math import exp

from pastvina.models import Round, Tick, Livestock, Crop, TeamCropHistory, TeamLivestockHistory, CropMarketHistory, \
    LivestockMarketHistory, TeamHistory


def cpy_to_next_tick(arr, new_tick):
    for a in arr:
        a.pk = None
        a.tick = new_tick
    return arr


def update_prices(dict, current_price_field, amount_sold_field, coef_to_price):
    s = reduce(lambda x, y: x + abs(getattr(y, amount_sold_field)), dict.values(), 0)

    vals = [exp(- 1 - getattr(a, amount_sold_field) / (s + 1)) for a in dict.values()]
    exp_s = sum(vals)
    coefs = [len(dict.values()) * v / exp_s for v in vals]

    for i, a in enumerate(dict.values()):
        setattr(a, current_price_field, coef_to_price(a, coefs[i]))


def new(tick: Tick, new_tick: Tick) -> None:
    """get previous states of market and teams"""

    crops_states = {crop_state.crop_id: crop_state for crop_state in CropMarketHistory
                    .objects.filter(tick=tick).select_related('crop')}
    livestock_states = {ls_state.livestock_id: ls_state for ls_state in LivestockMarketHistory
                        .objects.filter(tick=tick).select_related('livestock')}
    team_states = {team_state.user_id: team_state for team_state in TeamHistory.objects.filter(tick=tick)}

    """reset team state"""
    for team_state in team_states.values():
        team_state.stock_size = 0
        team_state.slaughtered = 0
        team_state.total_consumption = 0

    team_livestock = TeamLivestockHistory.objects.filter(tick=tick)
    for tls in team_livestock:
        livestock = livestock_states[tls.livestock_id].livestock
        crop_state = crops_states[livestock.consumption_type_id]
        team_states[tls.user_id].total_consumption += tls.amount * crop_state.current_price_sell * livestock.consumption

    """filter ids of the teams whose livestock will survive"""
    surviving_teams = [team_states[team_id] for team_id in team_states.keys()
                       if team_states[team_id].total_consumption <= team_states[team_id].money]

    """update teams money by their total consumption"""
    for team_state in surviving_teams:
        team_state.money -= team_states[team_state.user_id].total_consumption

    """get livestock of those teams who survived"""
    team_livestock = TeamLivestockHistory.objects.filter(tick=tick, user__in=[team_state.user_id
                                                                              for team_state in surviving_teams])

    """
    apply production on mature animals (increase team money and the sales counter of the product)
    apply aging on all animals
    """
    for tls in team_livestock:
        ls_state = livestock_states[tls.livestock_id]
        team_state = team_states[tls.user_id]
        consumption_crop_state = crops_states[ls_state.livestock.consumption_type_id]

        if tls.age <= ls_state.livestock.life_time:
            prod = ls_state.product_current_price * tls.amount
            ls_state.product_amount_sold += prod
            team_state.money += prod

        cons = tls.amount * consumption_crop_state.current_price_sell * ls_state.livestock.consumption
        consumption_crop_state.amount_sold -= cons

        tls.age -= 1

    """remove dead animals"""
    team_livestock = [tls for tls in team_livestock if tls.age > 0]

    TeamLivestockHistory.objects.bulk_create(cpy_to_next_tick(team_livestock, new_tick))

    memory = 2

    """
    update livestock prices
    amount_sold contains <amount in last previous step> * <memory> + <amount sold in current tick>
    -> needs to be normalized by (1 + memory)
    """

    for ls_state in livestock_states.values():
        ls_state.amount_sold /= memory + 1
        ls_state.product_amount_sold /= memory + 1
    update_prices(livestock_states, 'current_price_sell', 'amount_sold',
                  lambda a, c: a.livestock.base_price_sell * c)
    update_prices(livestock_states, 'current_price_buy', 'amount_sold',
                  lambda a, c: a.livestock.base_price_buy * c)
    update_prices(livestock_states, 'product_current_price', 'product_amount_sold',
                  lambda a, c: a.livestock.product_price * c)
    for ls_state in livestock_states.values():
        ls_state.amount_sold *= memory
        ls_state.product_amount_sold *= memory

    LivestockMarketHistory.objects.bulk_create(cpy_to_next_tick([ls_state for ls_state in livestock_states.values()],
                                                                new_tick))
    """
    update crop prices
    amount_sold contains <amount in last previous step> * <memory> + <amount sold in current tick>
    -> needs to be normalized by (1 + memory)
    """

    for crop_state in crops_states.values():
        crop_state.amount_sold /= memory + 1
    update_prices(crops_states, 'current_price_sell', 'amount_sold',
                  lambda a, c: a.crop.base_price_sell * c)
    update_prices(crops_states, 'current_price_buy', 'amount_sold',
                  lambda a, c: a.crop.base_price_buy * c)

    CropMarketHistory.objects.bulk_create(cpy_to_next_tick([crop_state for crop_state in crops_states.values()],
                                                           new_tick))
    for crop_state in crops_states.values():
        crop_state.amount_sold *= memory

    """get crop, apply aging and remove a stock surplus"""
    storage_size = tick.round.crop_storage_size
    team_crops = TeamCropHistory.objects.filter(tick=tick).order_by('-age')
    for tc in team_crops:
        crop = crops_states[tc.crop_id].crop
        team_state = team_states[tc.user_id]
        tc.age -= 1
        if 0 < tc.age <= crop.rotting_time:
            team_state.stock_size += tc.amount
            surplus = max(0, team_state.stock_size - storage_size)
            team_state.stock_size -= surplus
            tc.amount -= surplus
    team_crops = [tc for tc in team_crops if tc.amount > 0 and tc.age > 0]

    TeamCropHistory.objects.bulk_create(cpy_to_next_tick(team_crops, new_tick))
    TeamHistory.objects.bulk_create(cpy_to_next_tick([team_state for team_state in team_states.values()],
                                                     new_tick))
