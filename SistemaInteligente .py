# Sistema Inteligente de rutas de Transmilenio
# ---------------------------------------------------------------
# Instrucciones de ejecución:
# ---------------------------------------------------------------
#
# Pasos:
#   1. Abrir una terminal en la carpeta donde está este archivo.
#   2. Ejecutar el comando:  python SistemaInteligente.py
#   3. Escribir el Punto A y el Punto B cuando el programa los pida,
#      con el nombre exacto de la estación (mayúsculas y tildes).
#
# Estaciones disponibles:
#   Portal Norte, Toberín, Calle 146, Pepe Sierra, Calle 100, Héroes,
#   Calle 72, Calle 45, Calle 26, Av. Jiménez, Tercer Milenio,
#   De La Sabana, Ricaurte, Pradera, Banderas, Portal Américas,
#   Centro Memoria, CAD, Av. Rojas, Portal El Dorado, Paloquemao.
# ---------------------------------------------------------------

#Hechos: Conectividad entre estaciones de Transmilenio y tiempo de viaje en minutos
# Estan definidos como tuplas (Estacion1, Estacion2, Tiempo) 
Hechos = [
    ("Portal Norte", "Toberín", 4),
    ("Toberín", "Calle 146", 3),
    ("Calle 146", "Pepe Sierra", 4),
    ("Pepe Sierra", "Calle 100", 3),
    ("Calle 100", "Héroes", 5),
    ("Héroes", "Calle 72", 3),
    ("Calle 72", "Calle 45", 5),
    ("Calle 45", "Calle 26", 4),
    ("Calle 26", "Av. Jiménez", 4),
    ("Av. Jiménez", "Tercer Milenio", 3),
    ("Av. Jiménez", "De La Sabana", 3),
    ("De La Sabana", "Ricaurte", 4),
    ("Ricaurte", "Pradera", 5),
    ("Pradera", "Banderas", 6),
    ("Banderas", "Portal Américas", 5),
    ("Calle 26", "Centro Memoria", 3),
    ("Centro Memoria", "CAD", 4),
    ("CAD", "Av. Rojas", 6),
    ("Av. Rojas", "Portal El Dorado", 5),
    ("Ricaurte", "Paloquemao", 3),
    ("Paloquemao", "CAD", 5),
]


# Regla 1
# Conectado(Estacion1, Estacion2, Tiempo) -> conectado(Estacion2, Estacion1, Tiempo)
# Si desde la Estacion1 se puede ir a la Estacion2, entonces desde Estacion2 también se puede ir a Estacion1, en el mismo tiempo.
def consecutivas(x):
    for a, b, t in Hechos:
        if a == x:
            yield b, t
        elif b == x:
            yield a, t


# Regla 2
# Ruta(Estacion1, Estacion1): cuando la estación de origen y destino son iguales, la ruta es solo esa estación y el tiempo es 0.
# Regla 3 
# Ruta(Estacion1, Estacion2) <- Conectado(Estacion1, Estacion3, Tiempo1) y Ruta(Estacion3, Estacion2), sin repetir estaciones
def rutas(x, y, visitadas):
    if x == y:
        yield [y], 0
        return
    for z, t in consecutivas(x):
        if z not in visitadas:
            for camino, total in rutas(z, y, visitadas + [z]):
                yield [x] + camino, t + total
