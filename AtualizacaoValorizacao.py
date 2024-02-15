import json
import sqlite3
from BinanceSpotBalance import BinanceSpotBalance

from BotTelegram import BotTelegram

class AtualizacaoValorizacao:
    def __init__(self, config_file_path):

        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)

        self.chat_id = config_data['GRUPO_ATUALIZACAO_VALORIZACAO']
        api_key = config_data['BINANCE_API_KEY']
        api_secret = config_data['BINANCE_API_SECRET']
        DATABASE_ADDRESS = "db/megatron.db"
        self.conexao = sqlite3.connect(DATABASE_ADDRESS)
        self.cursor = self.conexao.cursor()
        

        self.binance_balance = BinanceSpotBalance(api_key, api_secret)

    def consultar_valorizacao(self):
        try:
            
            consulta = """
                SELECT moeda.nome_moeda, compras.data_compra, compras.atual_valorizacao  
                FROM compras
                JOIN moeda ON compras.id_moeda = moeda.id
                WHERE compras.status = 'open' 
                ORDER BY compras.atual_valorizacao DESC;
            """

            # Executa a consulta
            self.cursor.execute(consulta)

            # Recupera os resultados
            resultados = self.cursor.fetchall()

            return resultados

        except sqlite3.Error as e:
            print(f"Erro ao executar a consulta SQL: {e}")
            return None
        
    def enviar_atualizacao(self):

        resultados = self.consultar_valorizacao()
        balances = self.binance_balance.get_balance()
        #print(f"dados balance: {balances}")
        saldo_atual = self.binance_balance.check_balance_usdt(balances)
        parse_mode='markdown'
        mensagem = "\n\n   📊 *NOVA ATUALIZAÇÃO* 📈   \n\n"

        if resultados:
            for resultado in resultados:
                mensagem += (f"Moeda: {resultado[0]}\nData: {resultado[1]}\nValorização: *{resultado[2]}%*\n\n")


        mensagem += (f"\n 💰 Saldo atual: *${saldo_atual}*  \n")
        mensagem += "\n     🎉 *FIM* 🎉     \n"
        botTelegran = BotTelegram('config.json')
        botTelegran.enviar_mensagem(self.chat_id,mensagem,parse_mode)

        # Fecha a conexão com o banco de dados
        self.fechar_conexao()

    def fechar_conexao(self):
        self.cursor.close()
        self.conexao.close()