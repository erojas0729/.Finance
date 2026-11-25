import ast
import json
from pathlib import Path
from unittest.mock import patch

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from IPython.display import HTML

st.set_page_config(page_title=".Finance", layout="wide")
st.title(".Finance")

ruta = Path(__file__).with_name("Finance_Spa_Planificador_v2_(1)(1).ipynb")
if not ruta.is_file():
    st.error(f"Sube {ruta.name} a la misma carpeta que app.py.")
    st.stop()

notebook = json.loads(ruta.read_text(encoding="utf-8"))
celdas = []
for numero, celda in enumerate(notebook["cells"], start=1):
    if celda["cell_type"] == "code":
        codigo = "".join(celda["source"])
        nombre = f"{ruta.name}, celda {numero}"
        celdas.append((nombre, ast.parse(codigo, filename=nombre)))

# Usa el número de clientes del notebook como valor inicial.
for _, arbol in celdas:
    for instruccion in arbol.body:
        if not isinstance(instruccion, ast.Assign):
            continue
        if (
            len(instruccion.targets) == 1
            and isinstance(instruccion.targets[0], ast.Name)
            and instruccion.targets[0].id == "clientes_esperados"
            and isinstance(instruccion.value, ast.Constant)
            and type(instruccion.value.value) is int
        ):
            clientes = st.number_input(
                "Clientes esperados hoy",
                min_value=0,
                value=instruccion.value.value,
                step=1,
                key="clientes_esperados",
            )
            instruccion.value = ast.copy_location(
                ast.Constant(value=int(clientes)), instruccion.value
            )

def mostrar(*resultados, **_):
    for resultado in resultados:
        if isinstance(resultado, HTML):
            st.html(resultado.data)
        elif isinstance(resultado, (pd.DataFrame, pd.Series)):
            st.dataframe(resultado)
        else:
            st.write(resultado)

def mostrar_graficas(*args, **kwargs):
    for numero in plt.get_fignums():
        figura = plt.figure(numero)
        st.pyplot(figura)
        plt.close(figura)

contexto = {"__name__": "__main__"}
try:
    with patch("IPython.display.display", mostrar), patch.object(
        plt, "show", mostrar_graficas
    ):
        contexto["display"] = mostrar
        for nombre, arbol in celdas:
            exec(compile(arbol, nombre, "exec"), contexto)
except Exception as error:
    st.error(f"Error al ejecutar {nombre}.")
    st.exception(error)
finally:
    plt.close("all")
