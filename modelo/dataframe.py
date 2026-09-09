"""
dataframe.py
------------
Define la clase DataFrame, que actúa como un contenedor/envoltorio (wrapper)
alrededor de un pandas.DataFrame.

Esta clase es el "estado compartido" del pipeline: todos los demás módulos
(Limpieza, BasicData, BasicFilter, AdvancedData, Calculations, AdvancedFilter)
reciben una instancia de esta clase y leen/modifican su atributo `df`.
Esto permite que múltiples módulos trabajen sobre el mismo DataFrame sin
tener que pasarlo explícitamente entre funciones.
"""

import pandas as pd


class DataFrame:
    def __init__(self, name):
        """
        Carga un archivo Excel y lo almacena como un DataFrame de pandas.

        Parámetros:
            name (str): ruta o nombre del archivo Excel a cargar (ej. 'stocks.xlsx').
        """
        self.df = pd.read_excel(name)

    def save_df(self, save_name):
        """
        Guarda el DataFrame actual en un archivo Excel.

        Parámetros:
            save_name (str): nombre/ruta del archivo Excel de salida.
                              No se incluye el índice del DataFrame (index=False).
        """
        self.df.to_excel(save_name, index=False)
