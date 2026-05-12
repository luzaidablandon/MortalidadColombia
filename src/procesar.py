import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

print("Cargando archivos...")

muertes  = pd.read_excel(os.path.join(DATA_DIR, "NoFetal2019.xlsx"))
codigos  = pd.read_excel(os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx"), header=8)
divipola = pd.read_excel(os.path.join(DATA_DIR, "Divipola.xlsx"))

print("¡Listo! Procesando...\n")

# -----------------------------------------------
# LIMPIEZA 1 — Renombrar columnas largas de codigos
# -----------------------------------------------
codigos = codigos.rename(columns={
    "Código de la CIE-10 cuatro caracteres"                  : "COD_MUERTE",
    "Descripcion  de códigos mortalidad a cuatro caracteres" : "NOMBRE_CAUSA"
})

# Quedarnos solo con las columnas que usaremos
codigos = codigos[["COD_MUERTE", "NOMBRE_CAUSA"]].dropna()
print(f"Códigos de muerte disponibles: {len(codigos)}")

# -----------------------------------------------
# LIMPIEZA 2 — Unir muertes con nombres de lugar
# -----------------------------------------------
# Divipola tiene COD_DEPARTAMENTO y DEPARTAMENTO
# Lo unimos con muertes para tener el nombre del departamento
deptos = divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()
muertes = muertes.merge(deptos, on="COD_DEPARTAMENTO", how="left")

# También unimos municipios
municipios = divipola[["COD_DANE", "MUNICIPIO"]].drop_duplicates()
muertes = muertes.merge(municipios, on="COD_DANE", how="left")

print(f"Columnas después de unir: {list(muertes.columns)}")

# -----------------------------------------------
# LIMPIEZA 3 — Verificar valores nulos críticos
# -----------------------------------------------
print("\nValores nulos en columnas clave:")
cols_clave = ["COD_DEPARTAMENTO", "DEPARTAMENTO", "MES", "SEXO", 
              "GRUPO_EDAD1", "COD_MUERTE", "MUNICIPIO"]
for col in cols_clave:
    nulos = muertes[col].isna().sum()
    print(f"  {col}: {nulos} nulos")

# -----------------------------------------------
# VERIFICACIÓN FINAL
# -----------------------------------------------
print(f"\nTotal muertes: {len(muertes)}")
print(f"Departamentos únicos: {muertes['DEPARTAMENTO'].nunique()}")
print(f"Municipios únicos: {muertes['MUNICIPIO'].nunique()}")
print(f"Meses: {sorted(muertes['MES'].dropna().unique())}")
print(f"Valores de SEXO: {muertes['SEXO'].unique()}")
print(f"Rango GRUPO_EDAD1: {muertes['GRUPO_EDAD1'].min()} a {muertes['GRUPO_EDAD1'].max()}")