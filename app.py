import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# Paleta de .Finance
FONDO = "#FFF9F5"
ROSA_CLARO = "#FFF0F5"
BORDE = "#EDCCD9"
TEXTO = "#3A2235"
CIRUELA = "#6B315C"
ROSA = "#C16C8A"
AMARILLO = "#FFE5A0"
VERDE = "#5F8567"
ROJO = "#B54747"
DIAS_MES = 30

SERVICIOS_EJEMPLO = [
    ("Masaje relajante", 200000, 30000),
    ("Facial hidratante premium", 260000, 50000),
    ("Ritual corporal", 360000, 90000),
]
EQUIPO_EJEMPLO = (
    "Valentina\nCamila\nSofía\nMariana\nIsabella\nLucía\nAndrea\nNatalia"
)


def formato_cop(valor):
    texto = f"{abs(valor):,.0f}".replace(",", ".")
    if valor < 0:
        return "-$" + texto
    return "$" + texto


def personal_necesario(clientes, capacidad):
    personal = clientes // capacidad
    if clientes % capacidad > 0:
        personal += 1
    return personal


def repartir_clientes(clientes, precios):
    inversos = []
    for precio in precios:
        inversos.append(1 / precio)

    total_inversos = sum(inversos)
    reparto = [0] * len(precios)
    pendientes = clientes
    for i in range(1, len(precios)):
        peso = inversos[i] / total_inversos
        cantidad = min(pendientes, int(clientes * peso + 0.5))
        reparto[i] = cantidad
        pendientes -= cantidad

    reparto[0] = pendientes
    return reparto


def calcular_jornada(clientes, seleccion_manual=None):
    profesionales = personal_necesario(clientes, clientes_por_profesional)
    recepcion = personal_necesario(clientes, clientes_por_recepcion)

    if clientes == 0:
        asignados = []
    elif seleccion_manual is None:
        asignados = equipo[:profesionales]
    else:
        asignados = seleccion_manual

    turnos_pagados = profesionales
    if seleccion_manual and clientes > 0:
        turnos_pagados = len(asignados)

    reparto = repartir_clientes(clientes, precios)
    ingresos = 0
    costo_insumos = 0
    filas = []
    indice_top = 0

    for i in range(len(nombres_servicios)):
        ingreso_servicio = reparto[i] * precios[i]
        insumos_servicio = reparto[i] * costos_insumos[i]
        ingresos += ingreso_servicio
        costo_insumos += insumos_servicio

        if reparto[i] > reparto[indice_top]:
            indice_top = i

        filas.append({
            "Servicio": nombres_servicios[i],
            "Clientes": reparto[i],
            "Ingresos": formato_cop(ingreso_servicio),
            "Insumos": formato_cop(insumos_servicio),
        })

    costo_personal = turnos_pagados * pago_profesional + recepcion * pago_recepcion
    costos_totales = costo_personal + costo_insumos + costo_fijo_jornada
    ganancia = ingresos - costos_totales
    margen = ganancia / ingresos * 100 if ingresos else 0
    capacidad_personal = turnos_pagados * clientes_por_profesional
    utilizacion = clientes / capacidad_personal * 100 if capacidad_personal else 0

    return {
        "profesionales": profesionales,
        "recepcion": recepcion,
        "asignados": asignados,
        "filas": filas,
        "servicio_top": nombres_servicios[indice_top],
        "clientes_top": reparto[indice_top],
        "ingresos": ingresos,
        "costo_personal": costo_personal,
        "costo_insumos": costo_insumos,
        "costos_totales": costos_totales,
        "ganancia": ganancia,
        "margen": margen,
        "utilizacion": utilizacion,
        "proyeccion_mensual": ganancia * DIAS_MES,
    }


