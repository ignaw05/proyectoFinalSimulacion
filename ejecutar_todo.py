import subprocess
import sys

def main():
    print("=" * 70)
    print("EJECUCIÓN DEL PIPELINE COMPLETO: CORRIENDO MAIN.PY Y PRUEBAS")
    print("=" * 70)
    
    # 1. Ejecutar main.py para generar y combinar los números pseudoaleatorios
    try:
        print("Ejecutando main.py...")
        subprocess.run([sys.executable, "main.py"], check=True)
        print("main.py ejecutado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar main.py: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 70)
    # 2. Ejecutar las pruebas estadísticas sobre cada archivo individual generado
    archivos = ["porcentajeACargarU.csv", "cargaInicialU.csv", "tipoAutonomiaU.csv"]
    for archivo in archivos:
        print("\n" + "=" * 70)
        try:
            print(f"Ejecutando pruebas estadísticas sobre {archivo}...")
            subprocess.run([sys.executable, "tests_estadisticos.py", archivo], check=True)
            print(f"Pruebas sobre {archivo} completadas con éxito.")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar las pruebas estadísticas sobre {archivo}: {e}")
            sys.exit(1)
        
    print("=" * 70)

if __name__ == "__main__":
    main()
