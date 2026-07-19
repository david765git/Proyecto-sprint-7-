import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página 
st.set_page_config(page_title="Dashboard de Vehiculos usados", layout="wide")

# 1. TÍTULO Y DESCRIPCIÓN PRINCIPAL
st.title("Panel Interactivo del Mercado de Vehiculos en EE.UU.")
st.write("Bienvenido a esta herramienta analitica avanzada diseñada para explorar y comprender las dinamicas de precios, condiciones y disponibilidad en el mercado automotriz.")
st.markdown("---")

# 2. carga y limpieza de datos 
@st.cache_data 
def load_and_clean_data():
    df = pd.read_csv("vehicles_us.csv")
    df.columns = df.columns.str.lower()
    
    # Relleno inteligente usando agrupaciones por modelo
    df['model_year'] = df.groupby('model')['model_year'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 2010)).astype(int)
    df['cylinders'] = df.groupby('model')['cylinders'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 6)).astype(int)
    df['odometer'] = df.groupby(['model_year', 'model'])['odometer'].transform(lambda x: x.fillna(x.median() if not x.isna().all() else df['odometer'].median())).astype(int)
    
    # Ajustes finales de formato
    df['is_4wd'] = df['is_4wd'].fillna(0).astype(int)
    df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
    
    # Extraer la marca del vehiculo (primera palabra del modelo)
    df['brand'] = df['model'].apply(lambda x: x.split()[0].title())
    return df

try:
    df = load_and_clean_data()
except Exception as e:
    st.error(f"Error al cargar el archivo de datos: {e}")
    st.stop()

# 3. filtros interactivos
st.sidebar.header("Filtros de Busqueda")

# filtro 1: selección de marcas (Multiselección)
brands = sorted(df['brand'].unique())
selected_brands = st.sidebar.multiselect("Selecciona las marcas a analizar:", options=brands, default=brands[:5])

# filtro 2: rango de precios (Slider dinámico)
min_price, max_price = int(df['price'].min()), int(df['price'].max())
selected_price_range = st.sidebar.slider("Rango de Precios ($):", min_value=min_price, max_value=max_price, value=(min_price, 50000))

# filtro 3: condición del vehiculo
conditions = df['condition'].unique()
selected_conditions = st.sidebar.multiselect("Condicion del auto:", options=conditions, default=conditions)

# aplicar filtros al data frame
df_filtered = df[
    (df['brand'].isin(selected_brands)) & 
    (df['price'].between(selected_price_range[0], selected_price_range[1])) &
    (df['condition'].isin(selected_conditions))
]

# 4. tarjetas de metricas claves
st.header("Indicadores Clave del Mercado (Metricas)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Anuncios Filtrados", f"{df_filtered.shape[0]:,}")
with col2:
    st.metric("Precio Promedio", f"${int(df_filtered['price'].mean()) if not df_filtered.empty else 0:,}")
with col3:
    st.metric("Kilometraje Promedio", f"{int(df_filtered['odometer'].mean()) if not df_filtered.empty else 0:,} mi")
with col4:
    st.metric("Año Promedio Modelo", f"{int(df_filtered['model_year'].mean()) if not df_filtered.empty else 0}")

st.markdown("---")

# 5. vista previa
st.header("Datos Seleccionados")
st.write("Utiliza la barra lateral para ajustar el conjunto de datos visualizado en esta tabla:")
st.dataframe(df_filtered.head(50), use_container_width=True)
st.markdown("---")

# 6. visualizacion dinamica
st.header("Graficos del Proyecto Integrados")
st.write("Activa las casillas para construir los graficos analiticos requeridos:")

# historigrama de precios
build_histogram = st.checkbox("Construir grafico: Distribucion de Precios")
if build_histogram:
    st.subheader("Analisis de Distribucion de Precios")
    fig1 = px.histogram(df_filtered, x="price", nbins=50, title="Distribucion de precios en el inventario seleccionado", color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig1, use_container_width=True)

# casilla para el gráfico de dispersión
build_scatter = st.checkbox("Construir grafico: Relacion Precio vs Kilometraje")
if build_scatter:
    st.subheader("Analisis de Depreciacion: Precio vs Kilometraje")
    fig2 = px.scatter(df_filtered, x="odometer", y="price", color="condition", 
                       title="Impacto del kilometraje en el precio de venta segun su condicion",
                       labels={"odometer": "Odometro (Millas)", "price": "Precio ($)"},
                       opacity=0.6)
    st.plotly_chart(fig2, use_container_width=True)

# casilla para gráficos adicionales agrupados
build_extra_charts = st.checkbox("Construir graficos: Comparativas de Combustible y Transmisiones")
if build_extra_charts:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Distribucion por tipo de transmision")
        fig3 = px.histogram(df_filtered, x="transmission", title="Volumen de anuncios por caja de cambios", color="transmission")
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_g2:
        st.subheader("Precio promedio por combustible")
        if not df_filtered.empty:
            avg_price = df_filtered.groupby("fuel")["price"].mean().reset_index()
            fig4 = px.bar(avg_price, x="fuel", y="price", title="Costo medio segun tipo de combustible", color="fuel")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.write("No hay datos para mostrar en la grafica de combustible.")