st.set_page_config(page_title=".Finance", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{background: {FONDO}; color: {TEXTO};}}
    h1, h2, h3 {{font-family: Georgia, serif; color: {CIRUELA};}}
    [data-testid="stMetric"] {{
        background: {ROSA_CLARO};
        border: 1px solid {BORDE};
        border-radius: 14px;
        padding: 14px;
    }}
    .finance-card {{
        border: 1px solid {BORDE};
        border-radius: 16px;
        padding: 18px;
    }}
    .finance-card h3 {{margin: 0 0 6px; font-size: 1.2rem;}}
    .finance-card p {{margin: 0; color: {TEXTO};}}
    .finance-own {{background: {ROSA_CLARO};}}
    .finance-demo {{background: {AMARILLO};}}
    .stButton button[kind="primary"] {{
        background: {CIRUELA};
        border-color: {CIRUELA};
        color: white;
    }}
    .stButton button[kind="secondary"] {{
        background: {FONDO};
        border-color: {CIRUELA};
        color: {CIRUELA};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(".Finance")
st.write("Planifica turnos, costos y ganancias para tu spa o salón de belleza.")

if "modo_finance" not in st.session_state:
    st.session_state["modo_finance"] = ""

col_negocio, col_ejemplo = st.columns(2)

with col_negocio:
    st.markdown(
        """
        <div class="finance-card finance-own">
            <h3>Mi negocio</h3>
            <p>Ingresa tus servicios, costos y equipo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Configurar mi negocio", type="primary"):
        st.session_state["modo_finance"] = "negocio"

with col_ejemplo:
    st.markdown(
        """
        <div class="finance-card finance-demo">
            <h3>Ejemplo Sunny Side</h3>
            <p>Explora el planificador con datos que puedes editar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Probar con datos de ejemplo"):
        st.session_state["modo_finance"] = "ejemplo"

modo = st.session_state["modo_finance"]
if not modo:
    st.stop()

es_ejemplo = modo == "ejemplo"

with st.expander("1. Configura tu negocio", expanded=True):
    nombre_negocio = st.text_input(
        "Nombre del negocio",
        value="Sunny Side Luxury Spa" if es_ejemplo else "",
        key=f"nombre_{modo}",
    ).strip()

    c1, c2, c3 = st.columns(3)
    cabinas = c1.number_input(
        "Cabinas o puestos", min_value=1,
        value=8 if es_ejemplo else 1, key=f"cabinas_{modo}",
    )
    clientes_por_profesional = c2.number_input(
        "Clientes por profesional por jornada",
        min_value=1, value=3, key=f"capacidad_profesional_{modo}",
    )
    clientes_por_recepcion = c3.number_input(
        "Clientes por persona de recepción",
        min_value=1, value=10, key=f"capacidad_recepcion_{modo}",
    )

    c1, c2 = st.columns(2)
    pago_profesional = c1.number_input(
        "Pago por turno de cada profesional (COP)",
        min_value=0, value=200000 if es_ejemplo else 0,
        step=10000, key=f"pago_profesional_{modo}",
    )
    pago_recepcion = c2.number_input(
        "Pago por turno de recepción (COP)",
        min_value=0, value=120000 if es_ejemplo else 0,
        step=10000, key=f"pago_recepcion_{modo}",
    )

    st.markdown("**Costos fijos mensuales**")
    c1, c2, c3 = st.columns(3)
    aseo = c1.number_input(
        "Aseo (COP)", min_value=0, value=900000 if es_ejemplo else 0,
        step=10000, key=f"aseo_{modo}",
    )
    arriendo = c2.number_input(
        "Arriendo (COP)", min_value=0, value=6000000 if es_ejemplo else 0,
        step=10000, key=f"arriendo_{modo}",
    )
    servicios_publicos = c3.number_input(
        "Servicios públicos (COP)", min_value=0,
        value=1200000 if es_ejemplo else 0,
        step=10000, key=f"servicios_publicos_{modo}",
    )

    texto_equipo = st.text_area(
        "Profesionales disponibles (un nombre por línea)",
        value=EQUIPO_EJEMPLO if es_ejemplo else "",
        key=f"equipo_{modo}",
    )
    equipo = []
    for linea in texto_equipo.splitlines():
        nombre = linea.strip()
        if nombre and nombre not in equipo:
            equipo.append(nombre)

with st.expander("2. Agrega tus servicios", expanded=True):
    numero_servicios = st.number_input(
        "Cantidad de servicios", min_value=1,
        value=len(SERVICIOS_EJEMPLO) if es_ejemplo else 1,
        key=f"cantidad_servicios_{modo}",
    )
    nombres_servicios = []
    precios = []
    costos_insumos = []

    for i in range(numero_servicios):
        nombre_base, precio_base, insumos_base = "", None, 0
        if es_ejemplo and i < len(SERVICIOS_EJEMPLO):
            nombre_base, precio_base, insumos_base = SERVICIOS_EJEMPLO[i]

        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input(
            f"Nombre del servicio {i + 1}", value=nombre_base,
            key=f"nombre_servicio_{modo}_{i}",
        ).strip()
        precio = c2.number_input(
            f"Precio {i + 1} (COP)", min_value=1, value=precio_base,
            step=1000, key=f"precio_{modo}_{i}",
        )
        insumos = c3.number_input(
            f"Insumos {i + 1} (COP)", min_value=0, value=insumos_base,
            step=1000, key=f"insumos_{modo}_{i}",
        )

        nombres_servicios.append(nombre)
        precios.append(precio)
        costos_insumos.append(insumos)

if not all(nombres_servicios) or None in precios:
    st.info("Completa el nombre y el precio de cada servicio para calcular la jornada.")
    st.stop()

if len(set(nombres_servicios)) != numero_servicios:
    st.warning("Escribe un nombre diferente para cada servicio.")
    st.stop()

costos_fijos = aseo + arriendo + servicios_publicos
costo_fijo_jornada = costos_fijos / DIAS_MES
capacidad_maxima = cabinas * clientes_por_profesional

st.header(nombre_negocio or "Mi negocio")
c1, c2, c3 = st.columns(3)
c1.metric("Capacidad por jornada", f"{capacidad_maxima} clientes")
c2.metric("Profesionales registrados", len(equipo))
c3.metric("Costos fijos por jornada", formato_cop(costo_fijo_jornada))
st.caption(f"Costos fijos mensuales: {formato_cop(costos_fijos)} repartidos en 30 días.")

st.subheader("Planifica la jornada")
c1, c2 = st.columns(2)
clientes = c1.number_input(
    "Clientes esperados", min_value=0,
    value=16 if es_ejemplo else 0, key=f"clientes_{modo}",
)
tipo_asignacion = c2.radio(
    "Asignación de profesionales", ["Automática", "Manual"],
    horizontal=True, key=f"asignacion_{modo}",
)
seleccion = None
if tipo_asignacion == "Manual":
    seleccion = st.multiselect(
        "Profesionales para esta jornada", equipo, key=f"seleccion_{modo}",
    )

jornada, catalogo, escenarios = st.tabs(
    ["Jornada", "Catálogo de servicios", "Escenarios"]
)

with jornada:
    if clientes > capacidad_maxima:
        st.warning(
            f"Hay capacidad para {capacidad_maxima} clientes. "
            f"Con {clientes} solicitudes quedarían "
            f"{clientes - capacidad_maxima} clientes sin atender."
        )
    else:
        resultado = calcular_jornada(clientes, seleccion)
        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos", formato_cop(resultado["ingresos"]))
        c2.metric("Costos totales", formato_cop(resultado["costos_totales"]))
        c3.metric("Ganancia estimada", formato_cop(resultado["ganancia"]))

        asignados = resultado["asignados"]
        requeridos = resultado["profesionales"]
        if len(asignados) != requeridos:
            st.warning(
                f"Se requieren {requeridos} profesionales y "
                f"hay {len(asignados)} asignados."
            )
        st.write(
            f"**Equipo asignado:** {', '.join(asignados) or 'Ninguno'} · "
            f"**Recepción requerida:** {resultado['recepcion']}"
        )
        if clientes > 0:
            st.write(
                f"**Servicio más frecuente:** {resultado['servicio_top']} "
                f"({resultado['clientes_top']} clientes)"
            )

        st.dataframe(pd.DataFrame(resultado["filas"]), hide_index=True)
        st.subheader("Costos y resultado de la jornada")

        valores = [
            resultado["costo_personal"],
            resultado["costo_insumos"],
            costo_fijo_jornada,
            resultado["ganancia"],
        ]
        color_ganancia = VERDE if resultado["ganancia"] >= 0 else ROJO
        fig, ax = plt.subplots(figsize=(8, 3.3), facecolor=FONDO)
        ax.set_facecolor(ROSA_CLARO)
        ax.barh(
            ["Personal", "Insumos", "Costos fijos", "Ganancia"],
            [valor / 1000000 for valor in valores],
            color=[CIRUELA, ROSA, AMARILLO, color_ganancia],
        )
        ax.invert_yaxis()
        ax.axvline(0, color=TEXTO, linewidth=0.8)
        ax.set_xlabel("Millones de COP")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.caption(
            f"Margen: {resultado['margen']:.1f}% · "
            f"Utilización del personal presupuestado: {resultado['utilizacion']:.1f}% · "
            f"Proyección si se repite la jornada 30 veces: "
            f"{formato_cop(resultado['proyeccion_mensual'])}."
        )

with catalogo:
    filas_catalogo = []
    for i in range(numero_servicios):
        filas_catalogo.append({
            "Servicio": nombres_servicios[i],
            "Precio": formato_cop(precios[i]),
            "Insumos": formato_cop(costos_insumos[i]),
            "Insumos (% del precio)": f"{costos_insumos[i] / precios[i] * 100:.0f}%",
            "Contribución por cliente": formato_cop(precios[i] - costos_insumos[i]),
        })
    st.dataframe(pd.DataFrame(filas_catalogo), hide_index=True)
    st.caption("La demanda de cada servicio se estima según su precio.")

with escenarios:
    nombres_escenarios = ["Baja afluencia", "Ocupación media", "Agenda llena"]
    clientes_escenarios = [
        max(1, capacidad_maxima // 3),
        max(1, capacidad_maxima * 2 // 3),
        capacidad_maxima,
    ]

    filas_escenarios = []
    ingresos_grafica = []
    costos_grafica = []
    ganancias_grafica = []

    for i in range(len(nombres_escenarios)):
        cantidad = clientes_escenarios[i]
        resultado = calcular_jornada(cantidad)
        filas_escenarios.append({
            "Escenario": nombres_escenarios[i],
            "Clientes": cantidad,
            "Servicio más frecuente": resultado["servicio_top"],
            "Profesionales": resultado["profesionales"],
            "Ingresos": formato_cop(resultado["ingresos"]),
            "Costos totales": formato_cop(resultado["costos_totales"]),
            "Ganancia jornada": formato_cop(resultado["ganancia"]),
            "Proyección 30 días": formato_cop(resultado["proyeccion_mensual"]),
            "Margen": f"{resultado['margen']:.1f}%",
        })
        ingresos_grafica.append(resultado["ingresos"] / 1000000)
        costos_grafica.append(resultado["costos_totales"] / 1000000)
        ganancias_grafica.append(resultado["ganancia"] / 1000000)

    st.dataframe(pd.DataFrame(filas_escenarios), hide_index=True)
    st.caption("Los escenarios usan la capacidad de cabinas y el costo del personal requerido.")

    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=FONDO)
    ax.set_facecolor(ROSA_CLARO)
    posiciones = [0, 1, 2]
    ancho = 0.25
    colores_ganancia = [VERDE if valor >= 0 else ROJO for valor in ganancias_grafica]

    ax.bar(
        [pos - ancho for pos in posiciones], ingresos_grafica,
        width=ancho, label="Ingresos", color=CIRUELA,
    )
    ax.bar(posiciones, costos_grafica, width=ancho, label="Costos", color=ROSA)
    ax.bar(
        [pos + ancho for pos in posiciones], ganancias_grafica,
        width=ancho, label="Ganancia o pérdida", color=colores_ganancia,
    )
    ax.axhline(0, color=TEXTO, linewidth=0.8)
    ax.set_xticks(posiciones)
    ax.set_xticklabels(nombres_escenarios)
    ax.set_ylabel("Millones de COP")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

