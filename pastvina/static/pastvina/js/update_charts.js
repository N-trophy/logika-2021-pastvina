var tickId = 0;
var timeOfNextUpdate = Date.now();
var showTime = false;
var loadTime = Date.now();

function updateTimeToNextTick()
{
    let millisToNextUpdate = timeOfNextUpdate - Date.now();
    if (millisToNextUpdate <= 0)
    {
        timeOfNextUpdate = Date.now() + 5000;
        showTime = false;
        requestUpdateCharts();
    }

    if (showTime) {
        $("#tick-countdown").text(Math.floor(millisToNextUpdate/1000));
    }
    else {
        $("#tick-countdown").text("-");
    }
}

function requestUpdateCharts() {
    $.getJSON("update", function(update_data) {
        updateCharts(update_data);
    })
    .fail(function(error){
        console.log("Nebylo možné obnovit data.\n" + error.responseText);
    });
}

function getReversedData(dataArray, dataSize, defaultValue=0) {
    let reversedData = dataArray.slice(0, dataSize);
    for (let i = reversedData.length; i < dataSize; i++) {
        reversedData.push(defaultValue);
    }
    return reversedData.reverse();
}

var cropAgeCharts = new Object();
var livestockAgeCharts = new Object();
var cropSellTime = new Object();
var livestockSellTime = new Object();
var livestockSellLimit = Infinity;
var currentlySold = 0;

function updateCharts(updateData) {
    console.log(updateData);
    if (updateData.reload_time && updateData.reload_time > loadTime && updateData.reload_time < Date.now()) {
        location.reload();
    }

    currentlySold = updateData.slaughtered;
    $("#game-money").text((updateData.money === null) ? "-" : updateData.money);
    $(".ls-sell-limit").text(livestockSellLimit - currentlySold);
    if (updateData.time > Date.now()) {
        timeOfNextUpdate = updateData.time;
        showTime = true;
        updateTimeToNextTick();
    }
    tickId = updateData.tick_id;
    $("#tick-index").text((updateData.tick_index === null) ? "-" : updateData.tick_index)

    let crop_rotting_ammount = 0;
    let next_tick_new_rotting = 0;
    for (crop of updateData.crops) {
        $(".crop-buy-price-" + crop.id).text(crop.buy);
        $(".crop-sell-price-" + crop.id).text(crop.sell);

        let ageChart = cropAgeCharts[crop.id];
        // ageChart.data.labels = new Array();
        // for (let i = 0; i < crop.by_age.length; i++) {
        //     ageChart.data.labels[i] = "týden " + i;
        // }
        ageChart.data.datasets[0].data = getReversedData(crop.by_age, ageChart.data.labels.length);
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/crop.buy);
        let maxSell = crop.by_age.slice(0, cropSellTime[crop.id]).reduce((a, b) => a + b, 0);
        crop_rotting_ammount += maxSell;
        if (cropSellTime[crop.id] < crop.by_age.length) {
            next_tick_new_rotting += crop.by_age[cropSellTime[crop.id]];
        }
        $("#buy-crop-count-" + crop.id).attr({ "max": maxBuy });
        $("#sell-crop-count-" + crop.id).attr({ "max": maxSell });
    }
    $("#crop-rotting-amount").text(crop_rotting_ammount);
    $("#next-tick-new-rotting").text(next_tick_new_rotting);

    for (ls of updateData.livestock) {
        $(".ls-buy-price-" + ls.id).text(ls.buy);
        $(".ls-sell-price-" + ls.id).text(ls.sell);
        $(".ls-product-price-" + ls.id).text(ls.product_price);

        let ageChart = livestockAgeCharts[ls.id];
        // ageChart.data.labels = new Array();
        // for (let i = 0; i < ls.by_age.length; i++) {
        //     ageChart.data.labels[i] = "týden " + i;
        // }
        ageChart.data.datasets[0].data = getReversedData(ls.by_age, ageChart.data.labels.length);
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/ls.buy);
        let maxSell = Math.min(livestockSellLimit - currentlySold, ls.by_age.slice(0, livestockSellTime[ls.id]).reduce((a, b) => a + b, 0));
        let maxKill = ls.by_age.reduce((a, b) => a + b, 0);
        $("#buy-ls-count-" + ls.id).attr({ "max": maxBuy });
        $("#sell-ls-count-" + ls.id).attr({ "max": maxSell });
        $("#kill-ls-count-" + ls.id).attr({ "max": maxKill });
    }
}
