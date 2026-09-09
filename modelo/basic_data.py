"""
basic_data.py
-------------
Define la clase BasicData, encargada de obtener información "básica" de cada
ticker desde Yahoo Finance (a través de yfinance.Ticker(ticker).info) y de
incorporar columnas específicas de esa información al DataFrame principal.

El proceso está dividido en dos pasos independientes para evitar tener que
volver a llamar a la API cada vez que se quiere agregar una nueva columna:
1. obtener_basic_data(): descarga y cachea en memoria (self.b_data) el
   diccionario `.info` completo de cada ticker.
2. add_basic_data(add_data): a partir de ese caché, agrega al DataFrame
   solo las columnas solicitadas en `add_data`.
"""

import yfinance as yf


class BasicData:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): wrapper del DataFrame principal sobre el que
                                   se agregarán las columnas de datos básicos.
        """
        self.df_class = df_class
        # Caché en memoria: ticker -> diccionario completo devuelto por yfinance (.info)
        self.b_data = {}

    def obtener_basic_data(self):
        """
        Recorre todos los tickers únicos (no nulos) del DataFrame y descarga
        su información básica desde yfinance, almacenándola en self.b_data.

        Si la descarga de un ticker falla (ej. ticker inválido o error de red),
        el error se ignora silenciosamente y se continúa con el siguiente ticker
        (ese ticker simplemente no quedará en self.b_data).
        """
        for ticker in self.df_class.df['ticker'].dropna().unique():
            print(ticker)  # Log simple de progreso en consola
            try:
                self.b_data[ticker] = yf.Ticker(ticker).info
            except:
                pass

    def add_basic_data(self, add_data):
        """
        Agrega al DataFrame una columna por cada campo indicado en `add_data`,
        tomando el valor correspondiente desde el caché self.b_data según el ticker.

        Parámetros:
            add_data (list[str]): lista de nombres de campos a extraer del
                                   diccionario `.info` de cada ticker
                                   (ej. ['sector', 'industry', 'marketCap']).

        Si un ticker no está en el caché (self.b_data) o no tiene el campo
        solicitado, el valor resultante será None (comportamiento de dict.get).
        """
        for columna in add_data:
            self.df_class.df[columna] = self.df_class.df['ticker'].map(
                lambda ticker: self.b_data.get(ticker, {}).get(columna)
            )
