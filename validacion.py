"""validacion de formatos e ingreso de registros por consola"""

import re


PATRONES = {
    "id": r"ID-[0-9]{3}",
    "fr": r"[0-9]{1,3} Años",
    "fc": r"[0-9]{3}ppm",
    "spo2": r"[0-9]{1,3}%",
}

EJEMPLOS = {"id": "ID-051", "fr": "18 Años", "fc": "090ppm", "spo2": "95%"}


def validar_registro(registro):
    """devuelve los errores encontrados; una lista vacia indica exito"""
    if not isinstance(registro, dict):
        return ["el registro debe ser un diccionario"]

    errores = []
    for campo, patron in PATRONES.items():
        valor = registro.get(campo)
        if not isinstance(valor, str) or re.fullmatch(patron, valor) is None:
            errores.append(f"formato incorrecto en {campo}, ejemplo: {EJEMPLOS[campo]}")
        elif campo == "spo2" and int(valor[:-1]) > 100:
            errores.append("la saturacion debe estar entre 0 y 100%")
    return errores


def validar_registros(registros):
    """revisa formatos e identificaciones repetidas en una lista"""
    errores = []
    identificaciones = set()
    for posicion, registro in enumerate(registros, start=1):
        for error in validar_registro(registro):
            errores.append(f"registro {posicion}: {error}")
        if isinstance(registro, dict):
            identificacion = registro.get("id")
            if isinstance(identificacion, str):
                if identificacion in identificaciones:
                    errores.append(f"registro {posicion}: id repetido ({identificacion})")
                identificaciones.add(identificacion)
    return errores


def ingresar_registro(registros):
    """solicita un registro y repite la entrada si hay errores vacio cancela"""
    while True:
        registro = {}
        print("\ningresa los campos con el formato indicado, deja uno vacio para cancelar")
        for campo in PATRONES:
            valor = input(f"{campo} (ejemplo: {EJEMPLOS[campo]}): ").strip()
            if not valor:
                print("ingreso cancelado")
                return None
            registro[campo] = valor

        errores = validar_registro(registro)
        if any(r["id"] == registro["id"] for r in registros):
            errores.append("la identificacion ya existe, usa otra")
        if not errores:
            return registro
        for error in errores:
            print(f"- {error}")
        print("vuelve a ingresar el registro")
