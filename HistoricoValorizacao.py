import json
import requests
from datetime import datetime

from GerenciadorMoedas import GerenciadorMoedas

class HistoricoValorizacao:
    def __init__(self, config_file_path):

        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)

        DATABASE_ADDRESS = "db/megatron.db"
    
        self.api_key = config_data['BINANCE_API_KEY']
        self.api_secret = config_data['BINANCE_API_SECRET']
        self.base_url = 'https://api.binance.com'
        self.days_ago = config_data['DAYS_AGO']
        self.nome_banco = DATABASE_ADDRESS
        self.gerenciador_moedas = GerenciadorMoedas(self.nome_banco)
        print(f"\nINÍCIO DO HISTORICO DE VALORIZAÇÃO ----------- \n")

    def get_server_time(self):
        url = "https://api.binance.com/api/v1/time"
        response = requests.get(url)
        server_time = response.json()
        return server_time["serverTime"]

    def get_historical_price(self, symbol):
        current_time = int(self.get_server_time())
        start_time = current_time - (self.days_ago * 24 * 60 * 60 * 1000)  # Convert days to milliseconds
        endpoint = '/api/v1/klines'
        params = {
            'symbol': symbol,
            'interval': '1d',  # Daily interval
            'startTime': start_time,
            'endTime': current_time
        }

        response = requests.get(self.base_url + endpoint, params=params)

        if response.status_code == 200:
            klines = response.json()
            if klines and len(klines) > 0:
                # Use the closing price of the first candlestick as the historical price
                return float(klines[0][4])
            else:
                raise Exception(f"No historical data available for {symbol} in the specified time range.")
        else:
            raise Exception(f"Failed to retrieve historical price: {response.status_code} - {response.text}")

    def calcular_valorizacao(self, symbol):
        # Obter o preço atual
        endpoint_ticker = '/api/v3/ticker/price'
        params_ticker = {'symbol': symbol}
        response_ticker = requests.get(self.base_url + endpoint_ticker, params=params_ticker)

        if response_ticker.status_code == 200:
            current_price = float(response_ticker.json()['price'])
        else:
            raise Exception(f"Failed to retrieve current price: {response_ticker.status_code} - {response_ticker.text}")

        # Obter o preço histórico
        historical_price = self.get_historical_price(symbol)

        # Calcular a porcentagem de valorização/desvalorização
        percent_change = ((current_price - historical_price) / historical_price) * 100

        return percent_change
    
    def gerar_historico_valorizacao(self):
        gerenciador = GerenciadorMoedas(self.nome_banco)
        moedas = gerenciador.listar_moedas_nome()

        for moeda in moedas:
            try:
                valorizacao = self.calcular_valorizacao(moeda)
                if valorizacao is not None:
                    #print(f"Moeda: {moeda}, Valorização: {valorizacao}")
                    gerenciador.atualizar_historico_valorizacao(moeda, valorizacao)
                else:
                    print(f"Não foi possível obter a valorização para a moeda {moeda}")
            except Exception as e:
                print(f"Erro ao processar a moeda {moeda}: {e}")

        print(f"\nFIM DO HISTORICO DE VALORIZAÇÃO ----------- \n")
        gerenciador.fechar_conexao()