var tickId = 0

var timeOfNextTick = Date.now();

function updateTimeToNextTick()
{
    let millisToNextTick = timeOfNextTick - Date.now();
    if (millisToNextTick > 0)
    {
        document.getElementById("tick-countdown").innerHTML = Math.floor(millisToNextTick/1000);
    }
    else
    {
        requestUpdateCharts();
    }
}

function requestUpdateCharts() {
    $.getJSON("/game/update", function(update_data) {
        updateCharts(update_data);
    })
    .fail(function(){
        console.log("Could not update chart data");
    });
}

var cropAgeCharts = new Object();
var livestockAgeCharts = new Object();
var cropSellTime = new Object();
var livestockSellTime = new Object();
var livestockMaxSell = Infinity;

function updateCharts(updateData) {
    console.log(updateData);

    $("#game-money").text(updateData.money);
    timeOfNextTick = updateData.time;
    tickId = updateData.tick_id;

    for (crop of updateData.crops) {
        $(".crop-buy-price-" + crop.id).text(crop.buy);
        $(".crop-sell-price-" + crop.id).text(crop.sell);

        let ageChart = cropAgeCharts[crop.id];
        for (let i = 0; i < crop.by_age.length; i++) {
            ageChart.data.labels[i] = "týden "+i
        }
        ageChart.data.datasets[0].data = crop.by_age;
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/crop.buy);
        let maxSell = crop.by_age.slice(0, cropSellTime[crop.id]).reduce((a, b) => a + b, 0);
        $("#buy-crop-count-" + crop.id).attr({ "max": maxBuy });
        $("#sell-crop-count-" + crop.id).attr({ "max": maxSell });
    }

    for (ls of updateData.livestock) {
        $(".ls-buy-price-" + ls.id).text(ls.buy);
        $(".ls-sell-price-" + ls.id).text(ls.sell);
        $(".ls-product-price-" + ls.id).text(ls.product_price);

        let ageChart = livestockAgeCharts[ls.id];
        ageChart.data.labels = new Array()
        for (let i = 0; i < ls.by_age.length; i++) {
            ageChart.data.labels[i] = "týden "+i
        }
        ageChart.data.datasets[0].data = ls.by_age;
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/ls.buy);
        let maxSell = Math.min(livestockMaxSell, ls.by_age.slice(0, livestockSellTime[ls.id]).reduce((a, b) => a + b, 0));
        let maxKill = ls.by_age.reduce((a, b) => a + b, 0);
        $("#buy-ls-count-" + ls.id).attr({ "max": maxBuy });
        $("#sell-ls-count-" + ls.id).attr({ "max": maxSell });
        $("#kill-ls-count-" + ls.id).attr({ "max": maxKill });
    }
}
