import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

def preprocess_input(func_str):
    # Normaliza la entrada para que sea compatible con SymPy
    func_str = func_str.strip().lower()
    
    # Reemplaza 'e^' con 'exp(' y asegura que se añadan paréntesis correctamente
    if 'e^' in func_str:
        func_str = func_str.replace('e^(', 'exp(')
        func_str = func_str.replace('e^', 'exp(')
        open_parens = func_str.count('(')
        close_parens = func_str.count(')')
        func_str += ')' * (open_parens - close_parens)
    
    # Maneja funciones trigonométricas y otras comunes
    func_str = func_str.replace('sin', 'sin(').replace('cos', 'cos(').replace('tan', 'tan(')
    if any(trig in func_str for trig in ['sin', 'cos', 'tan']):
        open_parens = func_str.count('(')
        close_parens = func_str.count(')')
        func_str += ')' * (open_parens - close_parens)
    
    # Asegura multiplicación explícita
    func_str = func_str.replace('e(', '*exp(')
    
    transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
    return func_str

def format_result(result):
    if isinstance(result, tuple):
        laplace, cond, domain = result
        latex_expr = sp.latex(laplace)
        return f"\\mathcal{{L}}{{f(t)}} = {latex_expr} \\quad (\\text{{condición: }} {cond}, \\text{{dominio: }} {domain})"
    else:
        result = sp.simplify(result)
        latex_expr = sp.latex(result)
        return f"\\mathcal{{L}}{{f(t)}} = {latex_expr}"

def format_inverse_result(result):
    result = sp.simplify(result)
    latex_expr = sp.latex(result)
    return f"\\mathcal{{L}}^{{-1}}{{F(s)}} = {latex_expr}"

