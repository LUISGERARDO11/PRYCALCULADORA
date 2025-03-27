import numpy as np

def solve_with_rk4(r, A, T, phi, P0, t_start, t_end, h):
    """
    Resuelve la EDO dP/dt = r*P + A*sin(2*pi/T*(t-phi)) usando RK4.
    
    Args:
        r (float): Tasa de crecimiento continuo.
        A (float): Amplitud de la componente estacional.
        T (float): Período de estacionalidad.
        phi (float): Desplazamiento de fase (en meses).
        P0 (float): Condición inicial P(t_start).
        t_start (float): Tiempo inicial.
        t_end (float): Tiempo final.
        h (float): Paso de tiempo.
    
    Returns:
        tuple: (P_values, t_values, steps, quarterly_values, total_2025)
    """
    try:
        t_values = np.arange(t_start, t_end + h, h)
        P_values = [P0]
        steps = {
            'step1': [],  # Ecuación ingresada
            'step2': '',  # Tipo de ecuación
            'step3': [],  # Método utilizado
            'step4': [],  # Resolución paso a paso
            'step5': ''   # Solución final
        }

        # Paso 1: Mostrar la ecuación
        steps['step1'].append(
            f"\\text{{Ecuación ingresada: }} \\frac{{dP}}{{dt}} = {r}P + {A}\\sin\\left(\\frac{{2\\pi}}{{{T}}}(t - {phi})\\right)"
        )

        # Paso 2: Identificar el tipo de ecuación
        steps['step2'] = "\\text{{Ecuación diferencial de primer orden con término estacional no lineal.}}"

        # Paso 3: Método utilizado
        steps['step3'].append("\\text{{Resolvemos usando el método numérico Runge-Kutta de orden 4 (RK4).}}")

        # Implementar RK4
        for i in range(len(t_values) - 1):
            t = t_values[i]
            P = P_values[-1]

            # Calcular las pendientes k1, k2, k3, k4
            k1 = r * P + A * np.sin(2 * np.pi / T * (t - phi))
            k2 = r * (P + h/2 * k1) + A * np.sin(2 * np.pi / T * ((t + h/2) - phi))
            k3 = r * (P + h/2 * k2) + A * np.sin(2 * np.pi / T * ((t + h/2) - phi))
            k4 = r * (P + h * k3) + A * np.sin(2 * np.pi / T * ((t + h) - phi))

            # Actualizar P(t)
            P_next = P + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
            P_values.append(P_next)

            # Registrar pasos intermedios (solo para los primeros 3 pasos como ejemplo)
            if i < 3:
                steps['step4'].append(f"\\text{{Paso {i+1} (t={t} → t={t+h}):}}")
                steps['step4'].append(f"\\text{{k1 = {r} \\cdot {P:.2f} + {A} \\cdot \\sin(2\\pi/{T} \\cdot ({t} - {phi})) = {k1:.2f}}}")
                steps['step4'].append(f"\\text{{k2 = {r} \\cdot ({P:.2f} + {h/2} \\cdot {k1:.2f}) + {A} \\cdot \\sin(2\\pi/{T} \\cdot ({t} + {h/2} - {phi})) = {k2:.2f}}}")
                steps['step4'].append(f"\\text{{k3 = {r} \\cdot ({P:.2f} + {h/2} \\cdot {k2:.2f}) + {A} \\cdot \\sin(2\\pi/{T} \\cdot ({t} + {h/2} - {phi})) = {k3:.2f}}}")
                steps['step4'].append(f"\\text{{k4 = {r} \\cdot ({P:.2f} + {h} \\cdot {k3:.2f}) + {A} \\cdot \\sin(2\\pi/{T} \\cdot ({t} + {h} - {phi})) = {k4:.2f}}}")
                steps['step4'].append(f"\\text{{P({t+h}) = {P:.2f} + ({h}/6) \\cdot ({k1:.2f} + 2 \\cdot {k2:.2f} + 2 \\cdot {k3:.2f} + {k4:.2f}) = {P_next:.2f}}}")

        # Índices para los puntos finales de los trimestres de 2025 (t=15, 18, 21, 24)
        indices_pred = [int(t/h) for t in [15, 18, 21, 24]]
        quarterly_values = {
            'Q1_2025': P_values[indices_pred[0]],  # t=15 (Marzo 2025)
            'Q2_2025': P_values[indices_pred[1]],  # t=18 (Junio 2025)
            'Q3_2025': P_values[indices_pred[2]],  # t=21 (Septiembre 2025)
            'Q4_2025': P_values[indices_pred[3]],  # t=24 (Diciembre 2025)
        }
        total_2025 = sum(quarterly_values.values())

        # Paso 5: Solución final
        steps['step5'] = (
            f"\\text{{Predicciones para 2025: Q1 = {quarterly_values['Q1_2025']:.2f}, "
            f"Q2 = {quarterly_values['Q2_2025']:.2f}, Q3 = {quarterly_values['Q3_2025']:.2f}, "
            f"Q4 = {quarterly_values['Q4_2025']:.2f}, Total = {total_2025:.2f}}}"
        )

        return P_values, t_values, steps, quarterly_values, total_2025

    except Exception as e:
        print(f"Error al resolver con RK4: {str(e)}")
        return None, None, {'step1': [], 'step2': '', 'step3': [], 'step4': [], 'step5': ''}, {}, 0