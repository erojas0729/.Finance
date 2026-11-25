# Importamos las librerías básicas para tablas, gráficas y tarjetas visuales
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Paleta de colores del spa (códigos hexadecimales)
color_fondo = "#FBF7EF"      # crema marfil
color_tarjeta = "#FFFDF9"    # blanco cálido
color_borde = "#E5D9C3"      # arena suave
color_texto = "#2C251E"      # carbón cálido
color_oro = "#B8923A"        # dorado champán (para dar lujo)
color_taupe = "#8C7B6B"      # gris pardo
color_arena = "#C8B08A"      # beige dorado
color_salvia = "#5F8567"     # verde salvia (para la ganancia)

# Función auxiliar: convierte un número en texto con formato de pesos colombianos.
# Ejemplo: formato_cop(2040000) devuelve "$2.040.000"
def formato_cop(valor):
    texto = f"{abs(valor):,.0f}"        # separa los miles con coma: 2,040,000
    texto = texto.replace(",", ".")     # cambia la coma por punto: 2.040.000
    if valor < 0:
        return "-$" + texto
    return "$" + texto


# Función 1: cuántos trabajadores se necesitan (siempre redondeando hacia arriba)
def personal_necesario(clientes, capacidad):
    if clientes <= 0:
        return 0
    personal = clientes // capacidad          # división entera: cuántos grupos completos hay
    if clientes % capacidad > 0:              # % da el resto: si sobran clientes...
        personal = personal + 1               # ...hace falta un trabajador más
    return personal

# Función 2: calcula pesos automáticos de demanda según precio (más accesible = más frecuente)
def calcular_pesos_automaticos(lista_precios):
    inversos = []                             # guarda 1 / precio de cada servicio
    suma_inversos = 0
    for p in lista_precios:
        inv = 1 / p                           # a menor precio, mayor peso relativo
        inversos.append(inv)
        suma_inversos = suma_inversos + inv

    pesos = []                                # normaliza los pesos para que sumen 1 (100%)
    for inv in inversos:
        pesos.append(inv / suma_inversos)
    return pesos

# Función 3: reparte los clientes entre N servicios (cantidad variable)
def repartir_clientes_variable(clientes, lista_precios):
    n = len(lista_precios)                    # cantidad de servicios configurados
    pesos = calcular_pesos_automaticos(lista_precios)
    reparto = [0] * n                         # lista con ceros para guardar clientes por servicio
    asignados = 0

    # Asignamos del segundo servicio en adelante usando int(x + 0.5) para que todo .5 suba
    for i in range(1, n):
        cant = min(clientes - asignados, int(clientes * pesos[i] + 0.5))
        reparto[i] = cant
        asignados = asignados + cant

    # El primer servicio recibe el resto para conservar siempre el total exacto de clientes
    reparto[0] = clientes - asignados
    return reparto

# Función 4: encuentra el servicio más frecuente de la jornada
def obtener_servicio_mas_frecuente(nombres, reparto):
    mayor_clientes = -1                       # guarda la cantidad más alta encontrada
    indice_mayor = 0                          # guarda la posición del servicio ganador
    for i in range(len(reparto)):
        if reparto[i] > mayor_clientes:
            mayor_clientes = reparto[i]
            indice_mayor = i
    return nombres[indice_mayor], mayor_clientes

# Función 5: asigna masajistas en modo "automatica" o "manual"
def asignar_masajistas(lista_masajistas, requeridos, modo="automatica", seleccion_manual=None):
    if requeridos == 0:
        return [], "Sin turnos requeridos"

    if modo == "automatica":
        # Toma automáticamente los primeros masajistas disponibles de la lista
        asignados = lista_masajistas[:requeridos]
        if len(asignados) < requeridos:
            faltan = requeridos - len(asignados)
            estado = f"Asignación automática parcial: faltan {faltan} masajista(s) en la lista."
        else:
            estado = "Asignación automática completada según disponibilidad."
        return asignados, estado

    elif modo == "manual":
        # Verifica que los nombres elegidos manualmente existan en la lista y no se repitan
        if seleccion_manual is None:
            seleccion_manual = []
        asignados = []
        for nombre in seleccion_manual:
            if nombre in lista_masajistas and nombre not in asignados:
                asignados.append(nombre)
        if len(asignados) < requeridos:
            estado = f"Asignación manual incompleta: elegiste {len(asignados)} de {requeridos} requeridos."
        elif len(asignados) > requeridos:
            estado = f"Asignación manual con sobrepersonal: elegiste {len(asignados)} (se requieren {requeridos})."
        else:
            estado = "Asignación manual confirmada y exacta."
        return asignados, estado

    return [], "Modo de asignación no reconocido."

