var tickId = 0;
var timeOfNextUpdate = Date.now();
var showTime = false;
var loadTime = Date.now();
var serverTimeCorrection = 0;

function getServerTimeCorrection(requestTime, serverTime, responseTime) {
    if (requestTime === null || serverTime === null || responseTime === null) {
        console.error("Could not get a time.");
        return 0;
    }

    let turnaroundTime = responseTime - requestTime;
    if (turnaroundTime < 0) {
        console.error("Time continuity failed.");
        return 0;
    }

    return (requestTime + responseTime) / 2 - serverTime;
}

function updateTimeCorrection() {
    $.post("/time_check/ping", {
        'request_time': Date.now(),
        'csrfmiddlewaretoken': csrf_token,
    }, "json")
    .done(function(data) {
        let responseTime = Date.now();
        data.response_time = responseTime;
        console.log(data);
        serverTimeCorrection = getServerTimeCorrection(data.request_time, data.server_time, responseTime);
        console.log("Server time correction: " + serverTimeCorrection/1000 + " s");
    })
    .fail(function(error, textStatus) {
        let userErrorText = "";
        if (textStatus == "timeout") {
            userErrorText = "Server neodpověděl včas.";
        } else if (error.responseText) {
            userErrorText = error.responseText;
        } else {
            userErrorText = "Neznámá chyba."
            console.log(textStatus);
            console.log(error);
        }
        console.error("Nepodařilo se spojit se serverem (korekce času).\n" + userErrorText);
    });
}


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
    $.post("update", {
        'csrfmiddlewaretoken': csrf_token,
    }, "json")
    .done(function(update_data) {
        updateCharts(update_data);
    })
    .fail(function(error, textStatus) {
        let userErrorText = "";
        if (textStatus == "timeout") {
            userErrorText = "Server neodpověděl včas.";
        } else if (error.responseText) {
            userErrorText = error.responseText;
        } else {
            userErrorText = "Neznámá chyba."
            console.log(textStatus);
            console.log(error);
        }
        console.error("Nebylo možné obnovit data.\n" + userErrorText);
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
var cropRottingTime = new Object();
var livestockLifeTime = new Object();
var livestockConsumption = new Object();
var livestockSellLimit = Infinity;
var cropStorageSize = Infinity;

function updateCharts(updateData) {
    console.log(updateData);
    if (updateData.reload_time) {
        let correctedReloadTime = updateData.reload_time + serverTimeCorrection;
        if (correctedReloadTime > loadTime && correctedReloadTime < Date.now()) {
            location.reload();
        }
    }

    let currentlySold = updateData.slaughtered;
    $("#game-money").text((updateData.money === null) ? "-" : updateData.money);
    $("#ls-sold-amount").text(currentlySold);
    let correctedUpdateTime = updateData.time + serverTimeCorrection;
    if (correctedUpdateTime > Date.now()) {
        timeOfNextUpdate = correctedUpdateTime;
        showTime = true;
        updateTimeToNextTick();
    }
    let isNewTick = tickId != updateData.tick_id;
    tickId = updateData.tick_id;
    $("#tick-index").text((updateData.tick_index === null) ? "-" : updateData.tick_index)

    let cropRottingTotal = 0;
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
        let options = ageChart.options.scales.yAxes[0].ticks;
        if (isNewTick) {
            options.max = Math.max(10, ...crop.by_age);
        } else if (crop.by_age.length > 0) {
            options.max = Math.max(options.max, crop.by_age[crop.by_age.length - 1]);
        }
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/crop.buy);
        let growing = crop.by_age.slice(cropRottingTime[crop.id]).reduce((a, b) => a + b, 0);
        let rotting = crop.by_age.slice(0, cropRottingTime[crop.id]).reduce((a, b) => a + b, 0);
        cropRottingTotal += rotting;
        if (cropRottingTime[crop.id] < crop.by_age.length) {
            nextTickNewRotting += crop.by_age[cropRottingTime[crop.id]];
        }
        $("#crop-growing-amount-" + crop.id).text(growing);
        $("#crop-rotting-amount-" + crop.id).text(rotting);
        $("#crop-bought-amount-" + crop.id).text(crop.bought);
        $("#crop-sold-amount-" + crop.id).text(crop.sold);
        $("#crop-buy-limit-" + crop.id).text(maxBuy);
        $("#crop-buy-limit-" + crop.id).css("color", maxBuy > cropStorageSize ? "#ff2000" : "");
        $("#crop-sell-limit-" + crop.id).text(rotting);
        $("#buy-crop-count-" + crop.id).attr("max", maxBuy);
        $("#sell-crop-count-" + crop.id).attr("max", rotting);
        $("#buy-crop-button-" + crop.id).attr("disabled", crop.bought != 0);
        $("#sell-crop-button-" + crop.id).attr("disabled", crop.sold != 0);
    }
    $("#crop-rotting-total").text(cropRottingTotal);
    $("#next-tick-new-rotting").text(nextTickNewRotting);
    $("#next-tick-new-rotting").css("color", cropRottingTotal + nextTickNewRotting > cropStorageSize ? "#ff2000" : "white");

    let tickConsumption = 0;
    let tickProduction = 0;
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
        let options = ageChart.options.scales.yAxes[0].ticks;
        if (isNewTick) {
            options.max = Math.max(10, ...ls.by_age);
        } else if (ls.by_age.length > 0) {
            options.max = Math.max(options.max, ls.by_age[ls.by_age.length - 1]);
        }
        ageChart.update();

        let maxBuy = Math.floor(updateData.money/ls.buy);
        let baby = ls.by_age.slice(livestockLifeTime[ls.id]).reduce((a, b) => a + b, 0);
        let adult = ls.by_age.slice(0, livestockLifeTime[ls.id]).reduce((a, b) => a + b, 0);
        let maxSell = Math.min(adult, livestockSellLimit - currentlySold);
        let consumptionCrop = getItemById(updateData.crops, livestockConsumption[ls.id].crop_id);
        if (consumptionCrop) {
            tickConsumption += (baby + adult) * livestockConsumption[ls.id].amount * consumptionCrop.sell;
        }
        tickProduction += adult * ls.product_price;
        $("#ls-baby-amount-" + ls.id).text(baby);
        $("#ls-adult-amount-" + ls.id).text(adult);
        $("#ls-bought-amount-" + ls.id).text(ls.bought);
        $("#ls-sold-amount-" + ls.id).text(ls.sold);
        $("#ls-killed-amount-" + ls.id).text(ls.killed);
        $("#ls-buy-limit-" + ls.id).text(maxBuy);
        $("#ls-sell-limit-" + ls.id).text(maxSell);
        $("#ls-kill-limit-" + ls.id).text(baby + adult);
        $("#buy-ls-count-" + ls.id).attr("max", maxBuy);
        $("#sell-ls-count-" + ls.id).attr("max", maxSell);
        $("#kill-ls-count-" + ls.id).attr("max", baby + adult);
        $("#buy-ls-button-" + ls.id).attr("disabled", ls.bought != 0);
        $("#sell-ls-button-" + ls.id).attr("disabled", ls.sold != 0);
        $("#kill-ls-button-" + ls.id).attr("disabled", ls.killed != 0);
    }
    $("#consumption-money").text(tickConsumption);
    $("#consumption-money").css("color", tickConsumption > updateData.money ? "#ff2000" : "white");
    $("#production-money").text(tickProduction);
}
