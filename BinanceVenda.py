import datetime
import json
import logging
import sqlite3
from binance.client import Client
import requests

from BotTelegram import BotTelegram

class BinanceVenda:
    def __init__(self, api_key, api_secret, config_file_path, conn):
        self.binance_client = Client(api_key, api_secret)
        self.config_file_path = config_file_path
        self.conn = conn

    def obter_step_size(self, simbolo_moeda):
        try:
            # Fazer uma solicitação à API da Binance para obter informações do par de criptomoedas
            response = requests.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={simbolo_moeda}')
            if response.status_code == 200:
                data = response.json()
                symbol_info = next((symbol for symbol in data['symbols'] if symbol['symbol'] == simbolo_moeda), None)
                if symbol_info:
                    for filter in symbol_info['filters']:
                        if filter['filterType'] == 'LOT_SIZE':
                            step_size = float(filter['stepSize'])
                            return step_size
                else:
                    logging.error(f"Símbolo {simbolo_moeda} não encontrado nas informações da Binance.")
                    return None
            else:
                logging.error(f"Erro ao obter informações do par {simbolo_moeda}")
                return None
        except Exception as e:
            logging.error(f"Erro ao obter o step size: {str(e)}")
            return None
        

    def realizar_venda(self, compra_id, simbolo_moeda, valor_atual):
        with open(self.config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
        
        chat_id = config_data['GRUPO_COMPRA_VENDA']

        # Configurar o logger com base nas configurações do JSON
        logging.basicConfig(filename=config_data['filenamelog'], level=getattr(logging, config_data['level_log']), format='%(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        
        try:

            # Obter o step size do par de criptomoedas
            step_size = self.obter_step_size(simbolo_moeda)
            if step_size is None:
                return
            

            # Obtenha informações sobre a carteira da moeda
            moedaSemPareamento = simbolo_moeda.split("USDT")
            carteira_moeda = self.binance_client.get_asset_balance(asset=moedaSemPareamento[0])
            saldo_moeda = float(carteira_moeda['free'])


            # Verifique se você tem saldo suficiente para a venda
            if saldo_moeda > step_size:
                # Ajuste a quantidade para ser um múltiplo do step size
                quantidade_ajustada = int(saldo_moeda / step_size) * step_size
                parse_mode='markdown'
                if int(quantidade_ajustada) > 0:
                # Ajuste adicional para 4 casas decimais
                    quantidade_ajustada = round(quantidade_ajustada, 4)
                logging.info(f"\n\nPrecisao {quantidade_ajustada} \n\n")
                venda = self.binance_client.create_order(
                    symbol=simbolo_moeda,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantidade_ajustada
                )

                # Atualize o status da compra para 'closed' no banco de dados
                self.atualizar_compra(compra_id, valor_atual)

                mensagem = (f"\n\n   💶💷 *ALERTA VENDA* 💰💰   \n\n Moeda: {simbolo_moeda}\n\n")
                botTelegran = BotTelegram('config.json')
                botTelegran.enviar_mensagem(chat_id,mensagem,parse_mode)
                logging.info(f"Venda realizada com sucesso: {simbolo_moeda} \n {venda} \n")

            else:
                logging.info(f"Saldo insuficiente para a venda de {simbolo_moeda}")

        except Exception as e:
            logging.info(f"Erro ao realizar a venda: {str(e)} - moeda -> {simbolo_moeda}")
            

    def atualizar_compra(self, compra_id, valor_atual):

            cursor = self.conn.cursor()

            # Obtenha a data atual para a venda
            data_venda = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') # %Y-%m-%d %H:%M:%S'

            # Atualize a tabela de compras com a data de venda, valor de venda e status
            cursor.execute("UPDATE compras SET data_venda = ?, valor_venda = ?, status = 'closed' WHERE id = ?",
                           (data_venda, valor_atual, compra_id))

            self.conn.commit()