# Función 6: calcula todos los resultados de una jornada y los devuelve en un diccionario
def calcular_jornada_finance(clientes, modo_asignacion="automatica", seleccion_manual=None):
    # Si la demanda supera la capacidad máxima de cabinas, la operación no es viable
    if clientes > capacidad_maxima:
        return {
            "viable": False,
            "clientes": clientes,
            "sin_atender": clientes - capacidad_maxima,
        }

    # Calculamos personal requerido en masajistas y recepción
    masajistas_req = personal_necesario(clientes, clientes_por_masajista)
    recepcion_req = personal_necesario(clientes, clientes_por_recepcion)

    # Si es manual y el usuario eligió una lista, se paga según los elegidos
    if modo_asignacion == "manual" and seleccion_manual is not None and len(seleccion_manual) > 0:
        masajistas_pagados = len(seleccion_manual)
    else:
        masajistas_pagados = masajistas_req

    # Ejecutamos la asignación automática o manual de masajistas
    equipo_asignado, nota_equipo = asignar_masajistas(
        masajistas, masajistas_req, modo=modo_asignacion, seleccion_manual=seleccion_manual
    )

    # Repartimos los clientes entre los servicios y hallamos el servicio más frecuente
    reparto = repartir_clientes_variable(clientes, precios)
    servicio_top, clientes_top = obtener_servicio_mas_frecuente(nombres_servicios, reparto)

    # Sumamos ingresos y costos de insumos recorriendo todos los servicios
    ingresos = 0
    costo_insumos_total = 0
    for i in range(len(nombres_servicios)):
        ingresos = ingresos + reparto[i] * precios[i]
        costo_insumos_total = costo_insumos_total + reparto[i] * costos_insumos[i]

    # Costos totales incluyen personal, insumos y el costo fijo diario (mensual ÷ 30)
    costo_personal = masajistas_pagados * costo_turno_masajista + recepcion_req * costo_turno_recepcion
    costos_totales = costo_personal + costo_insumos_total + costo_fijo_jornada
    ganancia = ingresos - costos_totales

    # Margen neto y utilización de capacidad
    if ingresos > 0:
        margen = (ganancia / ingresos) * 100
    else:
        margen = 0

    if masajistas_pagados > 0:
        utilizacion = (clientes / (masajistas_pagados * clientes_por_masajista)) * 100
    else:
        utilizacion = 0

    return {
        "viable": True,
        "clientes": clientes,
        "masajistas_req": masajistas_req,
        "masajistas_pagados": masajistas_pagados,
        "recepcion_req": recepcion_req,
        "equipo_asignado": equipo_asignado,
        "nota_equipo": nota_equipo,
        "reparto": reparto,
        "servicio_top": servicio_top,
        "clientes_top": clientes_top,
        "ingresos": ingresos,
        "costo_personal": costo_personal,
        "costo_insumos": costo_insumos_total,
        "costo_fijo_jornada": costo_fijo_jornada,
        "costos_totales": costos_totales,
        "ganancia": ganancia,
        "proyeccion_mensual": ganancia * dias_mes,
        "margen": margen,
        "utilizacion": utilizacion,
    }


