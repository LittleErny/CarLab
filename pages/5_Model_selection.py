import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Инициализация состояния
if "charts" not in st.session_state:
    st.session_state.charts = []

# Демо-данные
df = pd.DataFrame({
    "x": range(10),
    "y": [i ** 2 for i in range(10)],
    "category": ["A", "B"] * 5
})


# Функция для отображения графиков
def render_chart(chart_params):
    plt.figure(figsize=(5, 3))
    if chart_params["type"] == "Scatter":
        sns.scatterplot(data=df, x=chart_params["x"], y=chart_params["y"], hue=chart_params["color"])
    elif chart_params["type"] == "Line":
        sns.lineplot(data=df, x=chart_params["x"], y=chart_params["y"], hue=chart_params["color"])
    elif chart_params["type"] == "Bar":
        sns.barplot(data=df, x=chart_params["x"], y=chart_params["y"], hue=chart_params["color"])
    st.pyplot(plt)


# Добавление нового графика
if st.button("Add new chart"):
    st.session_state.charts.append({
        "type": "Scatter",
        "x": "x",
        "y": "y",
        "color": "category"
    })

# Список графиков
for i, chart in enumerate(st.session_state.charts):
    st.write(f"### Chart {i + 1}")
    render_chart(chart)

    # Редактирование графика
    with st.expander("Edit Chart", expanded=True):
        chart["type"] = st.selectbox("Chart Type", ["Scatter", "Line", "Bar"], key=f"type_{i}")
        chart["x"] = st.selectbox("X-axis", df.columns, key=f"x_{i}")
        chart["y"] = st.selectbox("Y-axis", df.columns, key=f"y_{i}")
        chart["color"] = st.selectbox("Color", df.columns, key=f"color_{i}")

    # Удаление графика
    if st.button(f"Delete Chart {i + 1}"):
        st.session_state.charts.pop(i)
        st.rerun()
