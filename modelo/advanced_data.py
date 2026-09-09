"""
advanced_data.py
-----------------
Define la clase AdvancedData, encargada de obtener datos financieros
"avanzados" (estados financieros: income statement, balance sheet,
balance sheet trimestral y cashflow) para cada ticker desde yfinance,
convertirlos a una moneda común de referencia y agregarlos como nuevas
columnas al DataFrame principal.

A diferencia de BasicData (que usa el diccionario `.info`), aquí se accede
a los reportes financieros históricos (`income_stmt`, `balance_sheet`,
`quarterly_balance_sheet`, `cashflow`), que son DataFrames de pandas con
las distintas partidas contables como filas y los períodos como columnas.

Todas las conversiones monetarias se hacen dividiendo por `valor_moneda`,
que representa el tipo de cambio (previousClose) de la moneda financiera
de cada empresa (`financialCurrency`) respecto a la moneda de referencia
usada en el ticker de FX (ej. 'USD=X').
"""

import yfinance as yf


class AdvancedData:
    def __init__(self, df_class):
        """
        Parámetros:
            df_class (DataFrame): wrapper del DataFrame principal sobre el que
                                   se agregarán las columnas de datos avanzados.
        """
        self.df_class = df_class

    def obtener_advanced_data(self, save_name):
        """
        Recorre cada ticker del DataFrame, descarga sus estados financieros
        desde yfinance, extrae las partidas contables relevantes (convertidas
        a la moneda de referencia) y las escribe como nuevas columnas en el
        DataFrame, fila por fila.

        Parámetros:
            save_name (str): nombre de archivo usado para guardar checkpoints
                              parciales del DataFrame cada 100 tickers procesados,
                              de forma de no perder el trabajo avanzado si el
                              proceso se interrumpe (dado que puede tardar mucho
                              por la cantidad de llamadas a la API).
        """
        # --- Paso 1: obtener el tipo de cambio de cada moneda financiera presente ---
        # Se arma un diccionario moneda -> valor de cierre previo del par MONEDA=X
        # (ej. 'USD=X', 'EUR=X'), que se usará para convertir todas las cifras
        # financieras a una base comparable.
        valores_monedas = {}
        for moneda in self.df_class.df['financialCurrency'].unique().tolist():
            valores_monedas[moneda] = yf.Ticker(f'{moneda}=X').info.get('previousClose')

        i = 0
        # --- Paso 2: recorrer cada ticker único (no nulo) del DataFrame ---
        for ticker in self.df_class.df['ticker'].dropna().unique():
            # Checkpoint: cada 100 tickers procesados se guarda el progreso en disco
            if (i % 100) == 0:
                self.df_class.save_df(save_name)
            print(ticker)  # Log simple de progreso en consola
            try:
                i += 1
                # Tipo de cambio correspondiente a la moneda financiera de este ticker
                valor_moneda = valores_monedas[
                    self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'financialCurrency'].values[0]
                ]

                # Descarga de los 4 estados financieros necesarios para este ticker
                obj = yf.Ticker(ticker)
                income_stmt = obj.income_stmt
                balance_sheet = obj.balance_sheet
                balance_sheet_q = obj.quarterly_balance_sheet
                cashflow_stmt = obj.cashflow

                # --- Ingresos totales (Total Revenue) de los últimos hasta 4 años ---
                # Se usa para calcular luego el CAGR de ingresos (revenue_cagr).
                try:
                    total_revenue = income_stmt.loc['Total Revenue'].dropna().tolist()[:4]
                    revenue_years = len(total_revenue)          # Cantidad de años con datos disponibles
                    total_revenue_last = total_revenue[0]        # Ingreso del año más reciente
                    total_revenue_first = total_revenue[-1]      # Ingreso del año más antiguo disponible
                except:
                    revenue_years = 0
                    total_revenue_last = 0
                    total_revenue_first = 0

                # --- EBIT (utilidad operacional) del período más reciente, convertido a moneda de referencia ---
                try:
                    ebit = income_stmt.loc['EBIT'].iloc[0] / valor_moneda
                except:
                    ebit = 0

                # --- Tasa impositiva efectiva usada para cálculos (Tax Rate For Calcs) ---
                try:
                    tax_rate = income_stmt.loc['Tax Rate For Calcs'].iloc[0] / valor_moneda
                except:
                    tax_rate = 0

                # --- Gasto por intereses ---
                try:
                    interest_expense = income_stmt.loc['Interest Expense'].iloc[0] / valor_moneda
                except:
                    interest_expense = 0

                # --- Caja y equivalentes de corto plazo (desde balance trimestral) ---
                try:
                    cash_equivalents = balance_sheet_q.loc['Cash Cash Equivalents And Short Term Investments'].iloc[0] / valor_moneda
                except:
                    cash_equivalents = 0

                # --- Deuda total (desde balance trimestral) ---
                try:
                    total_debt = balance_sheet_q.loc['Total Debt'].iloc[0] / valor_moneda
                except:
                    total_debt = 0

                # --- Capital invertido (Invested Capital), usado para calcular ROIC ---
                try:
                    invested_capital = balance_sheet.loc['Invested Capital'].iloc[0] / valor_moneda
                except:
                    invested_capital = 0

                # --- Cuentas por cobrar: período actual (1) y período anterior (2) ---
                # Se guardan ambos períodos para poder calcular la variación de
                # capital de trabajo operativo (var_operating_working_capital).
                try:
                    accounts_receivable_1 = balance_sheet.loc['Accounts Receivable'].iloc[0] / valor_moneda
                except:
                    accounts_receivable_1 = 0
                try:
                    accounts_receivable_2 = balance_sheet.loc['Accounts Receivable'].iloc[1] / valor_moneda
                except:
                    accounts_receivable_2 = 0

                # --- Inventario: período actual (1) y período anterior (2) ---
                try:
                    inventory_1 = balance_sheet.loc['Inventory'].iloc[0] / valor_moneda
                except:
                    inventory_1 = 0
                try:
                    inventory_2 = balance_sheet.loc['Inventory'].iloc[1] / valor_moneda
                except:
                    inventory_2 = 0

                # --- Otros activos corrientes: período actual (1) y período anterior (2) ---
                try:
                    other_current_assets_1 = balance_sheet.loc['Other Current Assets'].iloc[0] / valor_moneda
                except:
                    other_current_assets_1 = 0
                try:
                    other_current_assets_2 = balance_sheet.loc['Other Current Assets'].iloc[1] / valor_moneda
                except:
                    other_current_assets_2 = 0

                # --- Cuentas por pagar: período actual (1) y período anterior (2) ---
                try:
                    accounts_payable_1 = balance_sheet.loc['Accounts Payable'].iloc[0] / valor_moneda
                except:
                    accounts_payable_1 = 0
                try:
                    accounts_payable_2 = balance_sheet.loc['Accounts Payable'].iloc[1] / valor_moneda
                except:
                    accounts_payable_2 = 0

                # --- Otros pasivos corrientes: período actual (1) y período anterior (2) ---
                try:
                    other_current_liabilities_1 = balance_sheet.loc['Other Current Liabilities'].iloc[0] / valor_moneda
                except:
                    other_current_liabilities_1 = 0
                try:
                    other_current_liabilities_2 = balance_sheet.loc['Other Current Liabilities'].iloc[1] / valor_moneda
                except:
                    other_current_liabilities_2 = 0

                # --- Flujo de caja libre (Free Cash Flow) del período más reciente ---
                try:
                    free_cash_flow = cashflow_stmt.loc['Free Cash Flow'].iloc[0] / valor_moneda
                except:
                    free_cash_flow = 0

                # --- Gasto de capital (Capex), se usa valor absoluto porque yfinance lo reporta negativo ---
                try:
                    capital_expenditure = abs(cashflow_stmt.loc['Capital Expenditure'].iloc[0]) / valor_moneda
                except:
                    capital_expenditure = 0

                # --- Depreciación y amortización del período más reciente ---
                try:
                    depreciation_and_amortization = cashflow_stmt.loc['Depreciation And Amortization'].iloc[0] / valor_moneda
                except:
                    depreciation_and_amortization = 0

            except:
                # Si falla algo a nivel del ticker completo (ej. no se pudo determinar
                # el tipo de cambio, o yfinance no devolvió datos), se marcan todas las
                # variables como None para que quede explícito que no hay dato disponible
                # (a diferencia de los `except` internos, que usan 0 como valor por defecto).
                revenue_years = None
                total_revenue_last = None
                total_revenue_first = None
                ebit = None
                tax_rate = None
                interest_expense = None
                cash_equivalents = None
                total_debt = None
                invested_capital = None
                accounts_payable_1 = None
                accounts_payable_2 = None
                inventory_1 = None
                inventory_2 = None
                other_current_assets_1 = None
                other_current_assets_2 = None
                accounts_receivable_1 = None
                accounts_receivable_2 = None
                other_current_liabilities_1 = None
                other_current_liabilities_2 = None
                free_cash_flow = None
                capital_expenditure = None
                depreciation_and_amortization = None
            finally:
                # El bloque `finally` se ejecuta siempre (haya habido excepción o no),
                # asegurando que las columnas se escriban en el DataFrame para este
                # ticker con los valores calculados (o con None/0 en caso de error).
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'revenue_years'] = revenue_years
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'total_revenue_last'] = total_revenue_last
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'total_revenue_first'] = total_revenue_first
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'ebit'] = ebit
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'tax_rate'] = tax_rate
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'interest_expense'] = interest_expense
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'cash_equivalents'] = cash_equivalents
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'total_debt'] = total_debt
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'invested_capital'] = invested_capital
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'accounts_payable_1'] = accounts_payable_1
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'accounts_payable_2'] = accounts_payable_2
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'inventory_1'] = inventory_1
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'inventory_2'] = inventory_2
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'other_current_assets_1'] = other_current_assets_1
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'other_current_assets_2'] = other_current_assets_2
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'accounts_receivable_1'] = accounts_receivable_1
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'accounts_receivable_2'] = accounts_receivable_2
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'other_current_liabilities_1'] = other_current_liabilities_1
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'other_current_liabilities_2'] = other_current_liabilities_2
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'free_cash_flow'] = free_cash_flow
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'capital_expenditure'] = capital_expenditure
                self.df_class.df.loc[self.df_class.df['ticker'] == ticker, 'depreciation_and_amortization'] = depreciation_and_amortization
