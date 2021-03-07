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


def new(tick: Tick, new_tick: Tick) -> None:
    crops_states = {crop.crop.id: crop for crop in CropMarketHistory.objects.filter(tick=tick).select_related('crop')}
    livestock_states = {ls.livestock.id: ls for ls in LivestockMarketHistory.objects.filter(tick=tick).select_related('livestock')}

    team_states = {team.user.id: team for team in TeamHistory.objects.filter(tick=tick)}
    team_cons_and_prod = {key: {'cons': 0, 'prod': 0} for key in team_states.keys()}

    team_crops = TeamCropHistory.objects.filter(tick=tick)
    TeamCropHistory.objects.bulk_create(apply_aging(team_crops, new_tick))

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
    CropMarketHistory.objects.bulk_create(cpy_to_next_tick(crops_states.values(), new_tick))
    LivestockMarketHistory.objects.bulk_create(cpy_to_next_tick(livestock_states.values(), new_tick))
