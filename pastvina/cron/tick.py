from pastvina.models import Round, Tick


def new_tick(tick: Tick, new_tick: Tick) -> None:
    livestock = Livestock.objects.all()
    crops = Crop.objects.all()

    TeamCropHistory.objects.filter(tick=tick)



