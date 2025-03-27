from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
from sympy import lambdify, symbols
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from .calculations.laplace import preprocess_input, direct_laplace, inverse_laplace
from .calculations.differential_equation import solve_differential_equation
from .calculations.rk4 import solve_with_rk4  # Nueva importación para RK4

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
                if calculation_type == 'diferencial':
                    # Resolver ecuación diferencial
                    result, steps = solve_differential_equation(input_function)
                    context['result'] = result
                    context['steps'] = steps
                    context['plot_data'] = None  # No generamos gráfica para ecuaciones diferenciales
                else:
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
                    x_vals = np.linspace(range_t_min, range_t_max, 1000).tolist()
                    
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
                if calculation_type == 'diferencial':
                    # Por ahora, no generamos gráficas para ecuaciones diferenciales
                    context['error'] = 'La generación de gráficas para ecuaciones diferenciales no está soportada en este modo.'
                    context['plot_data'] = None
                else:
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
                    
                    x_vals = np.linspace(range_t_min, range_t_max, 1000).tolist()
                    
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

def rk4(request):
    """
    Vista para resolver ecuaciones diferenciales usando el método RK4.
    """
    context = {
        'result': '',
        'steps': None,
        'error': '',
        'mode': 'rk4',
        'r': 0.0498,  # Ajustado según MATLAB
        'A': 10.23,   # Ajustado según MATLAB
        'T': 12,
        'phi': 9.51,  # Ajustado según MATLAB
        'P0': 43.64,
        'h': 1,
        't_start': 0,
        't_end': 24,
    }
    
    if request.method == 'POST':
        try:
            r = float(request.POST.get('r', 0.0498))
            A = float(request.POST.get('A', 10.23))
            T = float(request.POST.get('T', 12))
            phi = float(request.POST.get('phi', 9.51))
            P0 = float(request.POST.get('P0', 43.64))
            h = float(request.POST.get('h', 1))
            t_start = float(request.POST.get('t_start', 0))
            t_end = float(request.POST.get('t_end', 24))
        except ValueError as e:
            context['error'] = 'Por favor, ingrese valores numéricos válidos para los parámetros.'
            return render(request, 'laplace_calculator/rk4.html', context)

        context['r'] = r
        context['A'] = A
        context['T'] = T
        context['phi'] = phi
        context['P0'] = P0
        context['h'] = h
        context['t_start'] = t_start
        context['t_end'] = t_end

        if h <= 0:
            context['error'] = 'El paso de tiempo (h) debe ser mayor que 0.'
        elif t_end <= t_start:
            context['error'] = 'El tiempo final debe ser mayor que el tiempo inicial.'
        elif T == 0:
            context['error'] = 'El período (T) no puede ser 0.'
        else:
            try:
                P_values, t_values, steps, quarterly_values, total_2025 = solve_with_rk4(r, A, T, phi, P0, t_start, t_end, h)
                if P_values is None:
                    context['error'] = 'Error al resolver la ecuación con RK4.'
                else:
                    context['result'] = f"\\text{{Demanda total estimada para 2025: }} {total_2025:.2f} \\text{{ unidades}}"
                    context['steps'] = steps
            except Exception as e:
                context['error'] = f'Error al resolver con RK4: {str(e)}'
    
    return render(request, 'laplace_calculator/rk4.html', context)