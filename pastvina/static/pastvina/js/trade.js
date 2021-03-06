function requestTrade(tradeType, prodType, prodId, count) {
    if (count <= 0)
    {
        console.log("Trade ammount is <= 0: " + count);
        alert("Select positive amount to " + tradeType + " (selected: " + count + ")");
        return;
    }
    if (tradeType != 'buy' && tradeType != 'sell' && tradeType != 'kill')
    {
        console.log('Unknown type type: "' + tradeType + '" (expected buy/sell/kill)');
    }
    if (prodType != 'crop' && prodType != 'ls')
    {
        console.log('Unknown prod type: "' + prodType + '" (expected crop/ls)');
    }

    $.get("trade", { 'tick_id': tickId, 'trade_type': tradeType, 'prod_type': prodType, 'prod_id': prodId, 'count': count })
    .done(function() {
        requestUpdateCharts();
    })
    .fail(function(error) {
        alert("Obchod neproběhl.\n" + error.responseText);
    });
}
