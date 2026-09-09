"""
control.py
-----------
Define la clase Controlador, que actúa como orquestador (patrón Facade/Controller)
del pipeline completo del screener de acciones.

En lugar de que app.py llame directamente a cada uno de los módulos del
"modelo" (Limpieza, BasicData, BasicFilter, AdvancedData, Calculations,
AdvancedFilter), el Controlador centraliza y simplifica esas llamadas,
exponiendo métodos de alto nivel que representan cada etapa del proceso.
"""


class Controlador:
    def __init__(self, limpieza_df, basic_data_df, basic_filter_df, advanced_data_df, calculations_df, advanced_filter_df):
        """
        Recibe una instancia de cada módulo del "modelo" (todas ellas ya
        apuntando al mismo df_class/DataFrame compartido) y las guarda como
        atributos para poder invocarlas desde los métodos de esta clase.

        Parámetros:
            limpieza_df (Limpieza): módulo de limpieza inicial del DataFrame.
            basic_data_df (BasicData): módulo de obtención de datos básicos (yfinance .info).
            basic_filter_df (BasicFilter): módulo de filtros básicos (sector, market cap).
            advanced_data_df (AdvancedData): módulo de obtención de datos financieros avanzados.
            calculations_df (Calculations): módulo de cálculo de métricas derivadas.
            advanced_filter_df (AdvancedFilter): módulo del filtro final de calidad/valor.
        """
        self.limpieza_df = limpieza_df
        self.basic_data_df = basic_data_df
        self.basic_filter_df = basic_filter_df
        self.advanced_data_df = advanced_data_df
        self.calculations_df = calculations_df
        self.advanced_filter_df = advanced_filter_df

    def hacer_limpieza(self, mantener_tipo, mantener_columnas, nuevos_ids):
        """
        Ejecuta la secuencia completa de limpieza inicial del DataFrame:
        filtra por tipo de instrumento, reduce las columnas, renombra los
        identificadores y da formato al ticker.
        """
        self.limpieza_df.filtrar_tipo(mantener_tipo)
        self.limpieza_df.filtrar_columnas(mantener_columnas)
        self.limpieza_df.cambiar_ids(nuevos_ids)
        self.limpieza_df.formateo()

    def save_basic_data(self):
        """
        Descarga y cachea en memoria los datos básicos (.info) de cada ticker
        desde yfinance, a través del módulo BasicData.
        """
        self.basic_data_df.obtener_basic_data()

    def proceso_basic_data(self, add_data):
        """
        Agrega al DataFrame las columnas de datos básicos indicadas en `add_data`,
        usando el caché ya descargado por save_basic_data().
        """
        self.basic_data_df.add_basic_data(add_data)

    def proceso_basic_filter(self, sectores):
        """
        Aplica el filtro básico por sector, dejando solo los sectores indicados.
        """
        self.basic_filter_df.aplicar_sector_filter(sectores)

    def proceso_marketcap_filter(self, min_market_cap, max_market_cap):
        """
        Aplica el filtro básico por capitalización de mercado, dejando solo las
        empresas dentro del rango [min_market_cap, max_market_cap].
        """
        self.basic_filter_df.aplicar_marketcap_filter(min_market_cap, max_market_cap)

    def proceso_advanced_data(self, save_name):
        """
        Descarga los datos financieros avanzados (estados financieros) de cada
        ticker restante y los agrega al DataFrame, guardando checkpoints
        periódicos en `save_name`.
        """
        self.advanced_data_df.obtener_advanced_data(save_name)

    def proceso_calculations(self):
        """
        Calcula las métricas financieras derivadas (ROIC, CAGR, reinversión, etc.)
        a partir de los datos avanzados ya obtenidos.
        """
        self.calculations_df.hacer_calculos()

    def proceso_advanced_filter(self):
        """
        Aplica el filtro final de calidad/valor sobre el DataFrame, usando las
        métricas calculadas en proceso_calculations().
        """
        self.advanced_filter_df.aplicar_filtro()
