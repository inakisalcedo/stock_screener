"""
limpieza.py
-----------
Define la clase Limpieza, encargada de dejar el DataFrame original
(cargado desde el Excel de origen) en un formato estandarizado y listo
para ser enriquecido con datos de Yahoo Finance.

Se encarga de:
- Filtrar filas según el tipo de instrumento (ej. solo acciones y ADRs).
- Quedarse solo con las columnas relevantes.
- Renombrar columnas a nombres internos estándar (ej. 'ticker', 'name').
- Formatear el símbolo del ticker para que sea compatible con yfinance.
"""


class Limpieza:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): instancia del wrapper de DataFrame sobre
                                   la cual se realizarán las operaciones de limpieza.
        """
        self.df_class = df_class

    def filtrar_tipo(self, mantener_tipo):
        """
        Conserva únicamente las filas cuyo valor en la columna 'Tipo'
        esté incluido en la lista `mantener_tipo` (ej. ['EQUITY', 'ADR']),
        descartando otros tipos de instrumentos (ETFs, fondos, etc.).
        """
        self.df_class.df = self.df_class.df[self.df_class.df['Tipo'].isin(mantener_tipo)]

    def filtrar_columnas(self, mantener_columnas):
        """
        Reduce el DataFrame dejando únicamente las columnas indicadas
        en la lista `mantener_columnas` (ej. ['Símbolo', 'Nombre']).
        """
        self.df_class.df = self.df_class.df[mantener_columnas]

    def cambiar_ids(self, nuevos_ids):
        """
        Renombra columnas del DataFrame según el diccionario `nuevos_ids`,
        donde la clave es el nombre original y el valor es el nuevo nombre
        (ej. {'Símbolo': 'ticker', 'Nombre': 'name'}).
        """
        self.df_class.df = self.df_class.df.rename(columns=nuevos_ids)

    def formateo(self):
        """
        Da formato a la columna 'ticker' reemplazando los puntos ('.') por
        guiones ('-'), ya que yfinance utiliza guiones para representar
        clases de acciones (ej. 'BRK.B' -> 'BRK-B').
        """
        self.df_class.df['ticker'] = self.df_class.df['ticker'].str.replace('.', '-', regex=False)
