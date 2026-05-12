import pandas as pd
import os

# Esto detecta automáticamente dónde está el archivo explorar.py
# y construye la ruta correcta a la carpeta data/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

print("Buscando datos en:", DATA_DIR)
print("Cargando archivos... espera un momento\n")

muertes  = pd.read_excel(os.path.join(DATA_DIR, "NoFetal2019.xlsx"))
codigos = pd.read_excel(os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx"), header=8)
divipola = pd.read_excel(os.path.join(DATA_DIR, "Divipola.xlsx"))

print("¡Archivos cargados!\n")

# EXPLORAMOS NoFetal2019
print("=" * 50)
print("ARCHIVO: NoFetal2019")
print("=" * 50)
print(f"Filas (muertes registradas): {len(muertes)}")
print(f"Columnas: {len(muertes.columns)}")
print("\nNombre de columnas:")
for col in muertes.columns:
    print(f"  → {col}")
print("\nPrimeras 3 filas:")
print(muertes.head(3))

# EXPLORAMOS CodigosDeMuerte
print("\n" + "=" * 50)
print("ARCHIVO: CodigosDeMuerte")
print("=" * 50)
print(f"Filas: {len(codigos)}")
print("\nNombre de columnas:")
for col in codigos.columns:
    print(f"  → {col}")
print("\nPrimeras 3 filas:")
print(codigos.head(3))

# EXPLORAMOS Divipola
print("\n" + "=" * 50)
print("ARCHIVO: Divipola")
print("=" * 50)
print(f"Filas: {len(divipola)}")
print("\nNombre de columnas:")
for col in divipola.columns:
    print(f"  → {col}")
print("\nPrimeras 3 filas:")
print(divipola.head(3))
# Investigamos CodigosDeMuerte más a fondo
print("\nColumnas reales de CodigosDeMuerte:")
for col in codigos.columns:
    print(f"  → {col}")
print("\nPrimeras 3 filas:")
print(codigos.head(3))