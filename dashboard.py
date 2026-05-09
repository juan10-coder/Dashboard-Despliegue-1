# ============================================================
#  Streamlit BI Studio
#  Maestría en Analítica Aplicada
#  Herramientas de Visualización para la Inteligencia de Negocios
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import matplotlib.pyplot as plt
import sqlite3

# ── Configuración ────────────────────────────────────────────
st.set_page_config(
    page_title="Streamlit BI Studio | Maestría en Analítica Aplicada",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Paleta monocromática profesional ─────────────────────────
# Azul oscuro slate como base, un solo acento azul medio.
CHART_PRIMARY   = "#4a7fc1"
CHART_SECONDARY = "#7faad6"
CHART_TERTIARY  = "#b0cceb"
CHART_NEG       = "#8a9ab5"
CHART_SEQ       = [CHART_PRIMARY, CHART_SECONDARY, CHART_TERTIARY, CHART_NEG,
                   "#3362a0", "#6992c4", "#c8daf2"]

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#d6dce8", size=12),
    title_font=dict(size=14, color="#d6dce8"),
    margin=dict(l=16, r=16, t=48, b=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    xaxis=dict(gridcolor="rgba(255,255,255,.06)", linecolor="rgba(255,255,255,.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,.06)", linecolor="rgba(255,255,255,.08)"),
)

st.markdown("""
<style>
/* ── Base ───────────────────────────────────────────────── */
:root {
    --bg:        #0b0f1a;
    --surface:   #10162a;
    --card:      #141b30;
    --border:    rgba(255,255,255,.07);
    --accent:    #4a7fc1;
    --accent-hl: rgba(74,127,193,.14);
    --text:      #d6dce8;
    --muted:     #7a8499;
    --faint:     #3a4258;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0e1428 0%, var(--bg) 60%);
}
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1,h2,h3,h4,h5,h6,p,li,span,div,label { color: var(--text); }

.block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; }

/* ── Hero ───────────────────────────────────────────────── */
.hero {
    background: var(--accent-hl);
    border: 1px solid rgba(74,127,193,.25);
    border-radius: 14px;
    padding: 1.5rem 1.8rem 1.2rem;
    margin-bottom: 1.4rem;
}
.hero h1, .hero h2, .hero h3 { margin: 0 0 .3rem; }

/* ── Section card ───────────────────────────────────────── */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
}

/* ── Callouts ───────────────────────────────────────────── */
.callout-info {
    background: rgba(74,127,193,.10);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: .65rem 1rem;
    margin: .6rem 0;
    font-size: .92rem;
    line-height: 1.6;
    color: var(--text);
}
.callout-warn {
    background: rgba(180,160,100,.10);
    border-left: 3px solid #b4a064;
    border-radius: 6px;
    padding: .65rem 1rem;
    margin: .6rem 0;
    font-size: .92rem;
    color: var(--text);
}

/* ── Sidebar nav ────────────────────────────────────────── */
[data-testid="stSidebar"] .stRadio label {
    font-size: .9rem;
    padding: .2rem 0;
}

hr { border: none; border-top: 1px solid var(--border); margin: 1.1rem 0; }

/* ── Metric delta ───────────────────────────────────────── */
[data-testid="stMetricDelta"] { font-size: .82rem; }
</style>
""", unsafe_allow_html=True)


# ── Estado de sesión ─────────────────────────────────────────
if "visitas" not in st.session_state:
    st.session_state.visitas = 0
if "escenario" not in st.session_state:
    st.session_state.escenario = "Base"
st.session_state.visitas += 1


# ── Datos simulados ──────────────────────────────────────────
@st.cache_data
def cargar_ventas():
    df_raw = pd.read_csv("ventas.csv", encoding="latin-1")
    
    df = pd.DataFrame()
    df["fecha"] = pd.to_datetime(df_raw["ORDERDATE"])
    df["region"] = df_raw["COUNTRY"].fillna("Desconocido")
    df["canal"] = df_raw["DEALSIZE"].fillna("Desconocido")
    df["producto"] = df_raw["PRODUCTLINE"].fillna("Desconocido")
    df["unidades"] = df_raw["QUANTITYORDERED"]
    df["precio_unitario"] = df_raw["PRICEEACH"]
    df["ventas"] = df_raw["SALES"]
    
    df["costo_unitario"] = df["precio_unitario"] * 0.70
    df["costo_total"] = df["unidades"] * df["costo_unitario"]
    df["margen_bruto"] = df["ventas"] - df["costo_total"]
    df["mes"] = df["fecha"].dt.strftime("%Y-%m")
    return df


@st.cache_data
def generar_salud(seed: int = 7):
    np.random.seed(seed)
    fechas   = pd.date_range("2025-01-01", periods=12, freq="MS")
    servicios= ["Urgencias", "Consulta externa", "Hospitalización", "Imágenes"]
    data = []
    for f in fechas:
        for s in servicios:
            data.append([f, s,
                np.random.randint(180, 620),
                np.random.randint(12, 95),
                np.random.randint(4, 45),
                np.random.randint(110000, 520000)])
    df = pd.DataFrame(data, columns=[
        "fecha","servicio","pacientes_atendidos","tiempo_espera_min","reingresos","costo_promedio"])
    df["tasa_reingreso"] = df["reingresos"] / df["pacientes_atendidos"]
    return df


@st.cache_data
def generar_finanzas(seed: int = 13):
    np.random.seed(seed)
    periodos = pd.date_range("2025-01-01", periods=12, freq="MS").strftime("%Y-%m")
    unidades = ["Consumo", "Corporativo", "Digital", "Retail"]
    data = []
    for p in periodos:
        for u in unidades:
            ingresos = np.random.randint(120, 420) * 1_000_000
            costos   = ingresos * np.random.uniform(0.42, 0.68)
            gastos   = ingresos * np.random.uniform(0.10, 0.19)
            data.append([p, u, ingresos, costos, gastos])
    df = pd.DataFrame(data, columns=["periodo","unidad_negocio","ingresos","costos","gastos"])
    df["utilidad_operativa"] = df["ingresos"] - df["costos"] - df["gastos"]
    df["margen_operativo"]   = np.where(df["ingresos"] > 0,
                                        df["utilidad_operativa"] / df["ingresos"], 0)
    return df


@st.cache_data
def generar_produccion(seed: int = 5):
    np.random.seed(seed)
    fechas = pd.date_range("2025-01-01", periods=120, freq="D")
    lineas = ["Línea A", "Línea B", "Línea C"]
    turnos = ["Mañana", "Tarde", "Noche"]
    data = []
    for f in fechas:
        for l in lineas:
            for t in turnos:
                producidas  = np.random.randint(180, 650)
                defectuosas = np.random.randint(2, 35)
                tiempo      = np.random.randint(280, 520)
                data.append([f, l, t, producidas, defectuosas, tiempo])
    df = pd.DataFrame(data, columns=[
        "fecha","linea","turno","unidades_producidas","unidades_defectuosas","tiempo_operacion_min"])
    df["tasa_defectos"]     = df["unidades_defectuosas"] / df["unidades_producidas"]
    df["productividad_min"] = df["unidades_producidas"] / df["tiempo_operacion_min"]
    df["mes"]               = df["fecha"].dt.strftime("%Y-%m")
    return df


@st.cache_resource
def obtener_conexion():
    return sqlite3.connect("datos_negocio.db", check_same_thread=False)


# ── Utilidades ───────────────────────────────────────────────
def fmt_cop(x):  return f"$ {x:,.0f}"
def fmt_m(x):    return f"$ {x/1_000_000:,.1f} M"
def fmt_pct(x):  return f"{x:.1%}"

def validar_columnas(df, requeridas):
    return [c for c in requeridas if c not in df.columns]

def insight_ventas(df):
    if df.empty:
        return "No hay datos suficientes para generar una lectura analítica."
    top_region = df.groupby("region")["ventas"].sum().idxmax()
    top_canal  = df.groupby("canal")["ventas"].sum().idxmax()
    margen = df["margen_bruto"].sum() / df["ventas"].sum() if df["ventas"].sum() > 0 else 0
    return (
        f"La región con mayor contribución al período es **{top_region}** y el canal con mayor "
        f"participación es **{top_canal}**. El margen bruto estimado sobre el conjunto filtrado "
        f"es **{margen:.1%}**, lo que refleja diferencias de desempeño atribuibles a la mezcla "
        f"de canal y a la estructura de costos por producto."
    )

def plt_clean(ax, fig):
    """Aplica estilo uniforme a figuras Matplotlib."""
    fig.patch.set_facecolor("#10162a")
    ax.set_facecolor("#141b30")
    ax.tick_params(colors="#7a8499")
    ax.xaxis.label.set_color("#7a8499")
    ax.yaxis.label.set_color("#7a8499")
    ax.title.set_color("#d6dce8")
    for spine in ax.spines.values():
        spine.set_edgecolor("#3a4258")


# ── Carga ────────────────────────────────────────────────────
ventas     = cargar_ventas()
salud      = generar_salud()
finanzas   = generar_finanzas()
produccion = generar_produccion()
conn       = obtener_conexion()


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## BI Studio")
    st.caption("Maestría en Analítica Aplicada")
    st.markdown("---")

    modulo = st.radio(
        "Módulo",
        [
            "Inicio",
            "1. Ciclo, estado y caché",
            "2. Layout",
            "3. Librerías de visualización",
            "4. Flujo analítico",
            "5. Caso BI comercial",
            "6. Producción industrial",
            "7. Finanzas",
            "8. Salud",
            "9. SQLite y recursos",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption(f"Sesión activa · {st.session_state.visitas} interacciones")

    escenario = st.selectbox(
        "Escenario",
        ["Base", "Optimista", "Pesimista"],
        index=["Base","Optimista","Pesimista"].index(st.session_state.escenario),
        help="Aplica un ajuste multiplicativo a las métricas del caso comercial."
    )
    st.session_state.escenario = escenario

factor = {"Base": 1.0, "Optimista": 1.08, "Pesimista": 0.93}[escenario]


# ════════════════════════════════════════════════════════════
# MÓDULO: INICIO
# ════════════════════════════════════════════════════════════
if modulo == "Inicio":
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.title("Streamlit BI Studio")
    st.markdown(
        "Aplicación demostrativa que integra ciclo de ejecución, estado de sesión, caché, "
        "layout ejecutivo, visualización multimotor y conexión a datos relacionales."
    )
    st.caption("Maestría en Analítica Aplicada · Herramientas de Visualización para la Inteligencia de Negocios")
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros comerciales", f"{len(ventas):,}")
    c2.metric("Registros producción",  f"{len(produccion):,}")
    c3.metric("Registros salud",       f"{len(salud):,}")
    c4.metric("Escenario activo",      st.session_state.escenario)

    st.markdown("---")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### Contenido de la aplicación")
        st.markdown("""
- Funcionamiento de `st.session_state`, `st.cache_data` y `st.cache_resource`
- Organización visual con sidebar, columnas y pestañas
- Integración de Plotly, Altair y Matplotlib en un mismo entorno
- Casos aplicados: comercio, producción industrial, finanzas y salud
- Consulta en tiempo real a una base de datos SQLite
        """)
    with col2:
        resumen = ventas.groupby("mes", as_index=False)["ventas"].sum()
        fig = px.area(resumen, x="mes", y="ventas",
                      title="Ventas mensuales consolidadas",
                      color_discrete_sequence=[CHART_PRIMARY])
        fig.update_traces(fillcolor="rgba(74,127,193,.18)", line_width=2)
        fig.update_layout(**PLOT_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# MÓDULO 1: CICLO, ESTADO Y CACHÉ
# ════════════════════════════════════════════════════════════
elif modulo == "1. Ciclo, estado y caché":
    st.title("Ciclo de ejecución, estado y caché")
    tab1, tab2, tab3 = st.tabs(["Ciclo de ejecución", "Estado de sesión", "Caché"])

    with tab1:
        st.markdown("### Ciclo de ejecución")
        st.markdown(
            "En Streamlit, el script completo se vuelve a ejecutar cada vez que el usuario "
            "interactúa con un widget. Esto tiene implicaciones directas sobre el rendimiento "
            "y la organización del código."
        )
        nombre = st.text_input("Nombre de prueba")
        st.markdown(
            '<div class="callout-info">Cada vez que escribe una letra, Streamlit vuelve a '
            "ejecutar el archivo. La caché y el estado de sesión son los mecanismos para "
            'controlar este comportamiento.</div>', unsafe_allow_html=True)
        if nombre:
            st.success(f"Bienvenido/a, {nombre}. El script acaba de ejecutarse nuevamente.")

    with tab2:
        st.markdown("### Estado de sesión")
        st.markdown(
            "`st.session_state` permite conservar valores entre ejecuciones sucesivas del script."
        )
        if st.button("Incrementar contador"):
            st.session_state.visitas += 1
        st.metric("Interacciones en la sesión actual", st.session_state.visitas)
        st.code(
            "if 'contador' not in st.session_state:\n"
            "    st.session_state.contador = 0\n\n"
            "if st.button('Incrementar'):\n"
            "    st.session_state.contador += 1",
            language="python"
        )

    with tab3:
        st.markdown("### Caché: `st.cache_data` y `st.cache_resource`")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**`st.cache_data`** — para resultados de funciones")
            st.code(
                "@st.cache_data\ndef cargar_datos():\n"
                "    df = pd.read_csv('data/ventas.csv')\n"
                "    return df",
                language="python"
            )
            st.caption("Ideal para DataFrames, listas, resultados de consultas.")
        with col_b:
            st.markdown("**`st.cache_resource`** — para recursos persistentes")
            st.code(
                "@st.cache_resource\ndef obtener_conexion():\n"
                "    return sqlite3.connect('data/bd.db',\n"
                "        check_same_thread=False)",
                language="python"
            )
            st.caption("Ideal para conexiones a BD, modelos de ML, clientes de API.")


# ════════════════════════════════════════════════════════════
# MÓDULO 2: LAYOUT
# ════════════════════════════════════════════════════════════
elif modulo == "2. Layout":
    st.title("Organización visual de una aplicación analítica")
    st.markdown(
        "Una aplicación de BI debe jerarquizar la información: contexto → filtros → "
        "indicadores → visualizaciones → tablas de detalle."
    )

    base_ventas = ventas["ventas"].sum() * factor
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas totales",   fmt_cop(base_ventas), "+8.5%")
    c2.metric("Clientes activos", "1.245",             "+4.1%")
    c3.metric("Margen promedio",  "18.4%",             "+1.3 pp")
    c4.metric("Ticket promedio",  "$ 238.700",         "+2.1%")

    t1, t2, t3 = st.tabs(["Resumen ejecutivo", "Detalle regional", "Detalle por canal"])
    with t1:
        st.markdown(
            "El resumen ejecutivo sitúa al usuario en el estado general del negocio antes "
            "de explorar dimensiones específicas. Los indicadores superiores responden "
            "siempre a la misma pregunta: ¿cómo estamos respecto al período de referencia?"
        )
    with t2:
        reg = ventas.groupby("region", as_index=False)["ventas"].sum()
        fig = px.bar(reg, x="region", y="ventas",
                     title="Ventas por región",
                     color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with t3:
        can = ventas.groupby("canal", as_index=False)["ventas"].sum()
        fig = px.pie(can, names="canal", values="ventas",
                     hole=.48, title="Participación por canal",
                     color_discrete_sequence=CHART_SEQ)
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# MÓDULO 3: LIBRERÍAS
# ════════════════════════════════════════════════════════════
elif modulo == "3. Librerías de visualización":
    st.title("Integración de librerías de visualización")
    tab1, tab2, tab3 = st.tabs(["Plotly", "Altair", "Matplotlib"])

    with tab1:
        st.markdown("### Plotly — visualización interactiva")
        st.markdown(
            "Plotly es la opción principal para tableros exploratorios. "
            "Ofrece tooltips, zoom y selección directa en el navegador."
        )
        serie = ventas.groupby("mes", as_index=False)["ventas"].sum()
        fig = px.line(serie, x="mes", y="ventas", markers=True,
                      title="Evolución mensual de ventas",
                      color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Altair — visualización declarativa")
        st.markdown(
            "Altair permite especificar qué representar mediante canales visuales "
            "(posición, color, tamaño), siguiendo la gramática de gráficos."
        )
        datos_salud = salud.groupby("servicio", as_index=False)["costo_promedio"].mean()
        chart = (
            alt.Chart(datos_salud)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color=CHART_PRIMARY)
            .encode(
                x=alt.X("servicio:N", title="Servicio"),
                y=alt.Y("costo_promedio:Q", title="Costo promedio"),
                tooltip=["servicio", alt.Tooltip("costo_promedio:Q", format=",.0f")]
            )
            .properties(height=360)
            .configure_axis(gridColor="#3a4258", labelColor="#7a8499", titleColor="#7a8499")
            .configure_view(stroke="transparent")
        )
        st.altair_chart(chart, use_container_width=True)

    with tab3:
        st.markdown("### Matplotlib — control técnico y estático")
        st.markdown(
            "Matplotlib es adecuado cuando se requiere control preciso sobre cada "
            "elemento del gráfico, o para generar figuras para informes académicos."
        )
        bio = pd.DataFrame({
            "tratamiento": ["Control", "Fertilizante A", "Fertilizante B"],
            "crecimiento_cm": [12.4, 18.7, 16.9],
            "desviacion":     [1.8, 2.1, 1.5]
        })
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(bio["tratamiento"], bio["crecimiento_cm"],
               yerr=bio["desviacion"], capsize=5,
               color=CHART_PRIMARY, edgecolor="none")
        ax.set_title("Crecimiento promedio por tratamiento")
        ax.set_xlabel("Tratamiento")
        ax.set_ylabel("Crecimiento promedio (cm)")
        plt_clean(ax, fig)
        st.pyplot(fig)


# ════════════════════════════════════════════════════════════
# MÓDULO 4: FLUJO ANALÍTICO
# ════════════════════════════════════════════════════════════
elif modulo == "4. Flujo analítico":
    st.title("Flujo de una aplicación analítica")
    st.markdown(
        "**Datos → Validación → Transformación → Filtros → Indicadores → "
        "Visualización → Decisión**"
    )
    st.markdown(
        "Este módulo ilustra la etapa de carga y validación. "
        "Cargue un archivo CSV para activar el perfilamiento básico del conjunto de datos."
    )

    archivo = st.file_uploader("Archivo CSV", type=["csv"])
    if archivo is not None:
        datos = pd.read_csv(archivo)
        st.success("Archivo cargado correctamente.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Filas",          f"{datos.shape[0]:,}")
        c2.metric("Columnas",       f"{datos.shape[1]:,}")
        c3.metric("Valores nulos",  f"{int(datos.isna().sum().sum()):,}")
        st.dataframe(datos.head(), use_container_width=True)

        st.markdown("#### Valores faltantes por columna")
        nulos = (datos.isna().sum()
                 .reset_index()
                 .rename(columns={"index": "columna", 0: "faltantes"}))
        st.dataframe(nulos, use_container_width=True)

        st.markdown("#### Tipos de datos")
        tipos = (datos.dtypes.reset_index()
                 .rename(columns={"index": "columna", 0: "tipo"}))
        tipos["tipo"] = tipos["tipo"].astype(str)
        st.dataframe(tipos, use_container_width=True)
    else:
        st.markdown(
            '<div class="callout-info">Cargue un archivo CSV para activar la '
            'validación, el perfilamiento y la vista previa de datos.</div>',
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════════════
# MÓDULO 5: CASO BI COMERCIAL
# ════════════════════════════════════════════════════════════
elif modulo == "5. Caso BI comercial":
    st.title("Caso completo de BI comercial")

    requeridas = ["fecha","region","canal","producto","unidades",
                  "precio_unitario","costo_unitario","ventas","margen_bruto"]
    faltantes = validar_columnas(ventas, requeridas)
    if faltantes:
        st.error(f"Columnas faltantes en el conjunto de datos: {faltantes}")
        st.stop()

    with st.sidebar:
        st.markdown("---")
        st.markdown("**Filtros — caso comercial**")
        region  = st.selectbox("Región",   ["Todas"]  + sorted(ventas["region"].unique()))
        canal   = st.selectbox("Canal",    ["Todos"]  + sorted(ventas["canal"].unique()))
        producto= st.selectbox("Producto", ["Todos"]  + sorted(ventas["producto"].unique()))

    df = ventas.copy()
    if region   != "Todas": df = df[df["region"]   == region]
    if canal    != "Todos": df = df[df["canal"]     == canal]
    if producto != "Todos": df = df[df["producto"]  == producto]

    df["ventas"]       = df["ventas"]       * factor
    df["margen_bruto"] = df["margen_bruto"] * factor

    v_total = df["ventas"].sum()
    u_total = df["unidades"].sum()
    m_total = df["margen_bruto"].sum()
    m_pct   = m_total / v_total if v_total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas totales",   fmt_cop(v_total))
    c2.metric("Unidades vendidas",f"{u_total:,.0f}")
    c3.metric("Margen bruto",     fmt_cop(m_total))
    c4.metric("Margen porcentual",fmt_pct(m_pct))

    tab1, tab2, tab3, tab4 = st.tabs(["Evolución", "Comparación", "Datos", "Lectura analítica"])

    with tab1:
        mensual = df.groupby("mes", as_index=False)["ventas"].sum()
        fig = px.line(mensual, x="mes", y="ventas", markers=True,
                      title="Ventas mensuales",
                      color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        a, b = st.columns(2)
        with a:
            vr = df.groupby("region", as_index=False)["ventas"].sum()
            fig = px.bar(vr, x="region", y="ventas", text_auto=".2s",
                         title="Ventas por región",
                         color_discrete_sequence=[CHART_PRIMARY])
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        with b:
            vc = df.groupby("canal", as_index=False)["ventas"].sum()
            fig = px.pie(vc, names="canal", values="ventas", hole=.5,
                         title="Participación por canal",
                         color_discrete_sequence=CHART_SEQ[:3])
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.dataframe(df, use_container_width=True, height=420)

    with tab4:
        st.markdown(
            f'<div class="callout-info">{insight_ventas(df)}</div>',
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════════════
# MÓDULO 6: PRODUCCIÓN INDUSTRIAL
# ════════════════════════════════════════════════════════════
elif modulo == "6. Producción industrial":
    st.title("Análisis de producción industrial")
    st.caption("Actividad 1")

    col_f1, col_f2 = st.columns(2)
    linea = col_f1.selectbox("Línea de producción",
                             ["Todas"] + sorted(produccion["linea"].unique()))
    turno = col_f2.selectbox("Turno",
                             ["Todos"] + sorted(produccion["turno"].unique()))

    df = produccion.copy()
    if linea != "Todas": df = df[df["linea"] == linea]
    if turno != "Todos": df = df[df["turno"] == turno]

    prod_total   = df["unidades_producidas"].sum()
    tasa_def     = (df["unidades_defectuosas"].sum() / prod_total) if prod_total > 0 else 0
    tiempo_prom  = df["tiempo_operacion_min"].mean()
    productividad= (prod_total / df["tiempo_operacion_min"].sum()
                    if df["tiempo_operacion_min"].sum() > 0 else 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Producción total",     f"{prod_total:,.0f}")
    c2.metric("Tasa de defectos",     fmt_pct(tasa_def))
    c3.metric("Tiempo promedio op.",  f"{tiempo_prom:,.1f} min")
    c4.metric("Productividad / min",  f"{productividad:.2f}")

    st.markdown("---")
    a, b = st.columns(2)
    with a:
        temporal = df.groupby("mes", as_index=False)["unidades_producidas"].sum()
        fig = px.line(temporal, x="mes", y="unidades_producidas", markers=True,
                      title="Unidades producidas por mes",
                      color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        comp = produccion.groupby("linea", as_index=False)["tasa_defectos"].mean()
        chart = (
            alt.Chart(comp)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color=CHART_PRIMARY)
            .encode(
                x=alt.X("linea:N", title="Línea"),
                y=alt.Y("tasa_defectos:Q", axis=alt.Axis(format="%"), title="Tasa de defectos"),
                tooltip=["linea", alt.Tooltip("tasa_defectos:Q", format=".2%")]
            )
            .properties(title="Tasa promedio de defectos por línea", height=340)
            .configure_axis(gridColor="#3a4258", labelColor="#7a8499", titleColor="#7a8499")
            .configure_view(stroke="transparent")
        )
        st.altair_chart(chart, use_container_width=True)

    st.dataframe(df, use_container_width=True, height=340)


# ════════════════════════════════════════════════════════════
# MÓDULO 7: FINANZAS
# ════════════════════════════════════════════════════════════
elif modulo == "7. Finanzas":
    st.title("Análisis financiero y económico")
    st.caption("Actividad 2")

    unidad = st.selectbox("Unidad de negocio", sorted(finanzas["unidad_negocio"].unique()))
    df = finanzas[finanzas["unidad_negocio"] == unidad].copy()

    ingresos = df["ingresos"].sum()
    costos   = df["costos"].sum()
    gastos   = df["gastos"].sum()
    utilidad = df["utilidad_operativa"].sum()
    margen   = utilidad / ingresos if ingresos > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ingresos",           fmt_m(ingresos))
    c2.metric("Costos",             fmt_m(costos))
    c3.metric("Gastos",             fmt_m(gastos))
    c4.metric("Utilidad operativa", fmt_m(utilidad))
    c5.metric("Margen operativo",   fmt_pct(margen))

    st.markdown("---")
    a, b = st.columns(2)
    with a:
        tmp = (df[["periodo","ingresos","utilidad_operativa"]]
               .melt(id_vars="periodo", var_name="indicador", value_name="valor"))
        tmp["indicador"] = tmp["indicador"].map(
            {"ingresos": "Ingresos", "utilidad_operativa": "Utilidad operativa"})
        fig = px.line(tmp, x="periodo", y="valor", color="indicador", markers=True,
                      title="Evolución mensual de ingresos y utilidad",
                      color_discrete_sequence=[CHART_PRIMARY, CHART_SECONDARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        comp = finanzas.groupby("unidad_negocio", as_index=False)[["ingresos","utilidad_operativa"]].sum()
        fig = px.bar(comp, x="unidad_negocio", y="utilidad_operativa",
                     title="Utilidad operativa por unidad de negocio",
                     color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="callout-info">'
        "La utilidad operativa permite separar el crecimiento de ingresos de la eficiencia "
        "estructural. Una unidad con ingresos elevados no maximiza necesariamente la "
        "rentabilidad si sostiene costos y gastos proporcionalmente más altos."
        '</div>', unsafe_allow_html=True
    )
    st.dataframe(df, use_container_width=True)


# ════════════════════════════════════════════════════════════
# MÓDULO 8: SALUD
# ════════════════════════════════════════════════════════════
elif modulo == "8. Salud":
    st.title("Indicadores en salud")
    st.caption("Actividad 3")

    servicio = st.selectbox("Servicio clínico",
                            ["Todos"] + sorted(salud["servicio"].unique()))
    df = salud.copy()
    if servicio != "Todos":
        df = df[df["servicio"] == servicio]

    pacientes = df["pacientes_atendidos"].sum()
    espera    = df["tiempo_espera_min"].mean()
    reing     = (df["reingresos"].sum() / df["pacientes_atendidos"].sum()
                 if df["pacientes_atendidos"].sum() > 0 else 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Pacientes atendidos",     f"{pacientes:,.0f}")
    c2.metric("Tiempo promedio espera",  f"{espera:,.1f} min")
    c3.metric("Tasa de reingreso",       fmt_pct(reing))

    st.markdown("---")
    a, b = st.columns(2)
    with a:
        temporal = df.groupby("fecha", as_index=False)["pacientes_atendidos"].sum()
        fig = px.line(temporal, x="fecha", y="pacientes_atendidos", markers=True,
                      title="Pacientes atendidos en el tiempo",
                      color_discrete_sequence=[CHART_PRIMARY])
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        comp = salud.groupby("servicio", as_index=False)["costo_promedio"].mean()
        fig_m, ax_m = plt.subplots(figsize=(7, 4))
        ax_m.bar(comp["servicio"], comp["costo_promedio"],
                 color=CHART_PRIMARY, edgecolor="none")
        ax_m.set_title("Costo promedio por servicio")
        ax_m.set_xlabel("Servicio")
        ax_m.set_ylabel("Costo promedio")
        ax_m.tick_params(axis="x", rotation=15)
        plt_clean(ax_m, fig_m)
        st.pyplot(fig_m)

    st.dataframe(df, use_container_width=True, height=360)


# ════════════════════════════════════════════════════════════
# MÓDULO 9: SQLITE Y RECURSOS
# ════════════════════════════════════════════════════════════
elif modulo == "9. SQLite y recursos":
    st.title("Conexión a datos y recursos persistentes")
    st.markdown(
        "`st.cache_resource` mantiene la conexión activa durante toda la sesión. "
        "La función no se vuelve a ejecutar mientras el recurso siga disponible."
    )

    col_q, _ = st.columns([1, 2])
    consulta = col_q.selectbox(
        "Tabla a consultar",
        ["clientes", "productos", "ventas", "usuarios"]
    )

    try:
        df = pd.read_sql_query(f"SELECT * FROM {consulta}", conn)
        st.success(f"Consulta ejecutada sobre la tabla **{consulta}**. "
                   "La conexión fue reutilizada desde la caché.")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo consultar la tabla: {e}. "
                   "Asegúrese de que `datos_negocio.db` esté en el directorio de la aplicación.")

    st.markdown("---")
    st.markdown("#### Implementación")
    st.code(
        "@st.cache_resource\n"
        "def obtener_conexion():\n"
        "    conexion = sqlite3.connect(\n"
        "        'datos_negocio.db',\n"
        "        check_same_thread=False\n"
        "    )\n"
        "    return conexion\n\n"
        "conexion = obtener_conexion()\n"
        "df = pd.read_sql_query('SELECT * FROM clientes', conexion)",
        language="python"
    )

    st.markdown(
        '<div class="callout-info">'
        "A diferencia de `st.cache_data`, `st.cache_resource` no serializa ni copia el "
        "objeto retornado. Esto es adecuado para conexiones de base de datos y modelos "
        "de aprendizaje automático que deben compartirse entre ejecuciones."
        '</div>', unsafe_allow_html=True
    )


# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Streamlit BI Studio · Maestría en Analítica Aplicada · "
    "Herramientas de Visualización para la Inteligencia de Negocios"
)
