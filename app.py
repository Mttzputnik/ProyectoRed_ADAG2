"""Laboratorio visual e interactivo para Proyecto Red ADAG2.

Ejecutar desde la raíz: streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.allocation import greedy_allocate, brute_force_allocate
from src.instances import (
    generate_coverage_instance,
    generate_concave_marginals,
    generate_graph,
)
from src.selection import greedy_max_coverage, exact_max_coverage, greedy_budgeted_coverage
from src.simulation import run_rounds


st.set_page_config(page_title="Proyecto Red ADAG2 | Laboratorio", page_icon="🕸️", layout="wide")
st.title("🕸️ Proyecto Red ADAG2")
st.caption("Laboratorio visual para explorar selección de nodos, asignación de presupuesto y simulación multirronda.")
st.info(
    "Los datos se generan sintéticamente con una semilla reproducible. "
    "Sirven para comprender los algoritmos; no representan mediciones de una red real."
)

with st.sidebar:
    st.header("Parámetros de la instancia")
    n_nodes = st.slider("Número de nodos", 4, 40, 12)
    universe_size = st.slider("Tamaño del universo", 10, 200, 60, step=5)
    density = st.slider("Densidad de cobertura", 0.05, 0.80, 0.20, step=0.05)
    k = st.slider("Nodos que se pueden seleccionar (k)", 1, n_nodes, min(4, n_nodes))
    units_per_node = st.slider("Unidades disponibles por nodo", 1, 20, 8)
    budget = st.slider("Presupuesto por ronda", 0, n_nodes * units_per_node, min(18, n_nodes * units_per_node))
    rounds_count = st.slider("Número de rondas", 1, 15, 5)
    failure_probability = st.slider("Probabilidad de fallo (p)", 0.0, 1.0, 0.10, step=0.05)
    neighbor_alpha = st.slider("Influencia vecinal (α)", 0.0, 0.20, 0.02, step=0.01)
    edge_probability = st.slider("Probabilidad de conexión", 0.0, 1.0, 0.15, step=0.05)
    seed = st.number_input("Semilla aleatoria", min_value=0, max_value=999999, value=42, step=1)
    run_button = st.button("Generar y ejecutar", type="primary", use_container_width=True)

if "run_config" not in st.session_state:
    st.session_state.run_config = None
if run_button or st.session_state.run_config is None:
    st.session_state.run_config = {
        "n_nodes": n_nodes, "universe_size": universe_size, "density": density,
        "k": k, "units_per_node": units_per_node, "budget": budget,
        "rounds_count": rounds_count, "failure_probability": failure_probability,
        "neighbor_alpha": neighbor_alpha, "edge_probability": edge_probability, "seed": int(seed),
    }

cfg = st.session_state.run_config
sets_by_node = generate_coverage_instance(
    cfg["n_nodes"], cfg["universe_size"], cfg["density"], cfg["seed"]
)
marginals = generate_concave_marginals(
    cfg["n_nodes"], cfg["units_per_node"], cfg["seed"] + 1
)
graph = generate_graph(cfg["n_nodes"], cfg["edge_probability"], cfg["seed"] + 2)
selection = greedy_max_coverage(sets_by_node, cfg["k"])
active_marginals = [marginals[node] for node in selection.selected]
allocation = None
if selection.selected and cfg["budget"] <= sum(map(len, active_marginals)):
    allocation = greedy_allocate(active_marginals, cfg["budget"])

tabs = st.tabs(["Resumen", "1 · Selección", "2 · Presupuesto", "3 · Simulación", "Datos de la red"])

with tabs[0]:
    st.subheader("Vista general de la ejecución")
    a, b, c, d = st.columns(4)
    a.metric("Nodos", cfg["n_nodes"])
    b.metric("Seleccionados", len(selection.selected))
    c.metric("Elementos cubiertos", int(selection.utility))
    d.metric("Rondas", cfg["rounds_count"])
    st.markdown(
        "**Flujo del modelo:** instancia sintética → selección de nodos → "
        "asignación de unidades → fallos e influencia vecinal en rondas sucesivas."
    )
    st.write("**Nodos seleccionados:**", ", ".join(map(str, selection.selected)) or "Ninguno")
    coverage_counts = pd.DataFrame({
        "nodo": list(sets_by_node),
        "elementos cubiertos": [len(values) for values in sets_by_node.values()],
        "seleccionado": [node in selection.selected for node in sets_by_node],
    }).set_index("nodo")
    st.bar_chart(coverage_counts[["elementos cubiertos"]])
    st.caption("La altura de cada barra indica cuántos elementos distintos cubre cada nodo por sí solo.")

with tabs[1]:
    st.subheader("Maximum Coverage: ¿qué nodos cubren más elementos?")
    left, right = st.columns(2)
    left.metric("Cobertura voraz", int(selection.utility))
    left.write("Selección:", list(selection.selected))
    exact_enabled = st.checkbox(
        "Comparar con la solución exacta (enumeración)", value=cfg["n_nodes"] <= 16,
        disabled=cfg["n_nodes"] > 16,
    )
    if exact_enabled and cfg["n_nodes"] <= 16:
        exact = exact_max_coverage(sets_by_node, cfg["k"])
        right.metric("Cobertura óptima exacta", int(exact.utility))
        ratio = selection.utility / exact.utility if exact.utility else 1.0
        right.metric("Razón voraz / exacto", f"{ratio:.1%}")
        st.write("Selección exacta:", list(exact.selected))
    elif cfg["n_nodes"] > 16:
        right.warning("La enumeración exacta se limita a 16 nodos en esta interfaz para evitar tiempos excesivos.")
    st.markdown(
        "En cada paso, el algoritmo añade el nodo que aporta más elementos aún no cubiertos. "
        "El resultado exacto se ofrece solo para instancias pequeñas."
    )
    rows = []
    covered = set()
    for step, node in enumerate(selection.selected, start=1):
        gain = len(sets_by_node[node] - covered)
        rows.append({"paso": step, "nodo": node, "nueva cobertura": gain, "cobertura acumulada": len(covered) + gain})
        covered.update(sets_by_node[node])
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Asignación discreta de presupuesto")
    if allocation is None:
        st.warning(
            "El presupuesto supera la capacidad disponible de los nodos seleccionados "
            "o no hay nodos seleccionados. Reduce el presupuesto o aumenta las unidades disponibles."
        )
    else:
        st.metric("Utilidad total de asignación", f"{allocation.utility:.2f}")
        allocation_df = pd.DataFrame({
            "nodo": selection.selected,
            "unidades asignadas": allocation.allocation,
            "utilidad asignada": [
                sum(marginals[node][:amount])
                for node, amount in zip(selection.selected, allocation.allocation)
            ],
        }).set_index("nodo")
        st.bar_chart(allocation_df[["unidades asignadas"]])
        st.dataframe(allocation_df, use_container_width=True)
        st.markdown(
            "El algoritmo compara la siguiente ganancia marginal disponible de cada nodo "
            "y entrega la próxima unidad al nodo con mayor ganancia. Como las ganancias "
            "de cada fila no crecen, esta estrategia es óptima para el modelo de asignación."
        )
        with st.expander("Ver las ganancias marginales"):
            marginal_table = pd.DataFrame(
                {f"Nodo {node}": marginals[node] for node in selection.selected}
            )
            st.dataframe(marginal_table, use_container_width=True)
        if cfg["n_nodes"] <= 6 and cfg["units_per_node"] <= 8 and cfg["budget"] <= 10:
            if st.checkbox("Verificar contra enumeración exacta"):
                exact_allocation = brute_force_allocate(active_marginals, cfg["budget"])
                st.write("Voraz:", allocation.allocation, f"— utilidad {allocation.utility:.3f}")
                st.write("Exacta:", exact_allocation.allocation, f"— utilidad {exact_allocation.utility:.3f}")

with tabs[3]:
    st.subheader("Simulación multirronda")
    st.caption("Cada ronda aplica fallos independientes. La asignación anterior puede influir en las ganancias de los vecinos.")
    results = run_rounds(
        sets_by_node, marginals, rounds=cfg["rounds_count"], k=cfg["k"],
        budget_per_round=cfg["budget"], failure_probability=cfg["failure_probability"],
        seed=cfg["seed"], graph=graph, neighbor_alpha=cfg["neighbor_alpha"],
    )
    round_df = pd.DataFrame([{
        "ronda": item.round_number,
        "nodos activos": len(item.active_nodes),
        "nodos seleccionados": len(item.selected_nodes),
        "cobertura": item.coverage_utility,
        "unidades asignadas": sum(item.allocation),
        "utilidad de asignación": item.allocation_utility,
    } for item in results]).set_index("ronda")
    st.line_chart(round_df[["cobertura", "utilidad de asignación"]])
    st.dataframe(round_df, use_container_width=True)
    for item in results:
        with st.expander(f"Detalle de la ronda {item.round_number}"):
            x, y, z = st.columns(3)
            x.write("**Activos**")
            x.write(list(item.active_nodes))
            y.write("**Seleccionados**")
            y.write(list(item.selected_nodes))
            z.write("**Asignación (orden de nodos)**")
            z.write(list(item.allocation))
    st.caption("La influencia vecinal escala las ganancias para la ronda siguiente; no implica una garantía de aproximación para toda la simulación.")

with tabs[4]:
    st.subheader("Estructura de la instancia sintética")
    st.write("Cada fila representa un nodo y cada columna un elemento del universo. Un 1 indica que el nodo cubre ese elemento.")
    matrix = pd.DataFrame(
        {f"Elemento {element}": [int(element in sets_by_node[node]) for node in sets_by_node]
         for element in range(cfg["universe_size"])},
        index=[f"Nodo {node}" for node in sets_by_node],
    )
    st.dataframe(matrix, use_container_width=True, height=360)
    st.write("**Matriz de adyacencia:** un 1 indica que dos nodos están conectados.")
    adjacency = pd.DataFrame(
        {f"Nodo {node}": [int(other in graph[node]) for other in graph]
         for node in graph},
        index=[f"Nodo {node}" for node in graph],
    )
    st.dataframe(adjacency, use_container_width=True)
    st.caption(f"Semilla utilizada: {cfg['seed']}. Los mismos parámetros y semilla reproducen la misma instancia.")
