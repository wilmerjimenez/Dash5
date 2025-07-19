
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
import folium
import random
import os

# ------------------- Configuración inicial -------------------
st.set_page_config(page_title="Dashboard de Proyectos Climáticos", layout="wide")

# CSS para fondo degradado y estilos generales
st.markdown(
    '''
    <style>
    body, .stApp {
        background: radial-gradient(circle at top left, #101a36 0%, #070b16 100%);
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #d1d1d1;
    }
    .css-1v0mbdj p { color:white; }
    h1, h2, h3, h4, h5, h6 { color: white !important; }
    .block-container {
        padding: 1.5rem 1rem 2rem 1rem;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# -------------------- Cargar datos ---------------------------
@st.cache_data
def load_data():
    excel_file = '00_Planificacion_CambioClimatico_dashboard_2025jul19_4.xlsx'
    df = pd.read_excel(excel_file, engine='openpyxl')
    # Normalizar tipos
    date_cols = ['Fecha inicio','Fecha fin']
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    # Ubicación - separamos si hay varias ubicaciones
    df['Ubicación lista'] = df['Ubicación'].astype(str).str.split(',')
    return df

df = load_data()

# -------------------- Filtros -------------------------------
st.sidebar.header("🔍 Filtros")

# Proyecto principal
proyecto_default = df['Siglas proyecto'].dropna().unique()[0] if not df['Siglas proyecto'].dropna().empty else ''
proyecto_sel = st.sidebar.selectbox("Proyecto principal (Siglas proyecto)", df['Siglas proyecto'].dropna().unique(), index=0)

# Filtro de columnas dinámico
filter_cols = [
    'Entidad que lidera',
    'Financiamiento (entidad)',
    'Implementador',
    'Participacion de la UGCC-DRAA',
    'Fase'
]

filters = {}
for col in filter_cols:
    options = df[col].dropna().unique().tolist()
    selected = st.sidebar.multiselect(col, options, default=options)
    filters[col] = selected

# Filtrar dataframe
dff = df[df['Siglas proyecto'] == proyecto_sel].copy()
for col, sel in filters.items():
    if sel:
        dff = dff[dff[col].isin(sel)]

# ------------------ Layout ------------------------------
st.title(f"📊 Dashboard: {proyecto_sel}")
st.write("")

# Paleta neón
neon = ['#39FF14', '#00E5FF', '#FF00FF', '#FF6F00', '#FFFF00']

# --------------- Primera fila ---------------------------
col1, col2, col3 = st.columns([1.2,1,1.5])

# Donut 4 segmentos: avances y faltantes
with col1:
    st.subheader("Avance vs Faltante")
    if not dff.empty:
        avances = dff[['Porcentaje de avance global','Porcentaje faltante global',
                       'Porcentaje de avance individual','Porcentaje faltante individual']].mean().round(2)
        labels = ['Avance global','Faltante global','Avance individual','Faltante individual']
        donut_fig = px.pie(names=labels, values=avances.values,
                           hole=0.55, color_discrete_sequence=neon)
        donut_fig.update_traces(textinfo='percent', textposition='inside')
        donut_fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(donut_fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

# Mapa
with col2:
    st.subheader("Ubicación proyectos")
    # Inicializar mapa centrado en Ecuador aproximado
    m = folium.Map(location=[-1.52, -78.2], zoom_start=5, tiles="cartodb dark_matter")
    # Añadir marcadores
    for idx, row in dff.iterrows():
        for loc in row['Ubicación lista']:
            folium.CircleMarker(
                location=[0,0], # placeholder; update below
                radius=6,
                popup=f"{row['Siglas proyecto']} - {loc}",
                color=random.choice(neon),
                fill=True,
                fill_opacity=0.9
            ).add_to(m)
    st_folium(m, width=450, height=300)

# Tres gráficos de área apilada (placeholder): Beneficiarios, Superficie, CO2 evitado
with col3:
    st.subheader("Indicadores por fase")
    area_metrics = {
        'Beneficiarios (personas productoras)': 'Beneficiarios',
        'Superficie intervenida (ha)': 'Superficie (ha)',
        'CO2 eq evitado (t)': 'CO2 evitado (t)'
    }
    phases = dff['Fase'].astype(str).unique().tolist()
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    idx = 1
    for col_name, label in area_metrics.items():
        if col_name in dff.columns:
            df_area = dff.groupby('Fase')[col_name].sum().reset_index()
            fig.add_trace(
                go.Scatter(x=df_area['Fase'], y=df_area[col_name], mode='lines',
                           fill='tozeroy', name=label, line=dict(color=neon[idx%len(neon)])),
                row=idx, col=1
            )
        idx +=1
    fig.update_layout(height=450, margin=dict(t=10,b=10,l=10,r=10), showlegend=False,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ----------------- Segunda fila ----------------------------
col4, col5 = st.columns([1.4,1])

# Gráfico de barras apiladas horizontal: Monto requerido vs ejecutado
with col4:
    st.subheader("Financiamiento vs Superficie")
    if 'Monto requerido (USD)' in dff.columns and 'Monto ejecutado (USD)' in dff.columns:
        df_fin = dff[['Siglas proyecto','Monto requerido (USD)','Monto ejecutado (USD)','Superficie intervenida (ha)']]
        fig_fin = go.Figure()
        fig_fin.add_trace(go.Bar(y=df_fin['Siglas proyecto'],
                                 x=df_fin['Monto requerido (USD)'],
                                 name='Monto requerido',
                                 orientation='h',
                                 marker_color=neon[0]))
        fig_fin.add_trace(go.Bar(y=df_fin['Siglas proyecto'],
                                 x=df_fin['Monto ejecutado (USD)'],
                                 name='Monto ejecutado',
                                 orientation='h',
                                 marker_color=neon[3]))
        fig_fin.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'},
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              showlegend=False)
        st.plotly_chart(fig_fin, use_container_width=True)

# Anillos circulares de progreso
with col5:
    st.subheader("Progreso general")
    metrics = ['Porcentaje de avance global','Porcentaje faltante global',
               'Porcentaje de avance individual','Porcentaje faltante individual','Fase']
    progress_df = dff[metrics].mean().round(2)
    # Dibujar gauge semicircular
    value = progress_df['Porcentaje de avance global'] if 'Porcentaje de avance global' in progress_df else 0
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0,100], 'tickcolor':'white'},
               'bar': {'color': neon[1]},
               'bgcolor':'rgba(0,0,0,0)',
               'borderwidth':1,
               'steps':[
                   {'range':[0,50],'color':neon[3]},
                   {'range':[50,80],'color':neon[4]},
                   {'range':[80,100],'color':neon[0]}
               ]},
        number={'suffix':'%'}
    ))
    gauge_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=260, margin=dict(t=20,b=10,l=10,r=10))
    st.plotly_chart(gauge_fig, use_container_width=True)

# ----------------- Pie de página ----------------------------
st.markdown("---")
# Timeline minimalista
timeline_cols = ['Fecha inicio','Fecha fin']
if all(col in dff.columns for col in timeline_cols):
    timeline_df = dff[['Siglas proyecto','Fecha inicio','Fecha fin']].dropna()
    if not timeline_df.empty:
        import numpy as np
        import altair as alt
        timeline_df['Duración días'] = (timeline_df['Fecha fin'] - timeline_df['Fecha inicio']).dt.days
        timeline_df['Color'] = np.where(timeline_df.index % 2 == 0, '#FF6F00', '#00E5FF')
        timeline_chart = alt.Chart(timeline_df).mark_bar(size=6).encode(
            x='Fecha inicio:T',
            x2='Fecha fin:T',
            y=alt.Y('Siglas proyecto:N', sort='-x'),
            color=alt.Color('Color:N', scale=None)
        ).properties(height=200)
        st.altair_chart(timeline_chart, use_container_width=True)
