import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Cambiar el backend a Agg (no interactivo)
import matplotlib.pyplot as plt
import io
import base64
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

def preprocess_input(func_str):
    # Normaliza la entrada para que sea compatible con SymPy
    func_str = func_str.strip().lower()
    
    # Reemplaza 'e^' con 'exp(' y ajusta paréntesis
    if 'e^' in func_str:
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
    
    # Asegura multiplicación implícita y otras transformaciones
    transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
    return func_str

def generate_plot(func_str, calc_type):
    try:
        plt.figure(figsize=(6, 4))
        
        if calc_type == 'directa':
            t = sp.symbols('t')
            func_str = preprocess_input(func_str)
            transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
            f = parse_expr(func_str, transformations=transformations, local_dict={'t': t})
            t_vals = np.linspace(-10, 10, 400)
            f_vals = [float(f.subs(t, val)) if f.subs(t, val).is_real else 0 for val in t_vals]
            plt.plot(t_vals, f_vals, label='f(t)', color='#3b82f6')
        elif calc_type == 'inversa':
            s = sp.symbols('s')
            func_str = preprocess_input(func_str)
            transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
            F = parse_expr(func_str, transformations=transformations, local_dict={'s': s})
            s_vals = np.linspace(-10, 10, 400)
            F_vals = [float(F.subs(s, val)) if F.subs(s, val).is_real else 0 for val in s_vals]
            plt.plot(s_vals, F_vals, label='F(s)', color='#ef4444', linestyle='--')
        
        plt.axhline(0, color='gray', lw=0.5)
        plt.axvline(0, color='gray', lw=0.5)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return img_str
    except Exception as e:
        # Manejo de errores: devolver None y registrar el error
        print(f"Error al generar la gráfica: {str(e)}")
        return None