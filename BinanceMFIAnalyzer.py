import json

import ccxt
import talib
import numpy as np

from GerenciadorMoedas import GerenciadorMoedas


class BinanceMFIAnalyzer:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.load_config()

        self.api_key = self.config_data.get('BINANCE_API_KEY')
        self.api_secret = self.config_data.get('BINANCE_API_SECRET')
        self.exchange = ccxt.binance({'apiKey': self.api_key, 'secret': self.api_secret})

    def load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            self.config_data = json.load(config_file)

    def get_mfi(self, symbol, timeframe='1w', period=14):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
            close_prices = np.array([data[4] for data in ohlcv], dtype=float)
            high_prices = np.array([data[2] for data in ohlcv], dtype=float)
            low_prices = np.array([data[3] for data in ohlcv], dtype=float)
            volume = np.array([data[5] for data in ohlcv], dtype=float)
            mfi = talib.MFI(high_prices, low_prices, close_prices, volume, timeperiod=period)
            return mfi[-1]
        except Exception as e:
            return None

    def is_mfi_between(self, symbol, min_value, max_value):
        mfi = self.get_mfi(symbol)
        if mfi is not None and min_value < mfi < max_value:
            return True
        return False

    def verificaEntreValores(self, mfi_value, min_mfi, max_mfi, max_mfi_historico, historico_valorizao, min_historico_val, max_historico_val):
        if min_mfi <= mfi_value <= max_mfi:
            return True
        elif min_mfi <= mfi_value <= max_mfi_historico and historico_valorizao is not None and min_historico_val is not None and max_historico_val is not None and min_historico_val >= historico_valorizao >= max_historico_val:
            return True
        else:
            return False
            

    def atualiza_mfi_moedas(self):
        DATABASE_ADDRESS = "db/megatron.db"
        gerenciador = GerenciadorMoedas(DATABASE_ADDRESS)
        moedas = gerenciador.listar_moedas_nome()

        for moeda in moedas:
            mfi = self.get_mfi(moeda)
            if mfi is not None:
                #print(f"Moeda: {moeda}, MFI: {mfi}")
                gerenciador.atualizar_mfi_moeda(moeda, mfi)
            else:
                print(f"Não foi possível obter o MFI para a moeda {moeda}")

        gerenciador.fechar_conexao()
