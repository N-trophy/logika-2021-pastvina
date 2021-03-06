from pastvina.models import Round, Tick, Livestock, Crop, TeamCropHistory


def new(tick: Tick, new_tick: Tick) -> None:
    livestock = Livestock.objects.all()
    crops = Crop.objects.all()

    # TeamCropHistory.objects.filter(tick=tick)