def compute_steps(func_str, t, s, calc_type='directa'):
    """Genera pasos intermedios detallados para la transformada de Laplace."""
    try:
        func_str = preprocess_input(func_str)
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        f = parse_expr(func_str, transformations=transformations, local_dict={'t': t, 's': s})
        f = sp.expand(f)  # Expande la expresión
        
        steps = {
            'step1': [],  # Identificación de términos
            'step2': '',  # Expansión inicial
            'step3': [],  # Transformadas individuales
            'step4': [],  # Aplicación de propiedades específicas
            'step5': ''   # Resultado combinado
        }
        
        # Paso 1: Identificar términos individuales
        steps['step1'].append(f"\\text{{Función ingresada: }} {sp.latex(f)}")
        if isinstance(f, sp.Add):
            terms = f.args
            steps['step1'].append(f"\\text{{Separamos en términos: }} {sp.latex(f)} = {' + '.join(sp.latex(term) for term in terms)}")
        else:
            terms = [f]
            steps['step1'].append(f"\\text{{Un solo término: }} {sp.latex(f)}")
        
        # Paso 2: Expansión inicial (si aplica)
        if f != sp.expand(f):
            steps['step2'] = f"\\text{{Expandimos la expresión: }} {sp.latex(f)} \\rightarrow {sp.latex(sp.expand(f))}"
        
        # Paso 3 y 4: Transformadas individuales y propiedades específicas
        for term in terms:
            coeff = term.as_coeff_Mul()[0] if term.as_coeff_Mul()[0] != term else 1
            base_term = term / coeff if coeff != 1 else term
            
            term_latex = sp.latex(base_term)
            steps['step3'].append(f"\\text{{Analizamos }} {term_latex}:")
            
            # Caso 1: Término polinómico t^n
            if isinstance(base_term, sp.Pow) and base_term.args[0] == t:
                n = base_term.args[1]
                transform = sp.factorial(n) / s**(n + 1)
                steps['step4'].append(
                    f"\\text{{Para }} t^{{{sp.latex(n)}}}, \\text{{ usamos: }} \\mathcal{{L}}{{t^{{{sp.latex(n)}}}}} = \\frac{{{sp.latex(sp.factorial(n))}}}{{s^{{{sp.latex(n+1)}}}}}"
                )
                steps['step4'].append(f"\\text{{Entonces: }} \\mathcal{{L}}{{{term_latex}}} = {sp.latex(transform)}")
            
            # Caso 2: Exponencial e^(at)
            elif isinstance(base_term, sp.exp):
                a = base_term.args[0] / t
                transform = 1 / (s - a)
                steps['step4'].append(
                    f"\\text{{Para }} e^{{{sp.latex(a*t)}}}, \\text{{ usamos: }} \\mathcal{{L}}{{e^{{{sp.latex(a*t)}}}}} = \\frac{{1}}{{s - {sp.latex(a)}}}"
                )
                steps['step4'].append(f"\\text{{Entonces: }} \\mathcal{{L}}{{{term_latex}}} = {sp.latex(transform)}")
            
            # Caso 3: t^n * e^(at)
            elif isinstance(base_term, sp.Mul) and any(isinstance(factor, sp.exp) for factor in base_term.args) and any(isinstance(factor, sp.Pow) and factor.args[0] == t for factor in base_term.args):
                t_power = [f for f in base_term.args if isinstance(f, sp.Pow) and f.args[0] == t][0]
                exp_term = [f for f in base_term.args if isinstance(f, sp.exp)][0]
                n = t_power.args[1]
                a = exp_term.args[0] / t
                transform = sp.factorial(n) / (s - a)**(n + 1)
                steps['step4'].append(
                    f"\\text{{Para }} t^{{{sp.latex(n)}}} e^{{{sp.latex(a*t)}}}, \\text{{ usamos: }} \\mathcal{{L}}{{t^{{{sp.latex(n)}}} e^{{{sp.latex(a*t)}}}}} = \\frac{{{sp.latex(sp.factorial(n))}}}{{(s - {sp.latex(a)})^{{{sp.latex(n+1)}}}}}"
                )
                steps['step4'].append(f"\\text{{Entonces: }} \\mathcal{{L}}{{{term_latex}}} = {sp.latex(transform)}")
            
            # Caso 4: Funciones trigonométricas
            elif any(func in str(base_term) for func in ['sin', 'cos']):
                if 'sin' in str(base_term):
                    w = base_term.args[0] / t
                    transform = w / (s**2 + w**2)
                    steps['step4'].append(
                        f"\\text{{Para }} \\sin({sp.latex(w*t)}), \\text{{ usamos: }} \\mathcal{{L}}{{\\sin({sp.latex(w*t)})}} = \\frac{{{sp.latex(w)}}}{{s^2 + {sp.latex(w**2)}}}"
                    )
                elif 'cos' in str(base_term):
                    w = base_term.args[0] / t
                    transform = s / (s**2 + w**2)
                    steps['step4'].append(
                        f"\\text{{Para }} \\cos({sp.latex(w*t)}), \\text{{ usamos: }} \\mathcal{{L}}{{\\cos({sp.latex(w*t)})}} = \\frac{{s}}{{s^2 + {sp.latex(w**2)}}}"
                    )
                steps['step4'].append(f"\\text{{Entonces: }} \\mathcal{{L}}{{{term_latex}}} = {sp.latex(transform)}")
            
            # Caso genérico: Usar SymPy directamente
            else:
                if calc_type == 'directa':
                    transform = sp.laplace_transform(base_term, t, s, noconds=True)
                else:
                    transform = sp.inverse_laplace_transform(base_term, s, t, noconds=True)
                steps['step4'].append(f"\\text{{Transformada directa de }} {term_latex}: {sp.latex(transform)}")
            
            # Ajustar por el coeficiente
            if coeff != 1:
                steps['step4'].append(
                    f"\\text{{Multiplicamos por el coeficiente }} {sp.latex(coeff)}: \\mathcal{{L}}{{{sp.latex(term)}}} = {sp.latex(coeff * transform)}"
                )
        
        # Paso 5: Combinar resultados
        if len(terms) > 1:
            combined = " + ".join([f"{term.as_coeff_Mul()[0]}\\mathcal{{L}}{{{sp.latex(term.as_coeff_Mul()[1] if term.as_coeff_Mul()[0] != term else term)}}}" for term in terms])
            steps['step5'] = f"\\text{{Por linealidad: }} \\mathcal{{L}}{{{sp.latex(f)}}} = {combined}"
        
        return steps
    except Exception as e:
        print(f"Error al calcular los pasos intermedios: {str(e)}")
        return {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}

def direct_laplace(func_str):
    try:
        t, s = sp.symbols('t s')
        func_str = preprocess_input(func_str)
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        f = parse_expr(func_str, transformations=transformations, local_dict={'t': t, 's': s})
        f = sp.expand(f)
        result = sp.laplace_transform(f, t, s, noconds=True)
        steps = compute_steps(func_str, t, s, calc_type='directa')
        return format_result(result), steps
    except Exception as e:
        print(f"Error al calcular la transformada directa: {str(e)}")
        return f"\\text{{Error: No se pudo calcular la transformada directa de }} {sp.latex(func_str)}", {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}

def inverse_laplace(func_str):
    try:
        s, t = sp.symbols('s t')
        func_str = preprocess_input(func_str)
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        F = parse_expr(func_str, transformations=transformations, local_dict={'t': t, 's': s})
        F = sp.expand(F)
        result = sp.inverse_laplace_transform(F, s, t, noconds=True)
        steps = compute_steps(func_str, t, s, calc_type='inversa')
        return format_inverse_result(result), steps
    except Exception as e:
        print(f"Error al calcular la transformada inversa: {str(e)}")
        return f"\\text{{Error: No se pudo calcular la transformada inversa de }} {sp.latex(func_str)}", {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}