import os
import time
import json

class GerenciadorLog:
    def __init__(self, caminho_arquivo, config_file_path):
        self.caminho_arquivo = caminho_arquivo
        self.config_file_path = config_file_path
        self.carregar_configuracoes()

    def carregar_configuracoes(self):
        try:
            with open(self.config_file_path, 'r') as config_file:
                config_data = json.load(config_file)
                self.num_linhas_para_manter = config_data.get('num_linhas_para_manter', 20)
        except FileNotFoundError:
            # Trate a situação em que o arquivo de configuração não é encontrado
            print(f'Arquivo de configuração {self.config_file_path} não encontrado. Usando valor padrão (20).')
            self.num_linhas_para_manter = 20

    def verificar_tamanho_limpar(self):
        try:
            # Verificar o tamanho do arquivo
            tamanho_arquivo = os.path.getsize(self.caminho_arquivo)

            # Se o tamanho for maior que zero
            if tamanho_arquivo > 0:
                # Ler todas as linhas do arquivo
                with open(self.caminho_arquivo, 'r') as f:
                    linhas = f.readlines()

                # Se o número de linhas for maior que o limite desejado
                if len(linhas) > self.num_linhas_para_manter:
                    # Manter apenas as últimas N linhas
                    linhas = linhas[-self.num_linhas_para_manter:]

                    # Escrever as linhas de volta no arquivo
                    with open(self.caminho_arquivo, 'w') as f:
                        f.writelines(linhas)

                    #print(f'Arquivo limpo, mantendo as últimas {self.num_linhas_para_manter} linhas.')
                #else:
                    #print(f'O arquivo já tem menos de {self.num_linhas_para_manter} linhas.')

            #else:
                #print('O arquivo está vazio.')

        except FileNotFoundError:
            print(f'O arquivo {self.caminho_arquivo} não foi encontrado.')