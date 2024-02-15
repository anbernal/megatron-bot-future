import json
import logging
import sqlite3
import requests
from decouple import config

from BinanceVenda import BinanceVenda

class GerenciadorVenda:

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        with open(self.config_file_path, 'r') as config_file:
            self.config_data = json.load(config_file)

        api_key = self.config_data['BINANCE_API_KEY']
        api_secret = self.config_data['BINANCE_API_SECRET']
        DATABASE_ADDRESS = "db/megatron.db"
        base_url = 'https://api.binance.com/api/v3/ticker/price'

        self.conn = sqlite3.connect(DATABASE_ADDRESS)
        self.binance_api_key = api_key
        self.binance_api_secret = api_secret
        self.binance_api_base_url = base_url

    def verificar_compras_abertas(self):


        logging.basicConfig(filename=self.config_data['filenamelog'], level=getattr(logging, self.config_data['level_log']), format='%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        
        porcentagem_valorizacao = self.config_data['porcentagem_valorizacao']
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, id_moeda, permite_venda, valor_compra FROM compras WHERE status = 'open'")
        compras_abertas = cursor.fetchall()

        for compra in compras_abertas:
            compra_id, moeda_id, permite_venda, valor_compra = compra
            simbolo_moeda = self.obter_simbolo_moeda(moeda_id)
            valor_atual = self.obter_valor_atual(simbolo_moeda)

            valorizacao = ((valor_atual - valor_compra) / valor_compra) * 100

            if valorizacao >= porcentagem_valorizacao or (permite_venda == "S" and permite_venda is not None):
                self.realizar_venda(compra_id, simbolo_moeda,valor_atual)
            else:
                self.atualizar_valorizacao_no_banco(compra_id,valorizacao,simbolo_moeda)



    def obter_simbolo_moeda(self, moeda_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome_moeda FROM moeda WHERE id = ?", (moeda_id,))
        simbolo = cursor.fetchone()
        return simbolo[0] if simbolo else None

    def obter_valor_atual(self, simbolo):
        response = requests.get(f"{self.binance_api_base_url}?symbol={simbolo}")
        if response.status_code == 200:
            data = response.json()
            return float(data["price"])
        else:
            raise Exception(f"Failed to fetch current value for {simbolo}")

    def realizar_venda(self, compra_id, simbolo_moeda,valor_atual):
        logging.basicConfig(filename=self.config_data['filenamelog'], level=getattr(logging, self.config_data['level_log']), format='%(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        
        vendedorBinance = BinanceVenda(self.binance_api_key,self.binance_api_secret,self.config_file_path, self.conn)
        vendedorBinance.realizar_venda(compra_id, simbolo_moeda,valor_atual)

    def atualizar_valorizacao_no_banco(self, compra_id, valorizacao, simbolo_moeda):
        try:
            cursor = self.conn.cursor()

            cursor.execute("UPDATE compras SET atual_valorizacao = ? WHERE id = ?", (round(valorizacao, 2), compra_id))
            self.conn.commit()

            logging.info(f'Valorização atualizada no banco para a compra {simbolo_moeda} - LUCRO {round(valorizacao, 2)}%.')
        except Exception as e:
            logging.error(f"Erro ao atualizar valorização no banco de dados: {str(e)}")

    def fechar_conexao(self):
        self.conn.close()