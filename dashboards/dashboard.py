import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
#   CONFIGURACIÓN INICIAL
# ----------------------------------------------------
st.set_page_config(
    page_title="National Health Expenditures Dashboard",
    layout="wide"
)

st.title("National Health Expenditures (1960 – 2023)")
st.markdown("Exploración jerárquica y tendencias históricas del gasto nacional en salud.")

# ----------------------------------------------------
#   CARGA DEL DATAFRAME
# ----------------------------------------------------
# Asumiendo que ya tienes df_transformado del código anterior
# df_transformado = transform_to_hierarchy(df_intento)

# Si necesitas cargarlo desde archivo:
df_transformado = pd.read_csv("../data/datos_jerarquicos.csv")  # Ajusta la ruta

# Asegurarnos que Value sea numérico y Year sea entero
df_transformado['Value'] = pd.to_numeric(df_transformado['Value'], errors='coerce')
df_transformado['Year'] = pd.to_numeric(df_transformado['Year'], errors='coerce').astype(int)

# Eliminar filas con valores nulos
df_transformado = df_transformado.dropna(subset=['Value', 'Year'])

# ----------------------------------------------------
#   PANEL LATERAL: FILTROS SEGÚN LA JERARQUÍA
# ----------------------------------------------------
st.sidebar.header("Filtros")

# Nivel 1 - Category (fija)
selected_category = "Total National Health Expenditures"
st.sidebar.info(f" **Categoría:** {selected_category}")

# Filtrar por categoría seleccionada
df_filtered_cat = df_transformado[df_transformado["Category"] == selected_category]

# Nivel 2 - Subcategory 1
subcategories_1 = sorted(df_filtered_cat["Subcategory 1"].unique())
subcategories_1 = [s for s in subcategories_1 if s != "none"]
selected_subcat1 = st.sidebar.selectbox(
    "Subcategoría 1:", 
    ["(Todas)"] + subcategories_1
)

# Aplicar filtro de subcategoría 1
if selected_subcat1 != "(Todas)":
    df_filtered_cat = df_filtered_cat[df_filtered_cat["Subcategory 1"] == selected_subcat1]

# Nivel 3 - Subcategory 2
subcategories_2 = sorted(df_filtered_cat["Subcategory 2"].unique())
subcategories_2 = [s for s in subcategories_2 if s != "none"]
selected_subcat2 = st.sidebar.selectbox(
    "Subcategoría 2:", 
    ["(Todas)"] + subcategories_2
)

# Aplicar filtro de subcategoría 2
if selected_subcat2 != "(Todas)":
    df_filtered_cat = df_filtered_cat[df_filtered_cat["Subcategory 2"] == selected_subcat2]

# Nivel 4 - Subcategory 3
subcategories_3 = sorted(df_filtered_cat["Subcategory 3"].unique())
subcategories_3 = [s for s in subcategories_3 if s != "none"]
if subcategories_3:
    selected_subcat3 = st.sidebar.selectbox(
        "Subcategoría 3:", 
        ["(Todas)"] + subcategories_3
    )
    
    # Aplicar filtro de subcategoría 3
    if selected_subcat3 != "(Todas)":
        df_filtered_cat = df_filtered_cat[df_filtered_cat["Subcategory 3"] == selected_subcat3]

