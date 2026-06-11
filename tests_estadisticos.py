import sys
import os
import math

def load_numbers_from_csv(file_path):
    """
    Lee un archivo CSV y extrae los números flotantes.
    Soporta varios delimitadores (comas, punto y coma, tabuladores, saltos de línea).
    Ignora encabezados y texto que no sea numérico.
    """
    numbers = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo '{file_path}' no existe.")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Reemplazar delimitadores comunes por espacios para separar fácilmente
            cleaned_line = line.replace(',', ' ').replace(';', ' ').replace('\t', ' ')
            for part in cleaned_line.split():
                try:
                    num = float(part)
                    numbers.append(num)
                except ValueError:
                    # Ignorar filas de texto/encabezados
                    continue
    return numbers

def anderson_darling_uniform(data, alpha=0.05):
    """
    Realiza la prueba de Anderson-Darling para uniformidad U(0, 1).
    Usa el Caso 0 de Stephens (parámetros conocidos y fijos).
    """
    n = len(data)
    # Ordenar los datos ascendentemente
    y = sorted(data)
    
    print("\n" + "="*70)
    print("PRUEBA DE ANDERSON-DARLING (UNIFORMIDAD U(0,1))")
    print("="*70)
    print(f"Objetivo: Evaluar si los datos siguen una distribución Uniforme en (0,1).")
    print(f"H0: Los datos provienen de una distribución U(0,1).")
    print(f"H1: Los datos NO provienen de una distribución U(0,1).")
    print("-"*70)
    
    print(f"Paso 1: Ordenar los {n} números pseudoaleatorios.")
    print(f"  Primeros 5 datos ordenados: {[f'{val:.6f}' for val in y[:5]]}")
    print(f"  Últimos 5 datos ordenados: {[f'{val:.6f}' for val in y[-5:]]}")
    
    # Validar que estén en el rango (0, 1)
    if any(val < 0 or val > 1 for val in y):
        raise ValueError("Error: Todos los números pseudoaleatorios deben estar en el intervalo [0, 1].")
        
    print("\nPaso 2: Aplicar la fórmula del estadístico A^2.")
    print("  Fórmula: A^2 = -n - (1/n) * sum_{i=1}^{n} [ (2i - 1)*ln(y_i) + (2n + 1 - 2i)*ln(1 - y_i) ]")
    
    total_sum = 0.0
    eps = 1e-15  # Evitar logaritmo de cero si hay valores extremos
    
    print("\n  Cálculo detallado de los términos (primeros y últimos 3 como ejemplo):")
    for i in range(1, n + 1):
        val = y[i - 1]
        val_clipped = min(max(val, eps), 1 - eps)
        
        term1 = (2 * i - 1) * math.log(val_clipped)
        term2 = (2 * n + 1 - 2 * i) * math.log(1 - val_clipped)
        term_total = term1 + term2
        total_sum += term_total
        
        if i <= 3 or i >= n - 2:
            print(f"    i = {i:3d}: y_({i}) = {val:.6f} -> (2*i-1)*ln(y_i) = {term1:.6f}, (2n+1-2i)*ln(1-y_i) = {term2:.6f} -> Suma término = {term_total:.6f}")
        elif i == 4:
            print("    ...")
            
    a2 = -n - (total_sum / n)
    print(f"\n  Suma acumulada de todos los términos: {total_sum:.6f}")
    print(f"  Estadístico calculado A^2 = -{n} - ({total_sum:.6f} / {n}) = {a2:.6f}")
    
    # Valores críticos asintóticos de Stephens para Caso 0 (parámetros conocidos)
    # Para alpha = 0.05, el valor crítico es 2.492
    critical_values = {
        0.10: 1.933,
        0.05: 2.492,
        0.025: 3.070,
        0.01: 3.857
    }
    
    cv = critical_values.get(alpha, 2.492)
    print(f"\nPaso 3: Comparación con el valor crítico.")
    print(f"  Nivel de significancia (alpha): {alpha}")
    print(f"  Valor crítico de Stephens (Caso 0): {cv}")
    
    accepted = a2 <= cv
    if accepted:
        print(f"  Conclusión: A^2 ({a2:.6f}) <= {cv}. NO se rechaza H0.")
        print("  => Se acepta la hipótesis de uniformidad.")
    else:
        print(f"  Conclusión: A^2 ({a2:.6f}) > {cv}. SE RECHAZA H0.")
        print("  => NO se acepta la hipótesis de uniformidad.")
        
    return accepted, a2

