"""
basic_filter.py
----------------
Define la clase BasicFilter, encargada de aplicar filtros "básicos" sobre
el DataFrame principal, usando columnas que ya fueron incorporadas previamente
mediante BasicData (por ejemplo 'sector' y 'marketCap').
"""


class BasicFilter:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): wrapper del DataFrame principal sobre el que
                                   se aplicarán los filtros.
        """
        self.df_class = df_class

    def aplicar_sector_filter(self, sectores):
        """
        Conserva únicamente las filas cuyo valor en la columna 'sector'
        esté incluido en la lista `sectores` recibida.
        """
        self.df_class.df = self.df_class.df[self.df_class.df['sector'].isin(sectores)]

    def aplicar_marketcap_filter(self, min_market_cap, max_market_cap):
        """
        Conserva únicamente las filas cuya capitalización de mercado ('marketCap')
        se encuentre dentro del rango [min_market_cap, max_market_cap], ambos
        límites inclusive.
        """
        self.df_class.df = self.df_class.df[
            (self.df_class.df['marketCap'] >= min_market_cap) &
            (self.df_class.df['marketCap'] <= max_market_cap)
        ]