# Filtro de rango de años
st.sidebar.markdown("---")
year_min = int(df_transformado["Year"].min())
year_max = int(df_transformado["Year"].max())
year_range = st.sidebar.slider(
    "Rango de Años:",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

# Aplicar filtro de años
df_filtered = df_filtered_cat[
    (df_filtered_cat["Year"] >= year_range[0]) & 
    (df_filtered_cat["Year"] <= year_range[1])
]

# ----------------------------------------------------
#   MÉTRICAS CLAVE
# ----------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

if not df_filtered.empty:
    total_expenditure = df_filtered["Value"].sum()
    avg_expenditure = df_filtered["Value"].mean()
    first_year_value = df_filtered[df_filtered["Year"] == df_filtered["Year"].min()]["Value"].sum()
    last_year_value = df_filtered[df_filtered["Year"] == df_filtered["Year"].max()]["Value"].sum()
    
    if first_year_value > 0:
        growth_pct = ((last_year_value - first_year_value) / first_year_value) * 100
    else:
        growth_pct = 0
    
    with col1:
        st.metric("Gasto Total (período)", f"${total_expenditure:,.0f}M")
    
    with col2:
        st.metric("Promedio Anual", f"${avg_expenditure:,.0f}M")
    
    with col3:
        st.metric("Último Año", f"${last_year_value:,.0f}M")
    
    with col4:
        st.metric("Crecimiento", f"{growth_pct:,.1f}%")

st.markdown("---")

# ----------------------------------------------------
#   GRÁFICO PRINCIPAL: TENDENCIA TEMPORAL
# ----------------------------------------------------
st.subheader("Tendencia Temporal del Gasto")

if not df_filtered.empty:
    # Agrupar por año para el gráfico principal
    df_by_year = df_filtered.groupby("Year")["Value"].sum().reset_index()
    
    fig = px.line(
        df_by_year,
        x="Year",
        y="Value",
        markers=True,
        title=f"Tendencia del Gasto: {selected_category}" + 
              (f" > {selected_subcat1}" if selected_subcat1 != "(Todas)" else "")
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Gasto (Millones USD)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos disponibles para la selección actual.")

# ----------------------------------------------------
#   GRÁFICO DE COMPARACIÓN POR SUBCATEGORÍAS
# ----------------------------------------------------
st.subheader("Comparación por Subcategorías")

col_a, col_b = st.columns(2)

with col_a:
    if selected_subcat1 == "(Todas)" and not df_filtered.empty:
        # Mostrar comparación de Subcategoría 1
        df_comparison = df_filtered.groupby(["Year", "Subcategory 1"])["Value"].sum().reset_index()
        df_comparison = df_comparison[df_comparison["Subcategory 1"] != "none"]
        
        fig2 = px.line(
            df_comparison,
            x="Year",
            y="Value",
            color="Subcategory 1",
            title="Comparación por Subcategoría 1"
        )
        fig2.update_layout(xaxis_title="Año", yaxis_title="Gasto (Millones USD)")
        st.plotly_chart(fig2, use_container_width=True)

with col_b:
    if selected_subcat2 == "(Todas)" and selected_subcat1 != "(Todas)" and not df_filtered.empty:
        # Mostrar comparación de Subcategoría 2
        df_comparison2 = df_filtered.groupby(["Year", "Subcategory 2"])["Value"].sum().reset_index()
        df_comparison2 = df_comparison2[df_comparison2["Subcategory 2"] != "none"]
        
        if not df_comparison2.empty:
            fig3 = px.line(
                df_comparison2,
                x="Year",
                y="Value",
                color="Subcategory 2",
                title="Comparación por Subcategoría 2"
            )
            fig3.update_layout(xaxis_title="Año", yaxis_title="Gasto (Millones USD)")
            st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------
#   GRÁFICO DE DISTRIBUCIÓN (PIE CHART)
# ----------------------------------------------------
st.subheader("Distribución del Gasto (Último Año)")

if not df_filtered.empty:
    last_year_data = df_filtered[df_filtered["Year"] == df_filtered["Year"].max()]
    
    # Elegir qué nivel mostrar basado en los filtros
    if selected_subcat1 == "(Todas)":
        group_col = "Subcategory 1"
    elif selected_subcat2 == "(Todas)":
        group_col = "Subcategory 2"
    elif subcategories_3 and selected_subcat3 == "(Todas)":
        group_col = "Subcategory 3"
    else:
        group_col = None
    
    if group_col:
        pie_data = last_year_data.groupby(group_col)["Value"].sum().reset_index()
        pie_data = pie_data[pie_data[group_col] != "none"]
        
        if not pie_data.empty:
            fig4 = px.pie(
                pie_data,
                values="Value",
                names=group_col,
                title=f"Distribución en {df_filtered['Year'].max()}"
            )
            st.plotly_chart(fig4, use_container_width=True)

# ----------------------------------------------------
#   TABLA DE DATOS FILTRADOS
# ----------------------------------------------------
st.subheader("Tabla de Datos Detallados")

# Mostrar tabla con formato
df_display = df_filtered.copy()
df_display['Value'] = df_display['Value'].apply(lambda x: f"${x:,.2f}M")
st.dataframe(df_display, use_container_width=True, height=400)

# Opción de descarga
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Descargar datos filtrados (CSV)",
    data=csv,
    file_name="health_expenditures_filtered.csv",
    mime="text/csv"
)

# ----------------------------------------------------
#   INTERPRETACIÓN AUTOMÁTICA
# ----------------------------------------------------
st.subheader("Análisis Automático")

if not df_filtered.empty:
    df_analysis = df_filtered.groupby("Year")["Value"].sum().reset_index()
    
    first_year = df_analysis["Year"].min()
    last_year = df_analysis["Year"].max()
    first_value = df_analysis[df_analysis["Year"] == first_year]["Value"].values[0]
    last_value = df_analysis[df_analysis["Year"] == last_year]["Value"].values[0]
    
    if first_value > 0:
        growth = ((last_value - first_value) / first_value) * 100
        
        trend_text = f"""
        ### Resumen de la Tendencia
        
        Entre **{first_year}** y **{last_year}**, el gasto en la categoría seleccionada 
        pasó de **${first_value:,.0f} millones** a **${last_value:,.0f} millones**, 
        lo que representa un aumento de **{growth:.1f}%**.
        
        **Insights clave:**
        - Categoría analizada: **{selected_category}**
        {f"- Subcategoría 1: **{selected_subcat1}**" if selected_subcat1 != "(Todas)" else ""}
        {f"- Subcategoría 2: **{selected_subcat2}**" if selected_subcat2 != "(Todas)" else ""}
        - Período de análisis: **{last_year - first_year} años**
        - Tasa de crecimiento promedio anual: **{(growth / (last_year - first_year)):.2f}%**
        
        Esta tendencia refleja los cambios en las políticas de salud, demografía 
        y costos de servicios médicos a lo largo del tiempo.
        """
        
        st.markdown(trend_text)