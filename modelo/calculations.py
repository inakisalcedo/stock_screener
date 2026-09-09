"""
calculations.py
-----------------
Define la clase Calculations, encargada de calcular métricas financieras
derivadas a partir de los datos "avanzados" obtenidos en advanced_data.py
(estados financieros) y de algunos datos "básicos" (grossMargins, etc.).

Las métricas calculadas aquí (ROIC, reinversión, crecimiento esperado, etc.)
siguen un enfoque similar al utilizado en valoración de empresas al estilo
Damodaran, y luego son usadas por AdvancedFilter para el filtro final del screener.
"""

import numpy as np


class Calculations:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): wrapper del DataFrame principal sobre el que
                                   se calcularán y agregarán las nuevas columnas.
        """
        self.df_class = df_class

    def hacer_calculos(self):
        """
        Calcula y agrega al DataFrame las siguientes columnas derivadas:

        - revenue_cagr: tasa de crecimiento anual compuesta (CAGR) de los ingresos,
          calculada entre el ingreso más antiguo (total_revenue_first) y el más
          reciente (total_revenue_last), usando la cantidad de años disponibles
          (revenue_years).
        - nopat: utilidad operativa neta después de impuestos (EBIT * (1 - tasa impositiva)).
        - operating_working_capital_1 / _2: capital de trabajo operativo del
          período actual y del período anterior, respectivamente
          (cuentas por cobrar + inventario + otros activos corrientes
           - cuentas por pagar - otros pasivos corrientes).
        - var_operating_working_capital: variación del capital de trabajo
          operativo entre ambos períodos.
        - net_capex: capex neto (gasto de capital menos depreciación y amortización).
        - reinvestment: reinversión total de la empresa (capex neto + variación
          de capital de trabajo).
        - reinvestment_rate: tasa de reinversión (reinversión / NOPAT).
        - roic: retorno sobre el capital invertido (NOPAT / capital invertido).
        - expected_growth: crecimiento esperado, aproximado como
          ROIC * tasa de reinversión.
        - fcf_margin: margen de flujo de caja libre sobre los ingresos.
        - ebit_margin: margen EBIT sobre los ingresos.
        - fcf_nopat: relación entre flujo de caja libre y NOPAT.
        - interest_coverage: cobertura de intereses (EBIT / gasto por intereses).
          Si el gasto por intereses es 0 o negativo, se asigna infinito (np.inf),
          ya que no existe carga de intereses que cubrir.
        """
        # CAGR de ingresos entre el período más antiguo y el más reciente disponibles
        self.df_class.df['revenue_cagr'] = (
            (self.df_class.df['total_revenue_last'] / self.df_class.df['total_revenue_first'])
            ** (1 / (self.df_class.df['revenue_years'] - 1))
        ) - 1

        # Utilidad operativa neta después de impuestos
        self.df_class.df['nopat'] = self.df_class.df['ebit'] * (1 - self.df_class.df['tax_rate'])

        # Capital de trabajo operativo del período actual (1) y del anterior (2)
        self.df_class.df['operating_working_capital_1'] = (
            (self.df_class.df['accounts_receivable_1'] + self.df_class.df['inventory_1'] + self.df_class.df['other_current_assets_1'])
            - (self.df_class.df['accounts_payable_1'] + self.df_class.df['other_current_liabilities_1'])
        )
        self.df_class.df['operating_working_capital_2'] = (
            (self.df_class.df['accounts_receivable_2'] + self.df_class.df['inventory_2'] + self.df_class.df['other_current_assets_2'])
            - (self.df_class.df['accounts_payable_2'] + self.df_class.df['other_current_liabilities_2'])
        )

        # Variación del capital de trabajo operativo entre ambos períodos
        self.df_class.df['var_operating_working_capital'] = (
            self.df_class.df['operating_working_capital_1'] - self.df_class.df['operating_working_capital_2']
        )

        # Capex neto: gasto de capital menos depreciación y amortización
        self.df_class.df['net_capex'] = self.df_class.df['capital_expenditure'] - self.df_class.df['depreciation_and_amortization']

        # Reinversión total: capex neto + variación de capital de trabajo operativo
        self.df_class.df['reinvestment'] = self.df_class.df['net_capex'] + self.df_class.df['var_operating_working_capital']

        # Tasa de reinversión respecto al NOPAT
        self.df_class.df['reinvestment_rate'] = self.df_class.df['reinvestment'] / self.df_class.df['nopat']

        # Retorno sobre el capital invertido (ROIC)
        self.df_class.df['roic'] = self.df_class.df['nopat'] / self.df_class.df['invested_capital']

        # Crecimiento esperado, aproximado como ROIC * tasa de reinversión
        self.df_class.df['expected_growth'] = self.df_class.df['roic'] * self.df_class.df['reinvestment_rate']

        # Margen de flujo de caja libre sobre ingresos
        self.df_class.df['fcf_margin'] = self.df_class.df['free_cash_flow'] / self.df_class.df['total_revenue_last']

        # Margen EBIT sobre ingresos
        self.df_class.df['ebit_margin'] = self.df_class.df['ebit'] / self.df_class.df['total_revenue_last']

        # Relación entre flujo de caja libre y NOPAT (calidad de las utilidades)
        self.df_class.df['fcf_nopat'] = self.df_class.df['free_cash_flow'] / self.df_class.df['nopat']

        # Cobertura de intereses: EBIT / gasto por intereses.
        # Si el gasto por intereses no es positivo, se asigna infinito (no hay carga de deuda que cubrir).
        self.df_class.df['interest_coverage'] = np.where(
            self.df_class.df['interest_expense'] > 0,
            self.df_class.df['ebit'] / self.df_class.df['interest_expense'],
            np.inf
        )
