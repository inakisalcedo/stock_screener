# 📈 Stock Screener

Screener de acciones en Python que filtra un universo de acciones a partir de un archivo Excel de entrada, enriquece los datos con información de **Yahoo Finance** (vía [`yfinance`](https://pypi.org/project/yfinance/)) y aplica una serie de filtros progresivos (básicos y avanzados) hasta quedarse con un conjunto reducido de empresas que cumplen criterios de calidad, crecimiento y valoración.

## 🧠 ¿Qué hace este proyecto?

A partir de un listado inicial de acciones (`stocks.xlsx`), el pipeline:

1. **Limpia** el archivo original (tipo de instrumento, columnas relevantes, nombres estándar).
2. **Obtiene datos básicos** de cada ticker desde Yahoo Finance (sector, industria, país, market cap, ratios financieros).
3. **Filtra** por sector y por rango de capitalización de mercado.
4. **Obtiene datos avanzados** (estados financieros históricos: income statement, balance sheet, cashflow) para las empresas restantes.
5. **Calcula métricas financieras derivadas**: CAGR de ingresos, NOPAT, ROIC, tasa de reinversión, crecimiento esperado, márgenes, cobertura de intereses, entre otras.
6. **Aplica un filtro final** de calidad/valor sobre esas métricas.
7. **Exporta** el resultado final a un nuevo archivo Excel.

En cada etapa se generan checkpoints intermedios en Excel (`basic_data_1.xlsx`, `basic_data_2.xlsx`, `basic_data_3.xlsx`, `advanced_data.xlsx`) para poder auditar el proceso o retomarlo sin tener que repetir llamadas costosas a la API.

## 🗂️ Estructura del proyecto

```
.
├── app.py                     # Script principal (punto de entrada del pipeline)
├── controlador/
│   ├── __init__.py
│   └── control.py             # Orquestador: expone los pasos del pipeline de alto nivel
└── modelo/
    ├── __init__.py
    ├── dataframe.py            # Wrapper del DataFrame (carga/guarda Excel)
    ├── limpieza.py              # Limpieza y formateo inicial del DataFrame
    ├── basic_data.py            # Obtención de datos básicos (yfinance .info)
    ├── basic_filter.py          # Filtros por sector y market cap
    ├── advanced_data.py         # Obtención de estados financieros históricos
    ├── calculations.py          # Cálculo de métricas financieras derivadas
    └── advanced_filter.py       # Filtro final de calidad/valor
```

### Patrón de diseño

El proyecto sigue una arquitectura simple tipo **Controller / Model**:

- **`modelo/`**: cada clase encapsula una responsabilidad puntual (limpieza, obtención de datos, filtrado, cálculos) y todas comparten una misma instancia de `DataFrame` (`modelo/dataframe.py`) como estado central.
- **`controlador/control.py`**: expone métodos de alto nivel (`hacer_limpieza`, `proceso_basic_data`, `proceso_advanced_filter`, etc.) que orquestan las llamadas a los módulos del modelo, para que `app.py` quede simple y legible.

## ⚙️ Requisitos

- Python 3.9+
- Dependencias:

```bash
pip install pandas yfinance openpyxl numpy
```

## 🚀 Uso

1. Coloca un archivo `stocks.xlsx` en la raíz del proyecto, con al menos las columnas `Tipo`, `Símbolo` y `Nombre`.
2. Ajusta los parámetros en `app.py` según tus criterios (sectores, rango de market cap, columnas a obtener, etc.).
3. Ejecuta el script principal:

```bash
python app.py
```

4. Al finalizar, se generará el archivo `stocks_final.xlsx` con las empresas que superaron todos los filtros, además de los checkpoints intermedios.

## 🔍 Parámetros configurables (`app.py`)

| Parámetro | Descripción |
|---|---|
| `file` | Archivo Excel de entrada con el universo de acciones. |
| `save_name` | Nombre del archivo Excel de salida final. |
| `mantener_tipo` | Tipos de instrumento a conservar (ej. `EQUITY`, `ADR`). |
| `mantener_columnas` | Columnas originales a conservar del archivo de entrada. |
| `nuevos_ids` | Renombre de columnas a los nombres internos usados por el pipeline. |
| `add_data_1 / 2 / 3` | Campos de `yfinance.Ticker(ticker).info` a incorporar en cada etapa. |
| `sectores` | Sectores permitidos en el filtro básico. |
| `min_market_cap` / `max_market_cap` | Rango de capitalización de mercado permitido. |

## 📊 Métricas calculadas

| Métrica | Descripción |
|---|---|
| `revenue_cagr` | Tasa de crecimiento anual compuesta de los ingresos. |
| `nopat` | Utilidad operativa neta después de impuestos. |
| `reinvestment_rate` | Proporción de la reinversión respecto al NOPAT. |
| `roic` | Retorno sobre el capital invertido. |
| `expected_growth` | Crecimiento esperado (ROIC × tasa de reinversión). |
| `fcf_margin` / `ebit_margin` | Márgenes de flujo de caja libre y EBIT sobre ingresos. |
| `interest_coverage` | Capacidad de la empresa para cubrir sus gastos por intereses con el EBIT. |

## ✅ Criterios del filtro final (`advanced_filter.py`)

Una empresa pasa el filtro final si cumple, entre otros:

- Ingresos positivos y creciendo a un CAGR ≥ 15%.
- Margen bruto > 20%.
- Deuda/Patrimonio ≤ 150%.
- Cobertura de intereses ≥ 5x (o EBIT negativo, en cuyo caso el criterio no aplica).
- Participación de insiders ≥ 5%.
- ROIC ≥ 10%, tasa de reinversión positiva y crecimiento esperado ≥ 10% (criterios que solo aplican si la empresa tiene NOPAT positivo).

## ⚠️ Notas y limitaciones

- El proceso depende fuertemente de la disponibilidad y estabilidad de la API no oficial de `yfinance`, por lo que puede fallar o demorar según el volumen de tickers.
- Los checkpoints periódicos en `advanced_data.py` ayudan a mitigar pérdidas de progreso ante caídas del proceso, pero no implementan reintentos automáticos.
- Los valores financieros se convierten a una moneda de referencia usando el tipo de cambio *spot* más reciente (`previousClose`), lo que introduce una aproximación respecto al tipo de cambio vigente en cada período histórico reportado.
