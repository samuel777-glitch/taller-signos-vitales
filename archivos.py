"""guarda y recupera registros en archivos"""

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from datos import ordenar_por_frecuencia
from validacion import validar_registros


BASE = Path(__file__).resolve().parent
CAMPOS = ["id", "fr", "fc", "spo2"]


def registrar_accion(mensaje, base=BASE):
    """agrega una accion al log sin detener el programa si falla"""
    try:
        with (Path(base) / "log.txt").open("a", encoding="utf-8") as archivo:
            fecha = datetime.now().isoformat(timespec="seconds")
            archivo.write(f"{fecha} - {mensaje}\n")
    except OSError:
        print("no se pudo actualizar el registro de acciones")


def crear_carpetas(base=BASE):
    for formato in ("txt", "csv", "json"):
        (Path(base) / "data" / formato).mkdir(parents=True, exist_ok=True)
    registrar_accion("carpetas de datos verificadas", base)


def comprobar_registros(registros):
    if not isinstance(registros, list):
        raise ValueError("los datos deben ser una lista de registros")
    errores = validar_registros(registros)
    for posicion, registro in enumerate(registros, start=1):
        if isinstance(registro, dict) and set(registro) != set(CAMPOS):
            errores.append(f"registro {posicion}: los campos deben ser id, fr, fc y spo2")
    if errores:
        raise ValueError("\n".join(errores))


def exportar_archivos(registros, base=BASE):
    """valida y guarda los tres formatos ordenados por frecuencia"""
    comprobar_registros(registros)
    crear_carpetas(base)
    ordenados = ordenar_por_frecuencia(registros)
    rutas = []
    # los archivos se preparan y luego se mueven a su carpeta
    with TemporaryDirectory(dir=base) as temporal:
        for formato in ("txt", "csv", "json"):
            origen = Path(temporal) / f"signos_vitales.{formato}"
            with origen.open("w", encoding="utf-8", newline="") as archivo:
                if formato == "json":
                    json.dump(ordenados, archivo, ensure_ascii=False, indent=4)
                else:
                    separador = "\t" if formato == "txt" else ","
                    escritor = csv.DictWriter(archivo, fieldnames=CAMPOS, delimiter=separador)
                    escritor.writeheader()
                    escritor.writerows(ordenados)
            destino = Path(base) / "data" / formato / origen.name
            shutil.move(str(origen), str(destino))
            rutas.append(destino)
            registrar_accion(f"exportacion {formato} completada con {len(ordenados)} registros", base)
    return rutas


def importar_archivo(ruta, base=BASE):
    """lee y valida todo el archivo antes de devolver sus registros"""
    ruta = Path(ruta).expanduser()
    if not ruta.is_absolute():
        ruta = Path(base) / ruta
    if not ruta.is_file():
        raise FileNotFoundError("no se encontro el archivo indicado")
    formato = ruta.suffix.lower()
    if formato not in (".txt", ".csv", ".json"):
        raise ValueError("elige un archivo txt, csv o json")

    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        if formato == ".json":
            registros = json.load(archivo)
        else:
            separador = "\t" if formato == ".txt" else ","
            lector = csv.DictReader(archivo, delimiter=separador, strict=True)
            if lector.fieldnames != CAMPOS:
                raise ValueError("el encabezado debe contener id, fr, fc y spo2 en ese orden")
            registros = list(lector)

    comprobar_registros(registros)
    registrar_accion(f"importacion completada con {len(registros)} registros", base)
    return ordenar_por_frecuencia(registros)
