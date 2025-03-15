document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('chart-canvas');
    if (!chartCanvas || !window.plotData) return;

    const ctx = chartCanvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: window.plotData.x,
            datasets: [
                {
                    label: window.plotData.label_y,
                    data: window.plotData.y,
                    borderColor: 'blue',
                    fill: false,
                    tension: 0.1,
                    hidden: !document.getElementById('show-ft').checked
                },
                {
                    label: window.plotData.label_transform,
                    data: window.plotData.y_transform,
                    borderColor: 'red',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.1,
                    hidden: !document.getElementById('show-fs').checked
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: window.plotData.label_x
                    },
                    min: window.range_t_min,
                    max: window.range_t_max
                },
                y: {
                    title: {
                        display: true,
                        text: 'Valor'
                    },
                    min: window.range_y_min,
                    max: window.range_y_max
                }
            }
        }
    });

    // Actualizar la visibilidad de las líneas con los switches
    const showFtCheckbox = document.getElementById('show-ft');
    const showFsCheckbox = document.getElementById('show-fs');

    showFtCheckbox.addEventListener('change', (e) => {
        chart.data.datasets[0].hidden = !e.target.checked;
        chart.update();
    });

    showFsCheckbox.addEventListener('change', (e) => {
        chart.data.datasets[1].hidden = !e.target.checked;
        chart.update();
    });

    // Controles de rango
    const rangeTMin = document.getElementById('range-t-min');
    const rangeTMax = document.getElementById('range-t-max');
    const rangeYMin = document.getElementById('range-y-min');
    const rangeYMax = document.getElementById('range-y-max');

    function updateGraphWithRanges() {
        const tMin = parseFloat(rangeTMin.value);
        const tMax = parseFloat(rangeTMax.value);
        const yMin = parseFloat(rangeYMin.value);
        const yMax = parseFloat(rangeYMax.value);

        chart.options.scales.x.min = tMin;
        chart.options.scales.x.max = tMax;
        chart.options.scales.y.min = yMin;
        chart.options.scales.y.max = yMax;

        const functionValue = document.getElementById('graph-function-input')?.value || '';
        const calcType = document.getElementById('graph-calculation-type')?.value || 'directa';

        if (functionValue) {
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `function=${encodeURIComponent(functionValue)}&calculation_type=${calcType}&range_t_min=${tMin}&range_t_max=${tMax}&range_y_min=${yMin}&range_y_max=${yMax}&plot=`
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    console.error('Error al actualizar la gráfica');
                }
            }).catch(err => {
                console.error('Error en la solicitud:', err);
            });
        }
    }

    rangeTMin.addEventListener('change', updateGraphWithRanges);
    rangeTMax.addEventListener('change', updateGraphWithRanges);
    rangeYMin.addEventListener('change', updateGraphWithRanges);
    rangeYMax.addEventListener('change', updateGraphWithRanges);

    // Exportar gráfica
    const exportGraphButton = document.getElementById('export-graph-button');
    exportGraphButton.addEventListener('click', () => {
        const link = document.createElement('a');
        link.href = chartCanvas.toDataURL('image/png');
        link.download = 'grafica-laplace.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});