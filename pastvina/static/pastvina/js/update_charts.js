var cropProductionCharts = new Map();
var cropStorageCharts = new Map();
var livestockProductionCharts = new Map();

function update_charts(updateData) {
    console.log(updateData);

    for (crop of updateData.crops) {
        document.getElementById("crop-buy-price-" + crop.id).innerHTML = crop.buy;
        document.getElementById("crop-sell-price-" + crop.id).innerHTML = crop.sell;

        // Production
        let productionChart = cropProductionCharts[crop.id];
        for (let i = 0; i < crop.production.length; i++) {
            productionChart.data.datasets[0].data[i] = crop.production[i];
        }
        for (let i = crop.production.length; i < productionChart.data.datasets[0].data.length; i++) {
            productionChart.data.datasets[0].data[i] = 0;
        }
        productionChart.update();

        // Storage
        let storageChart = cropStorageCharts[crop.id];
        for (let i = 0; i < crop.storage.length; i++) {
            storageChart.data.datasets[0].data[i] = crop.storage[i];
        }
        for (let i = crop.storage.length; i < storageChart.data.datasets[0].data.length; i++) {
            storageChart.data.datasets[0].data[i] = 0;
        }
        storageChart.update();
    }

    for (ls of updateData.livestock) {
        document.getElementById("ls-buy-price-" + ls.id).innerHTML = ls.buy;
        document.getElementById("ls-sell-price-" + ls.id).innerHTML = ls.sell;

        let productionChart = livestockProductionCharts[ls.id];
        for (let i = 0; i < ls.production.length; i++) {
            productionChart.data.datasets[0].data[i] = ls.production[i];
        }
        for (let i = ls.production.length; i < productionChart.data.datasets[0].data.length; i++) {
            productionChart.data.datasets[0].data[i] = 0;
        }
        productionChart.update();
    }
}
