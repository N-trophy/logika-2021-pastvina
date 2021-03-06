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
    crops_states = CropMarketHistory.objects.filter(tick=tick).select_related('crop')
    CropMarketHistory.objects.bulk_create(cpy_to_next_tick(crops_states, new_tick))

    livestock_states = LivestockMarketHistory.objects.filter(tick=tick).select_related('livestock')
    LivestockMarketHistory.objects.bulk_create(cpy_to_next_tick(livestock_states, new_tick))

    team_states = TeamHistory.objects.filter(tick=tick)
    TeamHistory.objects.bulk_create(cpy_to_next_tick(team_states, new_tick))

    team_crops = TeamCropHistory.objects.filter(tick=tick)
    TeamCropHistory.objects.bulk_create(apply_aging(team_crops, new_tick))

    team_livestock = TeamLivestockHistory.objects.filter(tick=tick)
    TeamLivestockHistory.objects.bulk_create(apply_aging(team_livestock, new_tick))

