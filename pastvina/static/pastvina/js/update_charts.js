var tick_id = 0
var round_id = 0

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
        $.getJSON("/game/update", function(update_data) {
            update_charts(update_data);
        })
        .fail(function(){
            console.log("Could not update chart data");
        });
    }
}


var cropAgeCharts = new Map();
var livestockAgeCharts = new Map();

function update_charts(updateData) {
    console.log(updateData);

    document.getElementById("game-money").innerHTML = updateData.money;
    timeOfNextTick = updateData.time;
    tick_id = updateData.tick_id;
    round_id = updateData.round_id;

    for (crop of updateData.crops) {
        $(".crop-buy-price-" + crop.id).text(crop.buy);
        $(".crop-sell-price-" + crop.id).text(crop.sell);

        let ageChart = cropAgeCharts[crop.id];
        for (var i = 0; i < crop.by_age.length; i++) {
            ageChart.data.labels[i] = "týden "+i
        }
        ageChart.data.datasets[0].data = crop.by_age;
        ageChart.update();
    }

    for (ls of updateData.livestock) {
        $(".ls-buy-price-" + ls.id).text(ls.buy);
        $(".ls-sell-price-" + ls.id).text(ls.sell);
        $(".ls-product-price-" + ls.id).text(ls.product_price);

        let ageChart = livestockAgeCharts[ls.id];
        ageChart.data.labels = new Array()
        for (var i = 0; i < ls.by_age.length; i++) {
            ageChart.data.labels[i] = "týden "+i
        }
        ageChart.data.datasets[0].data = ls.by_age;
        ageChart.update();
    }
}
