from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
from sympy import lambdify, symbols
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from .calculations.laplace import preprocess_input, direct_laplace, inverse_laplace

def calculator(request):
    context = {
        'result': '',
        'steps': None,
        'plot_data': None,
        'input_function': '',
        'mode': 'calculator',
        'calculation_type': 'directa',
        'error': '',
        'range_t_min': -10,
        'range_t_max': 10,
        'range_y_min': -5,
        'range_y_max': 5
    }
    
    if request.method == 'POST':
        input_function = request.POST.get('function', '').strip()
        calculation_type = request.POST.get('calculation_type', 'directa')
        clear_input = request.POST.get('clear_input', 'false').lower() == 'true'
        range_t_min = float(request.POST.get('range_t_min', -10))
        range_t_max = float(request.POST.get('range_t_max', 10))
        range_y_min = float(request.POST.get('range_y_min', -5))
        range_y_max = float(request.POST.get('range_y_max', 5))

        context['input_function'] = input_function
        context['calculation_type'] = calculation_type
        context['range_t_min'] = range_t_min
        context['range_t_max'] = range_t_max
        context['range_y_min'] = range_y_min
        context['range_y_max'] = range_y_max

        if clear_input:
            context['input_function'] = ''
            context['result'] = ''
            return JsonResponse({'success': True})
        
        if not input_function:
            context['error'] = 'Por favor, ingrese una función válida.'
        else:
            try:
                # Preprocesar la entrada
                processed_input = preprocess_input(input_function)
                
                # Calcular la transformada
                t, s = symbols('t s')
                expr = parse_expr(processed_input, transformations=standard_transformations + (implicit_multiplication_application, convert_xor), local_dict={'t': t, 's': s})
                expr = sp.expand(expr)
                
                if calculation_type == 'directa':
                    result, steps = direct_laplace(processed_input)
                    transform_expr = sp.laplace_transform(expr, t, s, noconds=True)
                else:
                    result, steps = inverse_laplace(processed_input)
                    transform_expr = sp.inverse_laplace_transform(expr, s, t, noconds=True)
                
                # Generar datos para la gráfica
                x_vals = np.linspace(range_t_min, range_t_max, 1000).tolist()  # Convertir a lista de Python
                
                if calculation_type == 'directa':
                    # Calcular f(t)
                    func = lambdify(t, expr, modules=['numpy'])
                    y_vals_raw = func(np.array(x_vals))
                    # Manejar valores no serializables (nan, inf, valores complejos)
                    y_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_vals_raw]
                    # Calcular F(s) usando la transformada
                    transform_func = lambdify(s, transform_expr, modules=['numpy'])
                    y_transform_raw = transform_func(np.array(x_vals))
                    y_transform_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_transform_raw]
                else:
                    # Calcular F(s)
                    func = lambdify(s, expr, modules=['numpy'])
                    y_vals_raw = func(np.array(x_vals))
                    y_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_vals_raw]
                    # Calcular f(t) usando la inversa
                    inverse_func = lambdify(t, transform_expr, modules=['numpy'])
                    y_transform_raw = inverse_func(np.array(x_vals))
                    y_transform_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_transform_raw]

                # Preparar los datos para Chart.js como diccionario simple
                plot_data = {
                    'x': x_vals,
                    'y': y_vals,
                    'y_transform': y_transform_vals,
                    'label_x': 't' if calculation_type == 'directa' else 's',
                    'label_y': 'f(t)' if calculation_type == 'directa' else 'F(s)',
                    'label_transform': 'F(s)' if calculation_type == 'directa' else 'f(t)'
                }
                context['plot_data'] = plot_data
                context['result'] = result
                context['steps'] = steps
            except Exception as e:
                context['error'] = f'Error al calcular: {str(e)}'
    
    return render(request, 'laplace_calculator/calculator.html', context)

def graph(request):
    context = {
        'plot_data': None,
        'input_function': '',
        'mode': 'graph',
        'calculation_type': 'directa',
        'error': '',
        'range_t_min': -10,
        'range_t_max': 10,
        'range_y_min': -5,
        'range_y_max': 5
    }
    
    if request.method == 'POST':
        input_function = request.POST.get('function', '').strip()
        calculation_type = request.POST.get('calculation_type', 'directa')
        clear_input = request.POST.get('clear_input', 'false').lower() == 'true'
        range_t_min = float(request.POST.get('range_t_min', -10))
        range_t_max = float(request.POST.get('range_t_max', 10))
        range_y_min = float(request.POST.get('range_y_min', -5))
        range_y_max = float(request.POST.get('range_y_max', 5))

        context['input_function'] = input_function
        context['calculation_type'] = calculation_type
        context['range_t_min'] = range_t_min
        context['range_t_max'] = range_t_max
        context['range_y_min'] = range_y_min
        context['range_y_max'] = range_y_max

        if clear_input:
            context['input_function'] = ''
            context['plot_data'] = None
            return JsonResponse({'success': True})

        if not input_function:
            context['error'] = 'Por favor, ingrese una función válida.'
        else:
            try:
                # Preprocesar la entrada
                processed_input = preprocess_input(input_function)
                
                # Generar datos para la gráfica
                t, s = symbols('t s')
                expr = parse_expr(processed_input, transformations=standard_transformations + (implicit_multiplication_application, convert_xor), local_dict={'t': t, 's': s})
                expr = sp.expand(expr)
                
                if calculation_type == 'directa':
                    transform_expr = sp.laplace_transform(expr, t, s, noconds=True)
                else:
                    transform_expr = sp.inverse_laplace_transform(expr, s, t, noconds=True)
                
                x_vals = np.linspace(range_t_min, range_t_max, 1000).tolist()  # Convertir a lista de Python
                
                if calculation_type == 'directa':
                    # Calcular f(t)
                    func = lambdify(t, expr, modules=['numpy'])
                    y_vals_raw = func(np.array(x_vals))
                    y_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_vals_raw]
                    # Calcular F(s) usando la transformada
                    transform_func = lambdify(s, transform_expr, modules=['numpy'])
                    y_transform_raw = transform_func(np.array(x_vals))
                    y_transform_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_transform_raw]
                else:
                    # Calcular F(s)
                    func = lambdify(s, expr, modules=['numpy'])
                    y_vals_raw = func(np.array(x_vals))
                    y_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_vals_raw]
                    # Calcular f(t) usando la inversa
                    inverse_func = lambdify(t, transform_expr, modules=['numpy'])
                    y_transform_raw = inverse_func(np.array(x_vals))
                    y_transform_vals = [float(val) if val.imag == 0 and not np.isnan(val) and not np.isinf(val) else 0 for val in y_transform_raw]

                # Preparar los datos para Chart.js como diccionario simple
                plot_data = {
                    'x': x_vals,
                    'y': y_vals,
                    'y_transform': y_transform_vals,
                    'label_x': 't' if calculation_type == 'directa' else 's',
                    'label_y': 'f(t)' if calculation_type == 'directa' else 'F(s)',
                    'label_transform': 'F(s)' if calculation_type == 'directa' else 'f(t)'
                }
                context['plot_data'] = plot_data
            except Exception as e:
                context['error'] = f'Error al graficar: {str(e)}'
    
    return render(request, 'laplace_calculator/graph.html', context)