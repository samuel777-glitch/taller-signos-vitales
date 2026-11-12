"""primer punto del taller: generar y ordenar registros ficticios"""

import random


def generar_registros(cantidad=50):
    """crea registros con los formatos solicitados en el taller"""
    registros = []

    for numero in range(1, cantidad + 1):
        registro = {
            "id": f"ID-{numero:03d}",
            "fr": f"{random.randint(18, 90)} Años",
            "fc": f"{random.randint(50, 140):03d}ppm",
            "spo2": f"{random.randint(85, 100)}%",
        }
        registros.append(registro)

    return registros


def obtener_frecuencia(registro):
    """convierte, por ejemplo, '090ppm' en el numero 90"""
    return int(registro["fc"].removesuffix("ppm"))


def ordenar_por_frecuencia(registros):
    """devuelve una lista nueva, ordenada de menor a mayor frecuencia"""
    return sorted(registros, key=obtener_frecuencia)


def mostrar_registros(registros):
    """presenta los registros como una tabla en la consola"""
    print(f"{'id':<10}{'edad (fr)':<14}{'fc':<12}{'spo2':<8}")
    print("-" * 44)
    for registro in registros:
        print(
            f"{registro['id']:<10}{registro['fr']:<14}"
            f"{registro['fc']:<12}{registro['spo2']:<8}"
        )
