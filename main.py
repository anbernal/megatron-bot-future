
import threading
import time
from AtualizacaoValorizacao import AtualizacaoValorizacao
from BinanceMFIAnalyzer import BinanceMFIAnalyzer
from GerenciadorCompra import GerenciadorCompra
from GerenciadorLog import GerenciadorLog
from GerenciadorVenda import GerenciadorVenda
from HistoricoValorizacao import HistoricoValorizacao

print("O MEGATRON FOI INICIADO ..... acompanhe pelo megatron.log")

def thread_compra():
    bot = GerenciadorCompra('config.json')
    bot.run()

def thread_venda():
    while True:
        gerenciador = GerenciadorVenda('config.json')
        gerenciador.verificar_compras_abertas()
        gerenciador.fechar_conexao()
        time.sleep(1)

def thread_mfi():
    while True:
        binance_analyzer = BinanceMFIAnalyzer('config.json')
        binance_analyzer.atualiza_mfi_moedas()
        time.sleep(15)

def thread_limpa_log():
    while True:
        gerenciador_log = GerenciadorLog('megatron.log', 'config.json')
        gerenciador_log.verificar_tamanho_limpar()
        time.sleep(60)

def thread_historico_valorizacao():
    while True:
        historico_valotizao = HistoricoValorizacao( 'config.json')
        historico_valotizao.gerar_historico_valorizacao()
        time.sleep(60)

def thread_atualizacao_valorizacao():
    while True:
        atualiza_valorizacao = AtualizacaoValorizacao( 'config.json')
        atualiza_valorizacao.enviar_atualizacao()
        time.sleep(1200)


if __name__ == "__main__":
    # Crie as threads
    thread1 = threading.Thread(target=thread_compra)
    thread2 = threading.Thread(target=thread_venda)
    thread3 = threading.Thread(target=thread_mfi)
    thread4 = threading.Thread(target=thread_limpa_log)
    thread5 = threading.Thread(target=thread_historico_valorizacao)
    thread6 = threading.Thread(target=thread_atualizacao_valorizacao)

    # Inicie as threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()

    # Aguarde até que ambas as threads terminem
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()