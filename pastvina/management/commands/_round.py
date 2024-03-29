from django.contrib.auth.models import User
from pastvina.models import Round, Tick, Livestock, Crop, TeamHistory, \
    CropMarketHistory, LivestockMarketHistory


def new(round: Round, init_tick: Tick) -> None:
    teams = User.objects.all()
    livestock = Livestock.objects.all()
    crops = Crop.objects.all()

    team_history_set = [
        TeamHistory(user=team, tick=init_tick, money=round.start_money)
        for team in teams
    ]

    crop_market_history = [
        CropMarketHistory(tick=init_tick, crop=crop, amount_sold=0,
                          current_price_buy=crop.base_price_buy, current_price_sell=crop.base_price_sell)
        for crop in crops
    ]

    livestock_market_history = [
        LivestockMarketHistory(tick=init_tick, livestock=ls, amount_sold=0,
                               current_price_buy=ls.base_price_buy, current_price_sell=ls.base_price_sell,
                               product_amount_sold=0, product_current_price=ls.product_price)
        for ls in livestock
    ]

    TeamHistory.objects.bulk_create(team_history_set)
    CropMarketHistory.objects.bulk_create(crop_market_history)
    LivestockMarketHistory.objects.bulk_create(livestock_market_history)
