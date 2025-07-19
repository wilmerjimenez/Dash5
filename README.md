
# Dashboard de Proyectos Climáticos

Este repositorio contiene una aplicación **Streamlit** que genera un dashboard dinámico y de alta resolución inspirado en el mock‑up solicitado.

## Estructura

```
.
├── app.py
├── requirements.txt
├── 00_Planificacion_CambioClimatico_dashboard_2025jul19_4.xlsx
└── README.md
```

### app.py
* Carga y filtra el archivo `.xlsx` con **pandas**.
* Implementa filtros en la barra lateral para cada columna relevante.
* Genera gráficos con **Plotly**, **Altair** y un mapa **Folium**, todos con paleta neón y fondo degradado.

### requirements.txt
Lista de dependencias necesarias. Streamlit Cloud instala estas librerías automáticamente en el despliegue.

## Uso local

```bash
# Clona el repo y entra
git clone <tu‑repo> && cd <tu‑repo>

# (Opcional) crea un entorno virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt

# Ejecuta la app
streamlit run app.py
```

La interfaz se abre en tu navegador (`http://localhost:8501`).

## Despliegue gratuito en Streamlit Community Cloud

1. Sube este repositorio a GitHub.  
2. Entra a **[Streamlit Community Cloud](https://streamlit.io/cloud)** y pulsa **“New app”**.  
3. Elige tu repositorio y la rama principal, y apunta a `app.py`.  
4. Pulsa **Deploy** → en pocos minutos obtendrás la URL pública de tu dashboard.

## Personalización

* Para ajustar la paleta de colores, edita la lista `neon` en `app.py`.  
* Para añadir/quitar filtros, modifica la lista `filter_cols`.  
* Para cambiar la métrica principal del donut o el gauge, ajusta la sección “Avance vs Faltante” y “Progreso general”.

---
¡Disfruta visualizando tus proyectos climáticos! 🌱
