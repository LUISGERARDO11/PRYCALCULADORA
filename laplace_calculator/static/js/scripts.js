document.addEventListener('DOMContentLoaded', () => {
    // Modo oscuro
    const toggleDarkMode = () => {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('darkMode', isDark);
        document.getElementById('dark-mode-icon').textContent = isDark ? '☀️' : '🌙';
    };

    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.documentElement.classList.add('dark');
        document.getElementById('dark-mode-icon').textContent = '☀️';
    }

    document.querySelector('#dark-mode-toggle')?.addEventListener('click', toggleDarkMode);

    // Dropdown
    const dropdownToggle = document.getElementById('dropdown-toggle');
    const dropdownMenu = document.getElementById('dropdown-menu');
    const dropdownLabel = document.getElementById('dropdown-label');
    const calculationTypeInput = document.getElementById('calculation-type');
    const graphCalculationTypeInput = document.getElementById('graph-calculation-type');

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', (e) => {
            e.preventDefault(); // Prevenir el comportamiento predeterminado (enviar el formulario)
            dropdownMenu.classList.toggle('hidden');
        });

        dropdownMenu.querySelectorAll('div').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                dropdownLabel.textContent = item.textContent.trim();
                if (calculationTypeInput) calculationTypeInput.value = value;
                if (graphCalculationTypeInput) graphCalculationTypeInput.value = value;
                dropdownMenu.classList.add('hidden');
                updatePlaceholdersAndExample();
            });
        });

        document.addEventListener('click', (e) => {
            if (dropdownToggle && dropdownMenu && !dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.add('hidden');
            }
        });
    }

    // Copiar al portapapeles
    const copyButton = document.getElementById('copy-button');
    const resultText = document.getElementById('result-text');

    copyButton?.addEventListener('click', () => {
        navigator.clipboard.writeText(resultText.textContent).then(() => {
            alert('Resultado copiado al portapapeles');
        }).catch(err => {
            console.error('Error al copiar:', err);
        });
    });

    // Limpiar formulario (calculadora)
    const clearButton = document.getElementById('clear-button');
    clearButton?.addEventListener('click', () => {
        const form = document.getElementById('calculator-form');
        form.reset();
        document.getElementById('function-input').value = '';
        document.getElementById('result-text').innerHTML = 'El resultado aparecerá aquí';
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `function=&calculation_type=${calculationTypeInput?.value || 'directa'}&clear_input=true`
        }).then(response => response.json()).then(data => {
            if (data.success) {
                console.log('Input y resultado limpiados con éxito');
            } else {
                console.error('Error al limpiar el input:', data.error);
            }
        }).catch(err => {
            console.error('Error en la solicitud:', err);
        });
    });

    // Declaraciones de variables para el modo gráfico
    const functionInput = document.getElementById('function-input');
    const exampleButton = document.getElementById('example-button');
    const graphFunctionInput = document.getElementById('graph-function-input');
    const graphExampleButton = document.getElementById('graph-example-button');

    // Actualizar placeholder y botón de ejemplo según el tipo de cálculo
    function updatePlaceholdersAndExample() {
        const calcType = calculationTypeInput?.value || graphCalculationTypeInput?.value || 'directa';
        if (calcType === 'inversa') {
            if (functionInput) {
                functionInput.placeholder = 'Ej: 1/(s-2)';
                exampleButton.textContent = 'Ejemplo: 1/(s-2)';
                exampleButton.onclick = () => { functionInput.value = '1/(s-2)'; };
            }
            if (graphFunctionInput) {
                graphFunctionInput.placeholder = 'Ej: 1/(s-2)';
                graphExampleButton.textContent = 'Ejemplo: 1/(s-2)';
                graphExampleButton.onclick = () => { graphFunctionInput.value = '1/(s-2)'; };
            }
        } else {
            if (functionInput) {
                functionInput.placeholder = 'Ej: 2t + 3e^(-t)';
                exampleButton.textContent = 'Ejemplo: 2t + 3e^(-t)';
                exampleButton.onclick = () => { functionInput.value = '2t + 3e^(-t)'; };
            }
            if (graphFunctionInput) {
                graphFunctionInput.placeholder = 'Ej: 2t + 3e^(-t)';
                graphExampleButton.textContent = 'Ejemplo: 2t + 3e^(-t)';
                graphExampleButton.onclick = () => { graphFunctionInput.value = '2t + 3e^(-t)'; };
            }
        }
    }

    // Inicializar al cargar la página
    updatePlaceholdersAndExample();

    const graphClearButton = document.getElementById('graph-clear-button');

    graphClearButton?.addEventListener('click', () => {
        const form = document.getElementById('graph-form');
        form.reset();
        graphFunctionInput.value = '';
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `function=&calculation_type=${graphCalculationTypeInput?.value || 'directa'}&clear_input=true`
        }).then(response => response.json()).then(data => {
            if (data.success) {
                console.log('Input y gráfica limpiados con éxito');
                location.reload(); // Recargar para limpiar la gráfica
            } else {
                console.error('Error al limpiar el input:', data.error);
            }
        }).catch(err => {
            console.error('Error en la solicitud:', err);
        });
    });

    // Ejemplo en modo gráfico
    graphExampleButton?.addEventListener('click', () => {
        const calcType = graphCalculationTypeInput?.value || 'directa';
        graphFunctionInput.value = calcType === 'inversa' ? '1/(s-2)' : '2t + 3e^(-t)';
    });

    // Switches para mostrar u ocultar f(t) y F(s) (simulado)
    const showFtCheckbox = document.getElementById('show-ft');
    const showFsCheckbox = document.getElementById('show-fs');

    showFtCheckbox?.addEventListener('change', (e) => {
        console.log('Mostrar f(t):', e.target.checked);
        // Lógica futura para gráfica dinámica
    });

    showFsCheckbox?.addEventListener('change', (e) => {
        console.log('Mostrar F(s):', e.target.checked);
        // Lógica futura para gráfica dinámica
    });

    // Controles de rango
    const rangeTMin = document.getElementById('range-t-min');
    const rangeTMax = document.getElementById('range-t-max');
    const rangeYMin = document.getElementById('range-y-min');
    const rangeYMax = document.getElementById('range-y-max');
    const formRangeTMin = document.getElementById('form-range-t-min');
    const formRangeTMax = document.getElementById('form-range-t-max');
    const formRangeYMin = document.getElementById('form-range-y-min');
    const formRangeYMax = document.getElementById('form-range-y-max');

    function updateGraphWithRanges() {
        const tMin = rangeTMin.value;
        const tMax = rangeTMax.value;
        const yMin = rangeYMin.value;
        const yMax = rangeYMax.value;

        // Actualizar los campos ocultos en el formulario de calculator.html
        if (formRangeTMin) formRangeTMin.value = tMin;
        if (formRangeTMax) formRangeTMax.value = tMax;
        if (formRangeYMin) formRangeYMin.value = yMin;
        if (formRangeYMax) formRangeYMax.value = yMax;

        // Obtener la función actual y el tipo de cálculo
        const functionValue = (graphFunctionInput || functionInput)?.value || '';
        const calcType = graphCalculationTypeInput?.value || calculationTypeInput?.value || 'directa';

        if (functionValue) {
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `function=${encodeURIComponent(functionValue)}&calculation_type=${calcType}&range_t_min=${tMin}&range_t_max=${tMax}&range_y_min=${yMin}&range_y_max=${yMax}${graphFunctionInput ? '&plot=' : ''}`
            }).then(response => {
                if (response.ok) {
                    location.reload(); // Recargar la página para mostrar la nueva gráfica
                } else {
                    console.error('Error al actualizar la gráfica');
                }
            }).catch(err => {
                console.error('Error en la solicitud:', err);
            });
        }
    }

    rangeTMin?.addEventListener('change', updateGraphWithRanges);
    rangeTMax?.addEventListener('change', updateGraphWithRanges);
    rangeYMin?.addEventListener('change', updateGraphWithRanges);
    rangeYMax?.addEventListener('change', updateGraphWithRanges);

    // Exportar gráfica
    const exportGraphButton = document.getElementById('export-graph-button');
    exportGraphButton?.addEventListener('click', () => {
        const img = document.querySelector('img[alt="Gráfica"]');
        if (img) {
            const link = document.createElement('a');
            link.href = img.src;
            link.download = 'grafica-laplace.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert('No hay gráfica para exportar.');
        }
    });

    // Inicializar Lucide para los íconos
    lucide.createIcons();
});