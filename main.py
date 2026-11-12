"""integra datos, validacion, archivos y mongodb en un menu"""

from datos import generar_registros, mostrar_registros, ordenar_por_frecuencia
from validacion import ingresar_registro, validar_registros
import csv
from archivos import crear_carpetas, exportar_archivos, importar_archivo, registrar_accion
from mongo import menu_mongo


def main():
    try:
        crear_carpetas()
    except OSError:
        print("no se pudieron crear las carpetas, revisa los permisos")
        return
    registros = generar_registros(50)
    registrar_accion("inicio del programa y generacion de 50 registros")
    print("signos vitales: datos ficticios\n")
    while True:
        print("\n1 - mostrar registros ordenados")
        print("2 - ingresar un registro")
        print("3 - validar todos los registros")
        print("4 - exportar txt, csv y json")
        print("5 - importar un archivo y reemplazar los registros actuales")
        print("6 - conectar con mongodb y ejecutar consultas")
        print("0 - salir")
        opcion = input("elige una opcion: ").strip()

        if opcion == "1":
            mostrar_registros(ordenar_por_frecuencia(registros))
            print(f"\ntotal de registros: {len(registros)}")
        elif opcion == "2":
            registro = ingresar_registro(registros)
            if registro is not None:
                registros.append(registro)
                registrar_accion("registro agregado")
                print("registro agregado correctamente")
        elif opcion == "3":
            errores = validar_registros(registros)
            registrar_accion(f"validacion completada con {len(errores)} errores")
            if errores:
                for error in errores:
                    print(f"- {error}")
            else:
                print(f"los {len(registros)} registros son validos")
        elif opcion in ("4", "5"):
            try:
                if opcion == "4":
                    rutas = exportar_archivos(registros)
                    print("archivos guardados, se reemplazan las exportaciones anteriores")
                    for ruta in rutas:
                        print(ruta)
                else:
                    ruta = input("ruta del archivo, vacio para cancelar: ").strip()
                    if ruta:
                        nuevos = importar_archivo(ruta)
                        registros = nuevos
                        print(f"importacion correcta, total de registros: {len(registros)}")
            except (OSError, ValueError, UnicodeError, csv.Error) as error:
                print(f"no se completo la operacion: {error}")
                registrar_accion("error en operacion de archivos")
        elif opcion == "6":
            menu_mongo(registros)
        elif opcion == "0":
            registrar_accion("salida del programa")
            print("programa finalizado")
            break
        else:
            print("opcion incorrecta, elige un numero entre 0 y 6")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nprograma finalizado")
