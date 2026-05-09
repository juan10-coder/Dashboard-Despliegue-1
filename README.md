# Dashboard Ejecutivo de Ventas

Aplicación interactiva desarrollada en Streamlit para análisis de ventas comerciales con enfoque en inteligencia de negocios.

## Descripción

Este dashboard permite explorar indicadores comerciales mediante visualizaciones interactivas, métricas ejecutivas y filtros dinámicos para apoyar la toma de decisiones basada en datos.

## Funcionalidades

- Visualización interactiva de ventas
- KPIs comerciales
- Filtros por país, año, estado y línea de producto
- Análisis temporal de ventas
- Comparación de mercados
- Top clientes
- Distribución por territorio
- Heatmap de comportamiento mensual
- Tabla detallada con datos filtrados
- Insights automáticos

## Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Altair

## Estructura del proyecto

```text
dashboard-streamlit/
│
├── dashboard.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── sales_data_sample.csv
```

## Ejecución local

1. Crear entorno virtual:

```bash
python -m venv .venv
```

2. Activar entorno:

Windows:

```bash
.\.venv\Scripts\Activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar aplicación:

```bash
streamlit run dashboard.py
```

## Dataset

El proyecto utiliza el dataset `sales_data_sample.csv`, con información comercial como:

- órdenes
- ventas
- clientes
- países
- territorios
- líneas de producto
- estados de pedidos

## Despliegue

Aplicación desplegada mediante Streamlit Community Cloud conectada a GitHub.

## Autor

Juan Henao
Maestría en Analítica Aplicada