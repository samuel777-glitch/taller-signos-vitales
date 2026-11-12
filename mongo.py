"""conexion y consultas de mongodb"""

import json
import os
import re

from archivos import BASE, comprobar_registros, crear_carpetas, registrar_accion


def conectar():
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
    except ImportError:
        raise RuntimeError("instala las dependencias indicadas en requirements") from None

    load_dotenv(BASE / ".env")
    uri = os.getenv("MONGODB_URI", "")
    if not uri:
        raise ValueError("falta configurar la conexion en el archivo de entorno")
    cliente = MongoClient(uri, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    try:
        cliente.admin.command("ping")
        coleccion = cliente[os.getenv("MONGODB_DATABASE", "taller_informatica")]["signos_vitales"]
        coleccion.create_index("id", unique=True)
    except Exception:
        cliente.close()
        raise
    registrar_accion("conexion con mongodb completada")
    return cliente, coleccion


def insertar_registros(coleccion, registros):
    comprobar_registros(registros)
    insertados = 0
    for registro in registros:
        documento = dict(registro)
        documento["fc_num"] = int(registro["fc"][:-3])
        documento["spo2_num"] = int(registro["spo2"][:-1])
        resultado = coleccion.update_one(
            {"id": registro["id"]}, {"$setOnInsert": documento}, upsert=True
        )
        if resultado.upserted_id is not None:
            insertados += 1
    registrar_accion(f"mongodb inserto {insertados} registros nuevos")
    return insertados


def consultar_id(coleccion, identificacion):
    if re.fullmatch(r"ID-[0-9]{3}", identificacion) is None:
        raise ValueError("el id debe tener el formato indicado, ejemplo: ID-001")
    return coleccion.find_one({"id": identificacion}, {"_id": 0})


def consultar_resultados(coleccion):
    promedio = list(coleccion.aggregate([
        {"$group": {"_id": None, "promedio": {"$avg": "$fc_num"}}}
    ]))
    bajos = list(coleccion.find({"spo2_num": {"$lt": 94}}, {"_id": 0}).sort("id", 1))
    return {
        "promedio_fc": promedio[0]["promedio"] if promedio else None,
        "spo2_menor_94": bajos,
    }


def exportar_resultados(resultados, base=BASE):
    crear_carpetas(base)
    ruta = base / "data" / "json" / "resultados_mongo.json"
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, ensure_ascii=False, indent=4)
    registrar_accion("resultados de mongodb exportados", base)
    return ruta


def menu_mongo(registros):
    cliente = None
    try:
        cliente, coleccion = conectar()
        print("conexion lista")
        while True:
            print("\n1 - insertar registros actuales sin reemplazar los ids existentes")
            print("2 - consultar por id")
            print("3 - consultar promedio y saturacion, y exportar resultados")
            print("0 - volver")
            opcion = input("elige una opcion: ").strip()
            if opcion == "1":
                cantidad = insertar_registros(coleccion, registros)
                print(f"registros nuevos: {cantidad}, ids existentes omitidos: {len(registros) - cantidad}")
            elif opcion == "2":
                identificacion = input("id a consultar, ejemplo ID-001: ").strip()
                try:
                    registro = consultar_id(coleccion, identificacion)
                    print(registro if registro else "no se encontro ese id")
                    registrar_accion("consulta de mongodb por id")
                except ValueError as error:
                    print(error)
            elif opcion == "3":
                resultados = consultar_resultados(coleccion)
                promedio = resultados["promedio_fc"]
                print(f"promedio de frecuencia: {promedio}" if promedio is not None else "no hay registros para calcular el promedio")
                print(f"registros con saturacion menor a 94: {len(resultados['spo2_menor_94'])}")
                for registro in resultados["spo2_menor_94"]:
                    print(registro)
                exportar_resultados(resultados)
                print("resultados guardados")
            elif opcion == "0":
                break
            else:
                print("opcion incorrecta")
    except (ImportError, RuntimeError, ValueError, OSError):
        print("no se completo la operacion, revisa la configuracion y las dependencias")
        registrar_accion("error de configuracion o archivos en mongodb")
    except Exception:
        # no se imprime el error del servidor para evitar mostrar credenciales
        print("fallo la operacion de mongodb, revisa la conexion, el usuario y el acceso de red")
        print("si estabas insertando, algunos registros pueden haberse guardado")
        registrar_accion("error en operacion de mongodb")
    finally:
        if cliente is not None:
            cliente.close()

