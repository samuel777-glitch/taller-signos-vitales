# taller de signos vitales

actividad de informatica 1, unidades 3 y 4 desarrollo por etapas en python

## etapa 1: generacion y ordenamiento

el programa genera 50 registros ficticios y los presenta ordenados por frecuencia
cardiaca, de menor a mayor solo utiliza la biblioteca estandar de python

requiere python `3.9` o posterior desde la carpeta del proyecto, ejecutar:

```sh
python main.py
```

### campos

| campo | significado | ejemplo |
| --- | --- | --- |
| `id` | identificacion del registro | `ID-001` |
| `fr` | edad, conservando el nombre indicado por el taller | `18 Años` |
| `fc` | frecuencia cardiaca | `090ppm` |
| `spo2` | saturacion periferica de oxigeno | `95%` |

los intervalos elegidos para generar ejemplos son: edad de 18 a 90 anos,
frecuencia de 50 a 140 ppm y saturacion de 85 a 100 % son decisiones para
la simulacion, no limites clinicos ni requisitos adicionales del enunciado
se incluyen saturaciones menores de 94 para facilitar las consultas posteriores

### como funciona

1 - `generar_registros` usa un ciclo y numeros aleatorios para crear la lista
2 - `obtener_frecuencia` elimina el sufijo `ppm` y convierte el resultado a entero
3 - `ordenar_por_frecuencia` usa `sorted` con esa frecuencia como criterio
4 - `mostrar_registros` imprime una tabla con los cuatro campos

los identificadores se asignan antes de ordenar, por lo que sus numeros no
necesariamente aparecen en orden en la tabla cada ejecucion genera datos nuevos

## etapa 2: validacion e ingreso

`validacion.py` usa `re.fullmatch` para comprobar todo el contenido de cada
campo exige id con tres digitos, edad con uno a tres digitos y el sufijo
` Años`, frecuencia con tres digitos y `ppm`, y saturacion con uno a tres
digitos y `%` solo acepta digitos del 0 al 9

como comprobaciones adicionales, rechaza saturaciones mayores de 100% e
identificaciones repetidas no se aplican los intervalos de generacion como
restricciones de entrada ni se pretende hacer una evaluacion clinica

el menu permite mostrar los registros, ingresar uno nuevo, validar la lista o
salir si una entrada tiene errores, se explican y se pide de nuevo; dejar un
campo vacio cancela el ingreso

## etapa 3: archivos y carpetas

la opcion 4 guarda los registros ordenados en estos archivos y reemplaza
las exportaciones anteriores

- `data/txt/signos_vitales.txt`
- `data/csv/signos_vitales.csv`
- `data/json/signos_vitales.json`

el txt usa columnas separadas por tabulaciones y el csv usa comas
ambos tienen un encabezado con `id`, `fr`, `fc` y `spo2`
el json contiene una lista de registros

las carpetas se crean junto al programa usando pathlib
los archivos se preparan en una carpeta temporal y se mueven automaticamente
a la carpeta del formato correspondiente

la opcion 5 lee cualquiera de los tres formatos y reemplaza la lista actual
solo cuando todos los datos son validos
puedes escribir una ruta completa o una ruta relativa a la carpeta del proyecto
por ejemplo `data/json/signos_vitales.json`
dejar la ruta vacia cancela la importacion

se comprueban las rutas, los campos, los formatos y los ids repetidos
los errores de lectura o escritura se muestran sin cerrar el menu
si una exportacion falla despues de guardar un formato, ese archivo puede
quedar actualizado aunque los siguientes no se hayan guardado

`log.txt` guarda la fecha y hora local del equipo junto con las acciones
de inicio, carpetas, ingreso, validacion, archivos y salida
si no se puede escribir el log se muestra un aviso

al iniciar se generan 50 registros nuevos
para recuperar los de una sesion anterior debes haberlos exportado y luego
importar el archivo guardado

## etapa 4: mongodb

para usar mongodb instala las dependencias

```sh
python -m pip install -r requirements.txt
```

en este equipo ya se preparo un entorno local con las dependencias
desde la carpeta del proyecto puedes iniciar el programa con

```powershell
.\.venv\Scripts\python.exe main.py
```

la configuracion local se guarda en `.env`, que esta excluido de git
para configurar otra computadora copia `.env.example` a `.env` y completa
la cadena de conexion con un usuario de base de datos de atlas
si la clave tiene caracteres especiales debes codificarlos para una uri
la direccion ip del equipo debe estar autorizada en atlas

usa un usuario de atlas con acceso de lectura y escritura solo a la base del taller
si cambia la ip del equipo puede ser necesario actualizar el acceso de red en atlas

la opcion 6 abre el menu de mongodb

- insertar guarda los registros validados en `taller_informatica` y la coleccion `signos_vitales`
- consultar por id busca un registro con su identificacion exacta
- consultar resultados calcula el promedio de frecuencia y busca saturaciones menores de 94
- los resultados se guardan en `data/json/resultados_mongo.json`

se conservan los cuatro campos originales y se agregan `fc_num` y `spo2_num`
como numeros para hacer los calculos y filtros en mongodb
un indice unico evita ids repetidos y los ids que ya existen se omiten
por eso repetir una insercion no cambia los datos anteriores
si una insercion falla a la mitad, los registros ya guardados permanecen

el promedio queda como `null` si no hay datos
el cliente se cierra al volver al menu principal o cuando hay un error

referencia tecnica: [documentacion oficial de pymongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)

## etapa 5: integracion del sistema

`main.py` une todas las partes del proyecto

| opcion | funcion |
| --- | --- |
| 1 | mostrar los registros ordenados por frecuencia |
| 2 | ingresar y validar un registro nuevo |
| 3 | validar todos los registros en memoria |
| 4 | exportar los tres formatos |
| 5 | importar un archivo y reemplazar los registros en memoria |
| 6 | conectar con mongodb y abrir el menu de consultas |
| 0 | salir |

para recuperar los datos de ejemplo elige 5 e ingresa
`data/json/signos_vitales.json`
despues usa 3 para validar y 6 para abrir mongodb
en el menu de mongodb puedes insertar, buscar por id o exportar las consultas
la opcion 0 del menu de mongodb vuelve al menu principal

la lista en memoria y la coleccion de mongodb son independientes
importar un archivo no cambia automaticamente la base de datos
para enviarlo a mongodb hay que elegir insertar en su menu
los ids existentes se omiten aunque los nuevos valores sean diferentes

### revision realizada

se comprobo el programa completo en un proceso independiente con atlas real
la prueba uso una copia temporal para no cambiar los archivos de ejemplo

- opcion incorrecta y regreso al menu
- rechazo de formato incorrecto e id repetido durante el ingreso
- ingreso de un registro valido y validacion de 51 registros
- exportacion de los datos ordenados en los tres formatos
- rechazo de un json dañado sin perder la lista actual
- importacion de 50 registros desde el archivo de ejemplo
- conexion real y omision de los 50 ids ya existentes
- consulta de un id existente y de otro inexistente
- promedio y saturaciones contrastados con el archivo de ejemplo
- exportacion de resultados y salida al menu principal
- registro de acciones y cierre del programa