def nist_runs_test(data, alpha=0.01):
    """
    Realiza la prueba de rachas del NIST (NIST Runs Test) para independencia.
    Sigue las especificaciones del estándar NIST SP 800-22.
    """
    n = len(data)
    
    print("\n" + "="*70)
    print("PRUEBA DE RACHAS DEL NIST (NIST RUNS TEST - INDEPENDENCIA)")
    print("="*70)
    print("Objetivo: Determinar si la oscilación entre 0s y 1s es la esperada para una secuencia aleatoria.")
    print("H0: La secuencia de bits es independiente (aleatoria).")
    print("H1: La secuencia de bits NO es independiente (no aleatoria).")
    print("-"*70)
    
    print("Paso 1: Convertir la secuencia de números continuos a binaria usando el umbral 0.5.")
    print("  Regla: x_i = 1 si y_i >= 0.5; x_i = 0 si y_i < 0.5")
    
    binary_seq = [1 if val >= 0.5 else 0 for val in data]
    print(f"  Primeros 25 bits: {binary_seq[:25]}")
    print(f"  Últimos 25 bits:  {binary_seq[-25:]}")
    
    # Prerrequisito: Test de Frecuencia Monobit (NIST SP 800-22 Sección 2.2)
    ones_count = sum(binary_seq)
    pi = ones_count / n
    print(f"\nPaso 2: Verificar el prerrequisito del test de frecuencia monobit.")
    print(f"  Proporción de unos (pi) = {ones_count} / {n} = {pi:.6f}")
    
    freq_diff = abs(pi - 0.5)
    freq_threshold = 2.0 / math.sqrt(n)
    print(f"  Diferencia absoluta |pi - 0.5| = {freq_diff:.6f}")
    print(f"  Umbral mínimo de frecuencia: 2 / sqrt({n}) = {freq_threshold:.6f}")
    
    freq_passed = freq_diff < freq_threshold
    if not freq_passed:
        print("  ADVERTENCIA: La secuencia no cumple con el prerrequisito del test de frecuencia.")
        print("  Según la especificación NIST SP 800-22, la prueba de rachas no debería considerarse")
        print("  confiable y la secuencia se marca como fallida en este aspecto.")
    else:
        print("  Prerrequisito de frecuencia CUMPLIDO.")
        
    print("\nPaso 3: Calcular el número total de rachas observado (V_n).")
    print("  Una racha es una secuencia consecutiva de bits idénticos.")
    
    # Contar las rachas
    runs = 1
    for i in range(1, n):
        if binary_seq[i] != binary_seq[i-1]:
            runs += 1
            
    print(f"  Número de rachas observado V_n(obs): {runs}")
    
    print("\nPaso 4: Calcular el P-value usando la función de error complementaria (erfc).")
    print("  Fórmula: P-value = erfc( |V_n - 2*n*pi*(1-pi)| / (2 * sqrt(2*n) * pi * (1-pi)) )")
    
    numerator = abs(runs - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    
    if denominator == 0:
        p_val = 0.0
        print("  Error: El denominador es 0 (la secuencia tiene solo ceros o solo unos).")
    else:
        z = numerator / denominator
        p_val = math.erfc(z)
        print(f"  Numerador: |{runs} - 2 * {n} * {pi:.4f} * {1-pi:.4f}| = {numerator:.6f}")
        print(f"  Denominador: 2 * sqrt(2 * {n}) * {pi:.4f} * {1-pi:.4f} = {denominator:.6f}")
        print(f"  Argumento z = Numerador / Denominador = {z:.6f}")
        print(f"  P-value = erfc({z:.6f}) = {p_val:.6f}")
        
    print(f"\nPaso 5: Comparar P-value con el nivel de significancia (alpha = {alpha}).")
    accepted = p_val >= alpha
    
    if accepted:
        print(f"  Conclusión: P-value ({p_val:.6f}) >= alpha ({alpha}). NO se rechaza H0.")
        print("  => Se acepta la hipótesis de independencia.")
    else:
        print(f"  Conclusión: P-value ({p_val:.6f}) < alpha ({alpha}). SE RECHAZA H0.")
        print("  => NO se acepta la hipótesis de independencia.")
        
    return accepted, p_val, freq_passed

def main():
    if len(sys.argv) < 2:
        print("Uso: python tests_estadisticos.py <ruta_del_archivo.csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    try:
        data = load_numbers_from_csv(file_path)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)
        
    n = len(data)
    print("="*70)
    print("ANÁLISIS ESTADÍSTICO DE NÚMEROS PSEUDOALEATORIOS")
    print("="*70)
    print(f"Archivo de entrada: {file_path}")
    print(f"Cantidad de datos leídos: {n}")
    
    # Requerir al menos 180 datos o ajustar a los primeros 180
    if n < 180:
        print(f"Error: El archivo contiene únicamente {n} números. Se requieren al menos 180 para el análisis solicitado.")
        sys.exit(1)
    elif n > 180:
        print(f"Aviso: El archivo contiene {n} números. Para cumplir la especificación, usaremos los primeros 180 números.")
        data = data[:180]
        n = 180
        
    # Ejecutar Anderson-Darling para uniformidad
    ad_accepted, ad_stat = anderson_darling_uniform(data, alpha=0.05)
    
    # Ejecutar NIST Runs Test para independencia
    nist_accepted, p_val, freq_passed = nist_runs_test(data, alpha=0.01)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)
    print(f"1. Test de Anderson-Darling (Uniformidad): {'ACEPTADO' if ad_accepted else 'RECHAZADO'}")
    print(f"2. Test de Rachas del NIST (Independencia): {'ACEPTADO' if nist_accepted else 'RECHAZADO'}")
    
    # Verificar si cumple con todo
    if ad_accepted and nist_accepted:
        print("\n>>> DICTAMEN FINAL: LA SECUENCIA DE NÚMEROS PSEUDOALEATORIOS ACEPTA AMBOS TEST. <<<")
    else:
        print("\n>>> DICTAMEN FINAL: LA SECUENCIA NO ACEPTA AMBOS TEST. <<<")
        if not ad_accepted:
            print("    - Falló el test de Anderson-Darling para Uniformidad.")
        if not nist_accepted:
            print("    - Falló el test de Rachas del NIST para Independencia.")
            
    print("="*70)

if __name__ == "__main__":
    main()
