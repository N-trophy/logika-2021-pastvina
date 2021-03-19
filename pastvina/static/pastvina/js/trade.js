function requestTrade(tradeType, prodType, prodId, count) {
    if (count <= 0) {
        addMessage("error", "Nelze obchodovat nekladné množství.", true);
        console.error("Nelze obchodovat nekladné množství.");
        return;
    }
    if (tradeType != 'buy' && tradeType != 'sell' && tradeType != 'kill') {
        console.error('Unknown type type: "' + tradeType + '" (expected buy/sell/kill)');
    }
    if (prodType != 'crop' && prodType != 'ls') {
        console.error('Unknown prod type: "' + prodType + '" (expected crop/ls)');
    }

    let buttonElem = $('#' + tradeType + '-' + prodType + '-button-' + prodId);
    buttonElem.prop('disabled', true);

    $.post("trade", {
        'tick_id': tickId,
        'trade_type': tradeType,
        'prod_type': prodType,
        'prod_id': prodId,
        'count': count,
        'csrfmiddlewaretoken': csrf_token,
    })
    .done(function(data) {
        requestUpdateCharts();
        console.log(data);
        addMessage("default", data, true);
    })
    .fail(function(error, textStatus) {
        buttonElem.prop('disabled', false);
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
        console.error("Obchod neproběhl.\n" + userErrorText);
        addMessage("error", "Obchod neproběhl.\n" + userErrorText);
    });
}
