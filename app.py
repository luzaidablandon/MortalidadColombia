import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
import os
import json

# ============================================================
# 1. CARGA Y PROCESAMIENTO DE DATOS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

print("Cargando datos... esto puede tomar unos segundos")

muertes  = pd.read_excel(os.path.join(DATA_DIR, "NoFetal2019.xlsx"))
codigos  = pd.read_excel(os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx"), header=8)
divipola = pd.read_excel(os.path.join(DATA_DIR, "Divipola.xlsx"))

# Renombrar columnas largas
codigos = codigos.rename(columns={
    "Código de la CIE-10 cuatro caracteres"                 : "COD_MUERTE",
    "Descripcion  de códigos mortalidad a cuatro caracteres": "NOMBRE_CAUSA"
})[["COD_MUERTE", "NOMBRE_CAUSA"]].dropna()

# Unir nombres de departamento y municipio
deptos     = divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()
municipios = divipola[["COD_DANE", "MUNICIPIO"]].drop_duplicates()
muertes    = muertes.merge(deptos,     on="COD_DEPARTAMENTO", how="left")
muertes    = muertes.merge(municipios, on="COD_DANE",         how="left")

print("¡Datos cargados!")
# ============================================================
# CARGAR GEOJSON DE COLOMBIA
# ============================================================

with open(
    os.path.join(BASE_DIR, "assets", "geojson", "colombia.geojson"),
    encoding="utf-8"
) as f:
    geojson_colombia = json.load(f)

print("GeoJSON cargado correctamente")
print(geojson_colombia.keys())
print(geojson_colombia["features"][0]["properties"])

# ============================================================
# 2. CÁLCULOS PARA CADA GRÁFICO
# ============================================================

# --- GRÁFICO 1: Muertes por departamento (mapa) ---
muertes_depto = (muertes.groupby(["COD_DEPARTAMENTO", "DEPARTAMENTO"])
                         .size()
                         .reset_index(name="TOTAL"))

# --- GRÁFICO 2: Muertes por mes (líneas) ---
nombres_mes = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun",
               7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
muertes_mes = (muertes.groupby("MES")
                       .size()
                       .reset_index(name="TOTAL"))
muertes_mes["MES_NOMBRE"] = muertes_mes["MES"].map(nombres_mes)

# --- GRÁFICO 3: 5 ciudades más violentas (homicidios X95) ---
homicidios = muertes[muertes["COD_MUERTE"].str.startswith("X95", na=False)]
ciudades_violentas = (homicidios.groupby(["COD_DANE", "MUNICIPIO"])
                                .size()
                                .reset_index(name="HOMICIDIOS")
                                .sort_values("HOMICIDIOS", ascending=False)
                                .head(5))

# --- GRÁFICO 4: 10 ciudades con menor mortalidad ---
menor_mortalidad = (muertes.groupby(["COD_DANE", "MUNICIPIO"])
                            .size()
                            .reset_index(name="TOTAL")
                            .sort_values("TOTAL")
                            .head(10))

# --- GRÁFICO 5: Top 10 causas de muerte (tabla) ---
top_causas = (muertes.groupby("COD_MUERTE")
                     .size()
                     .reset_index(name="TOTAL")
                     .merge(codigos, on="COD_MUERTE", how="left")
                     .sort_values("TOTAL", ascending=False)
                     .head(10)[["COD_MUERTE", "NOMBRE_CAUSA", "TOTAL"]])

# --- GRÁFICO 6: Muertes por sexo y departamento (barras apiladas) ---
sexo_map = {1: "Hombre", 2: "Mujer", 3: "Indeterminado"}
muertes["SEXO_NOMBRE"] = muertes["SEXO"].map(sexo_map)
muertes_sexo = (muertes.groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
                        .size()
                        .reset_index(name="TOTAL"))

# --- GRÁFICO 7: Histograma por grupo de edad ---
edad_map = {
    0: "Neonatal (<1m)", 1: "Neonatal (<1m)", 2: "Neonatal (<1m)",
    3: "Neonatal (<1m)", 4: "Neonatal (<1m)",
    5: "Infantil (1-11m)", 6: "Infantil (1-11m)",
    7: "Primera infancia (1-4a)", 8: "Primera infancia (1-4a)",
    9: "Niñez (5-14a)", 10: "Niñez (5-14a)",
    11: "Adolescencia (15-19a)",
    12: "Juventud (20-29a)", 13: "Juventud (20-29a)",
    14: "Adultez temprana (30-44a)", 15: "Adultez temprana (30-44a)",
    16: "Adultez temprana (30-44a)",
    17: "Adultez intermedia (45-59a)", 18: "Adultez intermedia (45-59a)",
    19: "Adultez intermedia (45-59a)",
    20: "Vejez (60-84a)", 21: "Vejez (60-84a)", 22: "Vejez (60-84a)",
    23: "Vejez (60-84a)", 24: "Vejez (60-84a)",
    25: "Longevidad (85+)", 26: "Longevidad (85+)",
    27: "Longevidad (85+)", 28: "Longevidad (85+)",
    29: "Edad desconocida"
}
muertes["CATEGORIA_EDAD"] = muertes["GRUPO_EDAD1"].map(edad_map)
orden_edad = ["Neonatal (<1m)", "Infantil (1-11m)", "Primera infancia (1-4a)",
              "Niñez (5-14a)", "Adolescencia (15-19a)", "Juventud (20-29a)",
              "Adultez temprana (30-44a)", "Adultez intermedia (45-59a)",
              "Vejez (60-84a)", "Longevidad (85+)", "Edad desconocida"]
muertes_edad = (muertes.groupby("CATEGORIA_EDAD")
                        .size()
                        .reset_index(name="TOTAL"))
muertes_edad["CATEGORIA_EDAD"] = pd.Categorical(
    muertes_edad["CATEGORIA_EDAD"], categories=orden_edad, ordered=True)
muertes_edad = muertes_edad.sort_values("CATEGORIA_EDAD")

# ============================================================
# 3. CREACIÓN DE GRÁFICOS
# ============================================================

# --- GRÁFICO 1: Mapa de calor por departamento ---
fig_mapa = px.choropleth(
    muertes_depto,
    geojson=geojson_colombia,
    locations="DEPARTAMENTO",
    featureidkey="properties.DPTO_CNMBR",
    color="TOTAL",
    hover_name="DEPARTAMENTO",
    hover_data={"TOTAL": True},
    color_continuous_scale="Reds",
    title="Distribución total de muertes por departamento — Colombia 2019"
)

fig_mapa.update_geos(
    fitbounds="locations",
    visible=False
)

fig_mapa.update_layout(
    margin={"r":0,"t":50,"l":0,"b":0}
)

# --- GRÁFICO 2: Líneas por mes ---
fig_lineas = px.line(
    muertes_mes,
    x="MES_NOMBRE", y="TOTAL",
    markers=True,
    title="Total de muertes por mes — Colombia 2019",
    labels={"MES_NOMBRE": "Mes", "TOTAL": "Total muertes"},
    color_discrete_sequence=["#E63946"]
)
fig_lineas.update_layout(xaxis=dict(categoryorder="array",
                                     categoryarray=list(nombres_mes.values())))

# --- GRÁFICO 3: Barras ciudades violentas ---
fig_violentas = px.bar(
    ciudades_violentas,
    x="MUNICIPIO", y="HOMICIDIOS",
    title="5 ciudades más violentas — Homicidios con arma de fuego (X95) 2019",
    labels={"MUNICIPIO": "Ciudad", "HOMICIDIOS": "Homicidios"},
    color="HOMICIDIOS",
    color_continuous_scale="OrRd",
    text="HOMICIDIOS"
)
fig_violentas.update_traces(textposition="outside")

# --- GRÁFICO 4: Circular menor mortalidad ---
fig_circular = px.pie(
    menor_mortalidad,
    names="MUNICIPIO", values="TOTAL",
    title="10 municipios con menor índice de mortalidad — Colombia 2019",
    hole=0.3
)
fig_circular.update_traces(textposition="inside", textinfo="percent+label")

# --- GRÁFICO 5: Tabla top causas ---
fig_tabla = go.Figure(data=[go.Table(
    header=dict(
        values=["<b>Código</b>", "<b>Causa de muerte</b>", "<b>Total casos</b>"],
        fill_color="#E63946",
        font=dict(color="white", size=13),
        align="left"
    ),
    cells=dict(
        values=[top_causas["COD_MUERTE"],
                top_causas["NOMBRE_CAUSA"],
                top_causas["TOTAL"]],
        fill_color=[["#f8f8f8", "white"] * 5],
        align="left",
        font=dict(size=12)
    )
)])
fig_tabla.update_layout(title="Top 10 causas de muerte — Colombia 2019")

# --- GRÁFICO 6: Barras apiladas por sexo ---
fig_sexo = px.bar(
    muertes_sexo,
    x="DEPARTAMENTO", y="TOTAL",
    color="SEXO_NOMBRE",
    barmode="stack",
    title="Muertes por sexo en cada departamento — Colombia 2019",
    labels={"DEPARTAMENTO": "Departamento",
            "TOTAL": "Total muertes", "SEXO_NOMBRE": "Sexo"},
    color_discrete_map={"Hombre": "#1D3557",
                        "Mujer": "#E63946",
                        "Indeterminado": "#A8DADC"}
)
fig_sexo.update_layout(xaxis_tickangle=-45)

# --- GRÁFICO 7: Histograma grupos de edad ---
fig_edad = px.bar(
    muertes_edad,
    x="CATEGORIA_EDAD", y="TOTAL",
    title="Distribución de muertes por grupo de edad — Colombia 2019",
    labels={"CATEGORIA_EDAD": "Grupo de edad", "TOTAL": "Total muertes"},
    color="TOTAL",
    color_continuous_scale="Blues",
    text="TOTAL"
)
fig_edad.update_traces(textposition="outside")
fig_edad.update_layout(xaxis_tickangle=-30)

# ============================================================
# 4. APP DASH — LAYOUT (estructura de la página web)
# ============================================================
app = Dash(
    __name__,
    title="Mortalidad Colombia 2019 - Luz Blandón",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]  
    
server = app.server  # necesario para Render

app.layout = html.Div([

    # Encabezado
    html.Div([
        html.H1("Mortalidad en Colombia 2019",
                style={"color": "white", "textAlign": "center",
                       "margin": "0", "padding": "20px"}),
         html.H2("Luz Aida Blandón",
                style={"color": "white", "textAlign": "center",
                       "margin": "0", "padding": "20px"}),
        html.P("Análisis interactivo de datos DANE — 244.355 registros",
               style={"color": "#A8DADC", "textAlign": "center", "margin": "0"})
    ], style={"backgroundColor": "#1D3557", "paddingBottom": "15px"}),

    # Contenido
    html.Div([

        # Gráfico 1 — Mapa
        html.Div([
            html.H3("📍 Distribución geográfica de muertes"),
            dcc.Graph(figure=fig_mapa)
        ], style={"marginBottom": "30px"}),

        # Gráfico 2 — Líneas
        html.Div([
            html.H3("📈 Muertes por mes"),
            dcc.Graph(figure=fig_lineas)
        ], style={"marginBottom": "30px"}),

        # Gráfico 3 — Barras ciudades violentas
        html.Div([
            html.H3("🔴 Ciudades más violentas"),
            dcc.Graph(figure=fig_violentas)
        ], style={"marginBottom": "30px"}),

        # Gráfico 4 — Circular
        html.Div([
            html.H3("🟢 Municipios con menor mortalidad"),
            dcc.Graph(figure=fig_circular)
        ], style={"marginBottom": "30px"}),

        # Gráfico 5 — Tabla
        html.Div([
            html.H3("📋 Top 10 causas de muerte"),
            dcc.Graph(figure=fig_tabla)
        ], style={"marginBottom": "30px"}),

        # Gráfico 6 — Barras apiladas sexo
        html.Div([
            html.H3("👥 Muertes por sexo y departamento"),
            dcc.Graph(figure=fig_sexo)
        ], style={"marginBottom": "30px"}),

        # Gráfico 7 — Histograma edades
        html.Div([
            html.H3("📊 Distribución por grupo de edad"),
            dcc.Graph(figure=fig_edad)
        ], style={"marginBottom": "30px"}),

    ], style={"maxWidth": "1200px", "margin": "auto", "padding": "20px"})

])

# ============================================================
# 5. EJECUTAR LA APP
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
