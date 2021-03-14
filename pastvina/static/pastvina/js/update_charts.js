$.ajaxSetup({timeout:1000});

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

function getItemById(arr, id) {
    for (let i = 0; i < arr.length; i++) {
        if (arr[i].id == id) {
            return arr[i];
        }
    }
}

var cropAgeCharts = new Object();
var livestockAgeCharts = new Object();
var cropSellTime = new Object();
var livestockSellTime = new Object();
var livestockConsumption = new Object();
var livestockSellLimit = Infinity;
var cropStorageSize = Infinity;

function updateCharts(updateData) {
    console.log(updateData);
    if (updateData.reload_time && updateData.reload_time > loadTime && updateData.reload_time < Date.now()) {
        location.reload();
    }

    let currentlySold = updateData.slaughtered;
    $("#game-money").text((updateData.money === null) ? "-" : updateData.money);
    $("#ls-sold-amount").text(currentlySold);
    $(".ls-sell-limit").text(livestockSellLimit - currentlySold);
    if (updateData.time > Date.now()) {
        timeOfNextUpdate = updateData.time;
        showTime = true;
        updateTimeToNextTick();
    }
    tickId = updateData.tick_id;
    $("#tick-index").text((updateData.tick_index === null) ? "-" : updateData.tick_index)

    let cropRottingAmmount = 0;
    let nextTickNewRotting = 0;
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
        cropRottingAmmount += maxSell;
        if (cropSellTime[crop.id] < crop.by_age.length) {
            nextTickNewRotting += crop.by_age[cropSellTime[crop.id]];
        }
        $("#buy-crop-count-" + crop.id).attr({ "max": maxBuy });
        $("#sell-crop-count-" + crop.id).attr({ "max": maxSell });
    }
    $("#crop-rotting-amount").text(cropRottingAmmount);
    $("#next-tick-new-rotting").text(nextTickNewRotting);
    $("#next-tick-new-rotting").css("color", cropRottingAmmount + nextTickNewRotting > cropStorageSize ? "#ff2000" : "white");

    let tickConsumption = 0;
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
        let consumptionCrop = getItemById(updateData.crops, livestockConsumption[ls.id].crop_id);
        if (consumptionCrop) {
            tickConsumption += maxKill * livestockConsumption[ls.id].ammount * consumptionCrop.sell;
        }
        $("#buy-ls-count-" + ls.id).attr({ "max": maxBuy });
        $("#sell-ls-count-" + ls.id).attr({ "max": maxSell });
        $("#kill-ls-count-" + ls.id).attr({ "max": maxKill });
    }
    $("#consumption-money").text(tickConsumption);
    $("#consumption-money").css("color", tickConsumption > updateData.money ? "#ff2000" : "white");
}