st.set_page_config(page_title=".Finance", layout="wide")
st.markdown(
    """
    <style>
    .stApp {background: #FBF7EF; color: #2C251E;}
    h1, h2, h3 {font-family: Georgia, serif; color: #2C251E;}
    [data-testid="stMetric"] {
        background: #FFFDF9; border: 1px solid #E5D9C3;
        border-radius: 12px; padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title(".Finance")
st.write("Planifica turnos, costos y ganancias para tu spa o salón de belleza.")

modo = st.radio("Datos del negocio", ["Mi negocio", "Ejemplo Sunny Side"], horizontal=True)
es_ejemplo = modo == "Ejemplo Sunny Side"
dias_mes = 30

if es_ejemplo:
    # Datos precargados del caso base: Sunny Side Luxury Spa
    nombre_spa = "Sunny Side Luxury Spa"
    cabinas = 8                         # número de cabinas disponibles
    clientes_por_masajista = 3          # clientes que atiende cada masajista por turno
    clientes_por_recepcion = 10         # clientes que atiende cada persona de recepción
    costo_turno_masajista = 200000      # COP por turno de masajista
    costo_turno_recepcion = 120000      # COP por turno de recepción/apoyo

    # Costos fijos mensuales (30 días): solo estas 3 variables desglosadas
    aseo = 900000                       # COP al mes en aseo y lavandería
    arriendo = 6000000                  # COP al mes en arriendo del local
    servicios = 1200000                 # COP al mes en servicios públicos (agua, luz, gas)

    # Lista de masajistas disponibles en el spa
    masajistas = [
        "Valentina", "Camila", "Sofía", "Mariana",
        "Isabella", "Lucía", "Andrea", "Natalia"
    ]

    # Catálogo de servicios: listas paralelas (posición 0, 1, 2...)
    numero_servicios = 3                # cantidad total de servicios en el catálogo
    nombres_servicios = [
        "Masaje relajante",
        "Facial hidratante premium",
        "Ritual corporal"
    ]
    precios = [200000, 260000, 360000]  # COP por cliente para cada servicio
    costos_insumos = [30000, 50000, 90000]  # COP de insumos por cliente para cada servicio
else:
    with st.expander("1. Configura tu negocio", expanded=True):
        nombre_spa = st.text_input("Nombre del negocio").strip()
        c1, c2, c3 = st.columns(3)
        cabinas = c1.number_input("Cabinas o puestos", min_value=1, value=1)
        clientes_por_masajista = c2.number_input(
            "Clientes por profesional por jornada", min_value=1, value=3
        )
        clientes_por_recepcion = c3.number_input(
            "Clientes por persona de recepción", min_value=1, value=10
        )
        c1, c2 = st.columns(2)
        costo_turno_masajista = c1.number_input(
            "Pago por turno de cada profesional (COP)", min_value=0, step=10000
        )
        costo_turno_recepcion = c2.number_input(
            "Pago por turno de recepción (COP)", min_value=0, step=10000
        )
        st.markdown("**Costos fijos mensuales**")
        c1, c2, c3 = st.columns(3)
        aseo = c1.number_input("Aseo (COP)", min_value=0, step=10000)
        arriendo = c2.number_input("Arriendo (COP)", min_value=0, step=10000)
        servicios = c3.number_input("Servicios públicos (COP)", min_value=0, step=10000)
        equipo = st.text_area("Profesionales disponibles (un nombre por línea)")
        masajistas = []
        for linea in equipo.splitlines():
            nombre = linea.strip()
            if nombre and nombre not in masajistas:
                masajistas.append(nombre)

    with st.expander("2. Agrega tus servicios", expanded=True):
        numero_servicios = st.number_input("Cantidad de servicios", min_value=1, value=1)
        nombres_servicios = []
        precios = []
        costos_insumos = []
        for i in range(numero_servicios):
            c1, c2, c3 = st.columns([2, 1, 1])
            nombres_servicios.append(c1.text_input(f"Nombre del servicio {i + 1}").strip())
            precios.append(c2.number_input(
                f"Precio {i + 1} (COP)", min_value=1, value=None, step=5000
            ))
            costos_insumos.append(c3.number_input(
                f"Insumos {i + 1} (COP)", min_value=0, step=1000
            ))

    if not all(nombres_servicios) or None in precios:
        st.info("Completa el nombre y el precio de cada servicio para calcular la jornada.")
        st.stop()
    if len(set(nombres_servicios)) != numero_servicios:
        st.warning("Escribe un nombre diferente para cada servicio.")
        st.stop()

costosfijos = aseo + arriendo + servicios
costo_fijo_jornada = costosfijos / dias_mes
capacidad_maxima = cabinas * clientes_por_masajista

st.header(nombre_spa or "Mi negocio")
c1, c2, c3 = st.columns(3)
c1.metric("Capacidad por jornada", f"{capacidad_maxima} clientes")
c2.metric("Profesionales registrados", len(masajistas))
c3.metric("Costos fijos por jornada", formato_cop(costo_fijo_jornada))
st.caption(f"Costos fijos mensuales: {formato_cop(costosfijos)} repartidos en 30 días.")

st.subheader("Planifica la jornada")
c1, c2 = st.columns(2)
clientes = c1.number_input(
    "Clientes esperados", min_value=0, value=16 if es_ejemplo else 0,
    key=f"clientes_{modo}",
)
tipo = c2.radio("Asignación de profesionales", ["Automática", "Manual"], horizontal=True)
seleccion = None
modo_asignacion = "automatica"
if tipo == "Manual":
    modo_asignacion = "manual"
    seleccion = st.multiselect("Profesionales para esta jornada", masajistas)

jornada, catalogo, escenarios = st.tabs(["Jornada", "Catálogo de servicios", "Escenarios"])
with jornada:
    res = calcular_jornada_finance(clientes, modo_asignacion, seleccion)
    if not res["viable"]:
        st.warning(
            f"Solicitaste {clientes} cupos. Hay capacidad para {capacidad_maxima} "
            f"y quedarían {res['sin_atender']} clientes sin atender."
        )
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos", formato_cop(res["ingresos"]))
        c2.metric("Costos totales", formato_cop(res["costos_totales"]))
        c3.metric("Ganancia estimada", formato_cop(res["ganancia"]))

        if len(res["equipo_asignado"]) != res["masajistas_req"]:
            st.warning(
                f"Se requieren {res['masajistas_req']} profesionales. "
                f"Hay {len(res['equipo_asignado'])} asignados para esta jornada."
            )
        equipo_asignado = ", ".join(res["equipo_asignado"]) or "Ninguno"
        st.write(
            f"**Equipo asignado:** {equipo_asignado} · "
            f"**Recepción requerida:** {res['recepcion_req']}"
        )
        if clientes > 0:
            st.write(
                f"**Servicio más frecuente:** {res['servicio_top']} "
                f"({res['clientes_top']} clientes)"
            )

        filas_jornada = []
        for i in range(numero_servicios):
            cantidad = res["reparto"][i]
            filas_jornada.append({
                "Servicio": nombres_servicios[i],
                "Clientes": cantidad,
                "Ingresos": formato_cop(cantidad * precios[i]),
                "Insumos": formato_cop(cantidad * costos_insumos[i]),
            })
        st.dataframe(pd.DataFrame(filas_jornada), hide_index=True)

        st.subheader("Costos y resultado de la jornada")
        etiquetas = ["Personal", "Insumos", "Costos fijos", "Ganancia"]
        valores = [
            res["costo_personal"], res["costo_insumos"],
            res["costo_fijo_jornada"], res["ganancia"],
        ]
        fig, ax = plt.subplots(figsize=(8, 3.3), facecolor=color_fondo)
        ax.set_facecolor(color_tarjeta)
        ax.barh(etiquetas, [valor / 1000000 for valor in valores],
                color=[color_taupe, color_arena, color_oro, color_salvia])
        ax.invert_yaxis()
        ax.axvline(0, color=color_texto, linewidth=0.8)
        ax.set_xlabel("Millones de COP")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            f"Margen: {res['margen']:.1f}% · "
            f"Utilización del personal presupuestado: {res['utilizacion']:.1f}% · "
            f"Proyección si se repite la jornada 30 veces: {formato_cop(res['proyeccion_mensual'])}."
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
    st.caption("La demanda por servicio se estima según el precio, como en el modelo de .Finance.")

with escenarios:
    # Definimos los tres escenarios de ocupación (33%, 67% y 100% de la capacidad máxima)
    nombres_escenarios = ["Baja afluencia", "Ocupación media", "Agenda llena"]
    clientes_escenarios = [
        max(1, capacidad_maxima // 3),          # un tercio de la capacidad
        max(1, (capacidad_maxima * 2) // 3),    # dos tercios de la capacidad
        capacidad_maxima                        # capacidad máxima completa
    ]

    # Listas para construir la tabla comparativa y las barras de la gráfica
    tabla_esc = []
    ingresos_graf = []
    costos_graf = []
    ganancias_graf = []

    # Calculamos cada escenario usando nuestra función principal
    for idx in range(len(nombres_escenarios)):
        c_esc = clientes_escenarios[idx]
        r = calcular_jornada_finance(c_esc, modo_asignacion="automatica")
        ingresos_graf.append(r["ingresos"] / 1000000)         # pasamos a millones de COP
        costos_graf.append(r["costos_totales"] / 1000000)
        ganancias_graf.append(r["ganancia"] / 1000000)

        tabla_esc.append({
            "Escenario": nombres_escenarios[idx],
            "Clientes": c_esc,
            "Servicio más frecuente": r["servicio_top"],
            "Masajistas": r["masajistas_req"],
            "Ingresos": formato_cop(r["ingresos"]),
            "Costos Totales": formato_cop(r["costos_totales"]),
            "Ganancia Jornada": formato_cop(r["ganancia"]),
            "Proyección 30 días": formato_cop(r["proyeccion_mensual"]),
            "Margen": f"{r['margen']:.1f}%"
        })

    st.dataframe(pd.DataFrame(tabla_esc), hide_index=True)
    st.caption("Escenarios según capacidad de cabinas y costo del personal requerido.")

    # ---------- GRÁFICA ESTÉTICA CON PALETA .FINANCE ----------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.patch.set_facecolor(color_fondo)        # fondo exterior crema marfil
    ax.set_facecolor(color_tarjeta)             # fondo interior blanco cálido

    x = [0, 1, 2]
    ancho = 0.25                                # ancho de cada barra

    # Dibujamos las 3 barras por escenario: ingresos, costos totales y ganancia neta
    ax.bar([p - ancho for p in x], ingresos_graf, width=ancho, label="Ingresos", color=color_oro)
    ax.bar(x, costos_graf, width=ancho, label="Costos Totales (incl. Fijos)", color=color_taupe)
    ax.bar([p + ancho for p in x], ganancias_graf, width=ancho, label="Ganancia Neta", color=color_salvia)

    # Detalles visuales limpios de la gráfica
    ax.axhline(0, color=color_texto, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(nombres_escenarios, fontsize=11, color=color_texto)
    ax.set_ylabel("Millones de COP", fontsize=11, color=color_texto)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(color_borde)
    ax.spines["bottom"].set_color(color_borde)
    ax.legend(frameon=False)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)