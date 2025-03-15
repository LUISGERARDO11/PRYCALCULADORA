document.addEventListener('DOMContentLoaded', () => {
    const plotDataElement = document.getElementById('plot-data');
    const rangeTMinElement = document.getElementById('range-t-min-value');
    const rangeTMaxElement = document.getElementById('range-t-max-value');
    const rangeYMinElement = document.getElementById('range-y-min-value');
    const rangeYMaxElement = document.getElementById('range-y-max-value');

    if (plotDataElement && rangeTMinElement && rangeTMaxElement && rangeYMinElement && rangeYMaxElement) {
        console.log("Contenido de plotDataElement.textContent:", plotDataElement.textContent);
        window.plotData = JSON.parse(plotDataElement.textContent || 'null');
        window.range_t_min = parseFloat(rangeTMinElement.textContent) || -10;
        window.range_t_max = parseFloat(rangeTMaxElement.textContent) || 10;
        window.range_y_min = parseFloat(rangeYMinElement.textContent) || -5;
        window.range_y_max = parseFloat(rangeYMaxElement.textContent) || 5;
    } else {
        window.plotData = null;
        window.range_t_min = -10;
        window.range_t_max = 10;
        window.range_y_min = -5;
        window.range_y_max = 5;
    }
});