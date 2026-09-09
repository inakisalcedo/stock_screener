"""
advanced_filter.py
--------------------
Define la clase AdvancedFilter, encargada de aplicar el filtro final del
screener utilizando las métricas financieras calculadas en calculations.py
(ROIC, CAGR de ingresos, cobertura de intereses, tasa de reinversión, etc.).

El objetivo de este filtro es quedarse solo con empresas que muestren:
- Ingresos positivos y en crecimiento.
- Márgenes brutos saludables.
- Endeudamiento controlado y buena capacidad de pago de intereses.
- Suficiente participación de los insiders (accionistas internos).
- Buena rentabilidad sobre el capital invertido y reinversión eficiente,
  siempre que la empresa efectivamente genere utilidades operativas
  positivas (nopat > 0); en caso contrario, esos criterios se omiten
  (se dejan pasar) para no descartar injustamente empresas sin NOPAT positivo
  con reglas que no aplican en ese caso.
"""


class AdvancedFilter:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): wrapper del DataFrame principal sobre el que
                                   se aplicará el filtro final.
        """
        self.df_class = df_class

    def aplicar_filtro(self):
        """
        Aplica de forma secuencial los siguientes criterios de filtrado
        (cada uno reduce progresivamente el DataFrame, ya que se van
        encadenando condiciones sobre el resultado del filtro anterior):

        1. total_revenue_last > 0        -> la empresa debe tener ingresos positivos.
        2. grossMargins > 0.2            -> margen bruto superior al 20%.
        3. revenue_cagr >= 0.15          -> crecimiento de ingresos de al menos 15% anual.
        4. debtToEquity <= 150           -> ratio deuda/patrimonio no mayor a 150%.
        5. interest_coverage >= 5 OR ebit <= 0
           -> buena cobertura de intereses, salvo que la empresa no tenga
              utilidad operativa positiva (en cuyo caso este criterio no aplica).
        6. heldPercentInsiders >= 0.05   -> al menos 5% de participación de insiders.
        7. roic >= 0.1 OR nopat <= 0
           -> retorno sobre capital invertido de al menos 10%, salvo que la
              empresa no tenga NOPAT positivo (criterio no aplica en ese caso).
        8. reinvestment_rate > 0 OR nopat <= 0
           -> la empresa debe estar reinvirtiendo (tasa de reinversión positiva),
              salvo que no tenga NOPAT positivo (criterio no aplica en ese caso).
        9. expected_growth >= 0.1 OR nopat <= 0
           -> crecimiento esperado de al menos 10%, salvo que no tenga
              NOPAT positivo (criterio no aplica en ese caso).
        """
        self.df_class.df = self.df_class.df[self.df_class.df['total_revenue_last'] > 0]
        self.df_class.df = self.df_class.df[self.df_class.df['grossMargins'] > 0.2]
        self.df_class.df = self.df_class.df[self.df_class.df['revenue_cagr'] >= 0.15]
        self.df_class.df = self.df_class.df[self.df_class.df['debtToEquity'] <= 150]
        self.df_class.df = self.df_class.df[(self.df_class.df['interest_coverage'] >= 5) | (self.df_class.df['ebit'] <= 0)]
        self.df_class.df = self.df_class.df[self.df_class.df['heldPercentInsiders'] >= 0.05]
        self.df_class.df = self.df_class.df[(self.df_class.df['roic'] >= 0.1) | (self.df_class.df['nopat'] <= 0)]
        self.df_class.df = self.df_class.df[(self.df_class.df['reinvestment_rate'] > 0) | (self.df_class.df['nopat'] <= 0)]
        self.df_class.df = self.df_class.df[(self.df_class.df['expected_growth'] >= 0.1) | (self.df_class.df['nopat'] <= 0)]
