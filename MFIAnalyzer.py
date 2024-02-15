import ccxt
import pandas as pd

# Classe para verificar pares de negociação com MFI entre 10 e 30
class MFIAnalyzer:

    def __init__(self):
        self.exchange = ccxt.binance({
        'rateLimit': 1200,  # Limite de chamadas API por minuto
        'enableRateLimit': True,  # Ativar o limite de taxa
    })

    def calculate_mfi(self, data):
        typical_prices = [(ohlcv[2] + ohlcv[3] + ohlcv[4]) / 3 for ohlcv in data]

        raw_money_flow = [typical_price * volume for typical_price, volume in
                            zip(typical_prices, [ohlcv[5] for ohlcv in data])]

        positive_money_flow = [0]  # Inicializamos com zero para que os índices correspondam aos dados
        negative_money_flow = [0]  # Inicializamos com zero para que os índices correspondam aos dados

        for i in range(1, len(typical_prices)):
            if typical_prices[i] > typical_prices[i - 1]:
                positive_money_flow.append(raw_money_flow[i])
                negative_money_flow.append(0)
            elif typical_prices[i] < typical_prices[i - 1]:
                positive_money_flow.append(0)
                negative_money_flow.append(raw_money_flow[i])
            else:
                positive_money_flow.append(0)
                negative_money_flow.append(0)

        positive_money_flow_sum = sum(positive_money_flow[-14:])
        negative_money_flow_sum = sum(negative_money_flow[-14:])

        if negative_money_flow_sum == 0:
            mfi = 100
        else:
            money_ratio = positive_money_flow_sum / negative_money_flow_sum
            mfi = 100 - (100 / (1 + money_ratio))

        return mfi

    def find_pairs_with_mfi_between_10_and_30(self):
        # Defina o par de negociação base (USDT)
        base_symbol = 'USDT'
        base_symbol_UP = 'UP'
        base_symbol_DOWN = 'DOWN'

        markets = self.exchange.load_markets()
        spot_markets = [market for market in markets if market.endswith(base_symbol)]
        filtro_up = [par for par in spot_markets if par.endswith(base_symbol_UP)]
        pares_filtrado = [par for par in filtro_up if par.endswith(base_symbol_DOWN)]

        usdt_pairs_with_mfi_between_10_and_30 = []

        for symbol in pares_filtrado:

            try:
                mfi_data = self.exchange.fetch_ohlcv(symbol, timeframe='1w', limit=14)  # Intervalo de 1 semana
                mfi_value = self.calculate_mfi(mfi_data)
                if mfi_value is not None and mfi_value > 10 and mfi_value <= 20:
                    usdt_pairs_with_mfi_between_10_and_30.append(symbol)
                    print(f"{symbol} está entre 10 e 30 do MFI. MFI: {mfi_value}")

            except Exception as e:
                print(f"Erro ao processar o par {symbol}: {e}")
                continue

        return usdt_pairs_with_mfi_between_10_and_30