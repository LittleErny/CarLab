import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_sample_graph():
    sample_graph = {
        "id": st.session_state.chart_counter,
        "title": f"Chart {st.session_state.chart_counter + 1}",
        "type": "Scatter",
        "x": "x",
        "y": "y",
        "params": 2
    }
    return sample_graph


# Инициализация состояния
if "charts" not in st.session_state or "chart_counter" not in st.session_state:
    st.session_state.charts = []
    st.session_state.chart_counter = 0

# Демо-данные
df = pd.DataFrame({
    "x": range(10),
    "y": [i ** 2 for i in range(10)],
    "category": ["A", "B"] * 5
})


# Функция для отображения графика
def render_chart(chart_params):
    plt.figure(figsize=(5, 3))
    if chart_params["params"] == 1:
        # Рендеринг графиков с 1 параметром
        if chart_params["type"] == "Boxplot":
            sns.boxplot(data=df, x=chart_params["x"])
        elif chart_params["type"] == "Histogram":
            sns.histplot(data=df, x=chart_params["x"], kde=False)
        elif chart_params["type"] == "KDE":
            sns.kdeplot(data=df, x=chart_params["x"], fill=True)
    else:
        # Рендеринг графиков с 2 параметрами
        if chart_params["type"] == "Scatter":
            sns.scatterplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Line":
            sns.lineplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Bar":
            sns.barplot(data=df, x=chart_params["x"], y=chart_params["y"])
    st.pyplot(plt)


# Добавление первого графика, если список пуст
if not st.session_state.charts:
    if st.button("➕ Add First Chart"):
        st.session_state.charts.append(generate_sample_graph())
        st.session_state.chart_counter += 1

# Интерфейс блоков графиков
for i, chart in enumerate(st.session_state.charts):
    with st.container(border=True):

        # Заголовок графика (редактируемый)
        chart["title"] = st.text_input(f"Chart Title (ID: {chart['id']})", chart["title"], key=f"title_{i}")

        # Плейсхолдер для графика
        placeholder = st.empty()  # Пустой контейнер для графика (отрисовка будет позже)

        # Редактирование параметров
        with st.expander("Edit Chart Parameters"):
            # Choose the number of parameters
            chart["params"] = st.radio("Number of Parameters", [1, 2], index=[1, 2].index(chart["params"]),
                                       key=f"params_{i}")
            # Then choose the type of graph
            if chart["params"] == 1:
                try:
                    chart["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                 index=["Boxplot", "Histogram", "KDE"].index(chart["type"]),
                                                 key=f"type_1_{i}")
                except ValueError as err:
                    chart["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                 index=0,
                                                 key=f"type_1_{i}")

                # Then choose X-axis parameter
                chart["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(chart["x"]), key=f"x_{i}")
            else:
                try:
                    chart["type"] = st.selectbox("Chart Type (2 Param)", ["Scatter", "Line", "Bar"],
                                                 index=["Scatter", "Line", "Bar"].index(chart["type"]),
                                                 key=f"type_{i}")
                except ValueError as err:
                    chart["type"] = st.selectbox("Chart Type", ["Scatter", "Line", "Bar"],
                                                 index=0,
                                                 key=f"type_{i}")

                # Then choose X-axis parameter
                chart["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(chart["x"]), key=f"x_{i}")

                # And choose Y-axis parameter
                chart["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(chart["y"]), key=f"y_{i}")

        # Теперь, после редактирования, отрисовываем график в placeholder
        with placeholder:
            render_chart(chart)

        # Кнопки управления графиками
        col1, col2, col3, col4 = st.columns([1, 1, 6, 6])
        with col1:
            if st.button("⬆️", key=f"up_{i}") and i > 0:
                st.session_state.charts[i], st.session_state.charts[i - 1] = st.session_state.charts[i - 1], \
                    st.session_state.charts[i]
                st.rerun()
        with col2:
            if st.button("⬇️", key=f"down_{i}") and i < len(st.session_state.charts) - 1:
                st.session_state.charts[i], st.session_state.charts[i + 1] = st.session_state.charts[i + 1], \
                    st.session_state.charts[i]
                st.rerun()
        with col3:
            if st.button("❌ Delete Chart", key=f"delete_{i}"):
                st.session_state.charts.pop(i)
                st.rerun()
        with col4:
            if st.button("➕ Add Chart Below", key=f"add_{i}"):
                st.session_state.charts.insert(i + 1, generate_sample_graph())
                st.session_state.chart_counter += 1
                st.rerun()

st.write(st.session_state.charts)
