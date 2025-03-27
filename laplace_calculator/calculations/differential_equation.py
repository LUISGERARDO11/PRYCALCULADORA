import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import re

def preprocess_differential_equation(func_str):
    """Preprocesa específicamente una ecuación diferencial para que sea compatible con SymPy."""
    func_str = func_str.strip()
    
    # Primero reemplazar y por y(x) cuando no es parte de y' o y''
    # Usamos una expresión regular más precisa
    func_str = re.sub(r'(?<!\w)y(?![\w\'])', 'y(x)', func_str)
    
    # Luego reemplazar y' y y''
    func_str = func_str.replace("y''", "Derivative(y(x), x, x)")
    func_str = func_str.replace("y'", "Derivative(y(x), x)")
    
    # Manejar casos como 2y -> 2*y(x)
    func_str = re.sub(r'(\d)(y\(x\))', r'\1*\2', func_str)
    
    return func_str

def format_result(solution):
    """Formatea la solución de la ecuación diferencial en LaTeX."""
    try:
        # Extraer el lado derecho de la ecuación (y(x) = ...)
        if isinstance(solution, sp.Eq):
            rhs = solution.rhs
        else:
            rhs = solution
        
        # Simplificar la solución
        rhs = sp.simplify(rhs)
        
        # Formatear correctamente los exponentes
        latex_expr = sp.latex(rhs)
        
        # Reemplazar e^{2x} por e^{2 x} para mejor legibilidad
        latex_expr = re.sub(r'e\^{(\d+)([a-zA-Z])', r'e^{\1 \2', latex_expr)
        
        return f"y(x) = {latex_expr}"
    except Exception as e:
        return f"Error al formatear la solución: {str(e)}"

def compute_steps(input_equation, x, y, equation):
    """Genera pasos intermedios detallados para la resolución de la ecuación diferencial."""
    try:
        steps = {
            'step1': [],  # Ecuación ingresada
            'step2': '',  # Tipo de ecuación
            'step3': [],  # Método utilizado
            'step4': [],  # Resolución paso a paso
            'step5': ''   # Solución final
        }

        # Paso 1: Mostrar la ecuación ingresada
        steps['step1'].append(f"\\text{{Ecuación ingresada: }} {sp.latex(equation.lhs)} = {sp.latex(equation.rhs)}")

        # Paso 2: Identificar el tipo de ecuación
        order = sp.ode_order(equation, y)
        steps['step2'] = f"\\text{{Ecuación diferencial de {'primer' if order == 1 else 'segundo'} orden.}}"

        # Resolver la ecuación diferencial primero para determinar el tipo
        solution = sp.dsolve(equation)
        
        if order == 1:
            # Para ecuaciones lineales de primer orden y' + P(x)y = Q(x)
            if equation.rhs == 0:  # Homogénea
                steps['step2'] += " \\text{{ (lineal homogénea)}}"
                # Encontrar P(x)
                coeff_y = equation.lhs.coeff(sp.Function('y')(x))
                coeff_dy = equation.lhs.coeff(sp.Derivative(y, x))
                P = coeff_y / coeff_dy if coeff_dy != 0 else 0
                
                steps['step3'].append("\\text{{Método: Separación de variables}}")
                steps['step4'].append(f"\\frac{{dy}}{{dx}} = {sp.latex(-P)}y")
                steps['step4'].append(f"\\int \\frac{{dy}}{{y}} = \int {sp.latex(-P)} dx")
                steps['step4'].append(f"\\ln|y| = {sp.latex(-P*x)} + C_1")
                steps['step4'].append(f"y = Ce^{{{sp.latex(-P*x)}}}")
            else:
                steps['step2'] += " \\text{{ (lineal no homogénea)}}"
                steps['step3'].append("\\text{{Método: Factor integrante}}")

        steps['step5'] = f"\\text{{Solución general: }} y(x) = {sp.latex(solution.rhs)}"

        return steps
    except Exception as e:
        print(f"Error al calcular los pasos intermedios: {str(e)}")
        return {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}

def solve_differential_equation(input_equation):
    """Resuelve una ecuación diferencial y devuelve la solución con pasos intermedios."""
    try:
        # Preprocesar la entrada
        input_equation = preprocess_differential_equation(input_equation)
        print(f"Ecuación preprocesada: {input_equation}")  # Para depuración

        # Definir símbolos
        x = sp.symbols('x')
        y = sp.Function('y')
        
        # Parsear la ecuación
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        local_dict = {
            'x': x,
            'y': y,
            'Derivative': sp.Derivative
        }
        
        # Manejar ecuaciones con o sin igualdad
        if '=' in input_equation:
            parts = input_equation.split('=', 1)
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Parsear ambos lados por separado
            lhs_expr = parse_expr(lhs, transformations=transformations, local_dict=local_dict)
            rhs_expr = parse_expr(rhs, transformations=transformations, local_dict=local_dict)
            equation = sp.Eq(lhs_expr, rhs_expr)
        else:
            # Si no hay igualdad, asumimos que es igual a 0
            lhs_expr = parse_expr(input_equation, transformations=transformations, local_dict=local_dict)
            equation = sp.Eq(lhs_expr, 0)

        print(f"Ecuación parseada: {equation}")  # Para depuración

        # Resolver la ecuación
        solution = sp.dsolve(equation, y(x))
        print(f"Solución encontrada: {solution}")  # Para depuración

        # Generar pasos intermedios
        steps = compute_steps(input_equation, x, y(x), equation)

        # Formatear resultado
        result = format_result(solution)
        
        return result, steps

    except Exception as e:
        error_msg = f"Error al resolver la ecuación diferencial: {str(e)}"
        print(error_msg)
        return f"\\text{{Error: {error_msg}}}", {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}