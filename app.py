"""
app.py
------
Script principal (punto de entrada) del screener de acciones.

Flujo general del programa:
1. Se carga un archivo Excel con el listado de acciones ('stocks.xlsx').
2. Se limpia el DataFrame (tipo de instrumento, columnas, nombres de columnas, formato de ticker).
3. Se obtienen datos "básicos" desde Yahoo Finance (yfinance) por cada ticker (sector, industria, país, etc.).
4. Se aplican filtros básicos (sector, market cap).
5. Se obtienen datos "avanzados" (estados financieros: income statement, balance sheet, cashflow).
6. Se calculan métricas financieras derivadas (ROIC, CAGR de ingresos, reinversión, etc.).
7. Se aplica un filtro avanzado final según las métricas calculadas.
8. Se guarda el resultado final en un nuevo archivo Excel.

Cada paso intermedio se guarda en un archivo Excel independiente para poder
inspeccionar/depurar el proceso o retomar el análisis sin tener que rehacer
las llamadas a la API de Yahoo Finance (que son lentas y limitadas).
"""

# Importa el controlador (orquestador) y los distintos módulos del "modelo"
# que contienen la lógica de limpieza, obtención de datos y filtrado.
from controlador import control
from modelo import limpieza, dataframe, basic_data, basic_filter, advanced_data, calculations, advanced_filter

# --- Parámetros de entrada/salida ---
file = 'stocks.xlsx'          # Archivo Excel de origen con el listado de acciones
save_name = 'stocks_final.xlsx'  # Nombre del archivo Excel final con el resultado del screener

# --- Parámetros de limpieza inicial ---
mantener_tipo = ['EQUITY', 'ADR']              # Tipos de instrumento a conservar (se descartan ETFs, fondos, etc.)
mantener_columnas = ['Símbolo', 'Nombre']      # Columnas originales que se conservan del archivo de origen
nuevos_ids = {'Símbolo': 'ticker', 'Nombre': 'name'}  # Renombre de columnas a nombres internos estándar

# --- Grupos de columnas a obtener desde yfinance (Ticker.info) en distintas etapas ---
add_data_1 = ['sector', 'industry', 'country', 'financialCurrency']  # Datos descriptivos generales
add_data_2 = ['marketCap']                                           # Capitalización de mercado (para filtrar antes de traer más datos)
add_data_3 = [                                                       # Ratios/ indicadores adicionales una vez filtrado por tamaño
    'payoutRatio', 'trailingPE', 'forwardPE', 'priceToSalesTrailing12Months',
    'heldPercentInsiders', 'pegRatio', 'debtToEquity', 'returnOnEquity',
    'revenueGrowth', 'grossMargins'
]

# --- Parámetros de filtrado básico ---
sectores = [  # Sectores permitidos en el screener
    'Technology', 'Industrials', 'Consumer Cyclical', 'Healthcare',
    'Communication Services', 'Consumer Defensive'
]
min_market_cap = 100000000    # Capitalización mínima de mercado (100 millones)
max_market_cap = 1000000000   # Capitalización máxima de mercado (1.000 millones)

# --- Instanciación del contenedor de datos (DataFrame envuelto en una clase propia) ---
df_class = dataframe.DataFrame(file)  # Carga el Excel 'stocks.xlsx' en un DataFrame interno (df_class.df)

# --- Instanciación de cada módulo de procesamiento, todos apuntando al mismo df_class ---
# De esta forma, todos los módulos leen y modifican el mismo DataFrame subyacente.
limpieza_df = limpieza.Limpieza(df_class)
basic_data_df = basic_data.BasicData(df_class)
basic_filter_df = basic_filter.BasicFilter(df_class)
advanced_data_df = advanced_data.AdvancedData(df_class)
calculations_df = calculations.Calculations(df_class)
advanced_filter_df = advanced_filter.AdvancedFilter(df_class)

# --- Controlador: orquesta las llamadas a cada módulo en el orden correcto ---
control_screener = control.Controlador(
    limpieza_df, basic_data_df, basic_filter_df,
    advanced_data_df, calculations_df, advanced_filter_df
)

# 1) Limpieza inicial del DataFrame (filtra por tipo, columnas y renombra ids)
control_screener.hacer_limpieza(mantener_tipo, mantener_columnas, nuevos_ids)

# 2) Descarga los datos básicos (info) de cada ticker desde yfinance y los guarda en memoria
control_screener.save_basic_data()

# 3) Agrega al DataFrame las columnas del primer grupo de datos básicos (sector, industria, país, moneda)
control_screener.proceso_basic_data(add_data_1)
df_class.save_df('basic_data_1.xlsx')  # Checkpoint intermedio en disco

# 4) Filtra el DataFrame dejando solo los sectores de interés
control_screener.proceso_basic_filter(sectores)

# 5) Agrega la columna de market cap y guarda otro checkpoint
control_screener.proceso_basic_data(add_data_2)
df_class.save_df('basic_data_2.xlsx')

# 6) Filtra por rango de capitalización de mercado (reduce el universo antes de la parte más costosa)
control_screener.proceso_marketcap_filter(min_market_cap, max_market_cap)

# 7) Agrega el tercer grupo de datos (ratios financieros) y guarda otro checkpoint
control_screener.proceso_basic_data(add_data_3)
df_class.save_df('basic_data_3.xlsx')

# 8) Obtiene datos avanzados (estados financieros detallados) desde yfinance por cada ticker restante.
#    'save_name' se usa como checkpoint automático cada 100 tickers procesados (ver advanced_data.py).
control_screener.proceso_advanced_data(save_name)

# 9) Calcula las métricas financieras derivadas (CAGR, ROIC, reinversión, márgenes, etc.)
control_screener.proceso_calculations()
df_class.save_df('advanced_data.xlsx')  # Checkpoint con todos los datos y cálculos antes del filtro final

# 10) Aplica el filtro avanzado final según los criterios de calidad/valor definidos
control_screener.proceso_advanced_filter()

# Guarda el resultado final del screener en el archivo de salida
df_class.save_df(save_name)
