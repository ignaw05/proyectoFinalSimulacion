import os
import time
import csv
import hashlib
from main import capture, hashImages, generateRandomNumberSet
from tests_estadisticos import anderson_darling_uniform, nist_runs_test

def main():
    print("=" * 70)
    print("EJECUCIÓN DEL PIPELINE COMPLETO: CAPTURA, GENERACIÓN Y PRUEBAS")
    print("=" * 70)
    
    # 1. Capturar imágenes y obtener el hash
    combined_hash = ""
    try:
        # Intentamos realizar la captura (requiere playwright y conexión)
        capture(5, "imagen")
        combined_hash = hashImages()
    except Exception as e:
        print(f"\n[Aviso] No se pudo realizar la captura web (puede faltar Playwright o conexión): {e}")
        print("Procediendo con un hash alternativo usando la marca de tiempo local.")
        
    if not combined_hash:
        fallback_data = str(time.time()).encode('utf-8')
        combined_hash = hashlib.sha256(fallback_data).hexdigest()
        print(f"Hash derivado: {combined_hash}")
    else:
        print(f"Hash combinado de capturas: {combined_hash}")
        
    # 2. Obtener la semilla a partir del hash
    # Convertimos el hash hexadecimal en entero y aplicamos módulo 180
    seed = int(combined_hash, 16) % 180
    print(f"Semilla calculada (Hash % 180): {seed}")
    
    # 3. Generar el conjunto de 180 números pseudoaleatorios
    print("\nGenerando 180 números pseudoaleatorios usando el Generador Congruencial Lineal...")
    numbers = generateRandomNumberSet(seed, 180)
    
    # Guardar los números generados a un CSV
    csv_filename = "numeros_generados.csv"
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for num in numbers:
                writer.writerow([num])
        print(f"Números guardados exitosamente en: {csv_filename}")
    except Exception as e:
        print(f"Error al escribir el archivo CSV: {e}")
    
    # 4. Ejecutar las pruebas estadísticas sobre los números generados
    print("\nEjecutando las pruebas de Anderson-Darling y NIST Runs Test...")
    
    # Anderson-Darling para uniformidad
    ad_accepted, ad_stat = anderson_darling_uniform(numbers, alpha=0.05)
    
    # NIST Runs Test para independencia
    nist_accepted, p_val, freq_passed = nist_runs_test(numbers, alpha=0.01)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS DEL PIPELINE")
    print("="*70)
    print(f"1. Test de Anderson-Darling (Uniformidad): {'ACEPTADO' if ad_accepted else 'RECHAZADO'}")
    print(f"2. Test de Rachas del NIST (Independencia): {'ACEPTADO' if nist_accepted else 'RECHAZADO'}")
    
    if ad_accepted and nist_accepted:
        print("\n>>> DICTAMEN FINAL: LA SECUENCIA GENERADA ACEPTA AMBOS TEST. <<<")
    else:
        print("\n>>> DICTAMEN FINAL: LA SECUENCIA NO ACEPTA AMBOS TEST. <<<")
        if not ad_accepted:
            print("    - Falló el test de Anderson-Darling para Uniformidad.")
        if not nist_accepted:
            print("    - Falló el test de Rachas del NIST para Independencia.")
    print("="*70)

if __name__ == "__main__":
    main()
