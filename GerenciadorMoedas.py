import sqlite3

class GerenciadorMoedas:
    def __init__(self, nome_banco):
        self.conn = sqlite3.connect(nome_banco)
        self.cursor = self.conn.cursor()

    def listar_moedas(self):
        try:
            self.cursor.execute("SELECT nome_moeda, mfi_atual,historico_valorizacao FROM moeda order by historico_valorizacao")
            moedas = self.cursor.fetchall()
            return [(moeda[0], moeda[1],moeda[2]) for moeda in moedas]
        except sqlite3.Error as e:
            print(f"Erro ao listar criptomoedas: {e}")
            return []
        
    def listar_moedas_nome(self):
        try:
            self.cursor.execute("SELECT nome_moeda FROM moeda")
            moedas = self.cursor.fetchall()
            return [(moeda[0]) for moeda in moedas]
        except sqlite3.Error as e:
            print(f"Erro ao listar criptomoedas: {e}")
            return []

    def atualizar_mfi_moeda(self, nome_moeda, novo_mfi):
        try:
            self.cursor.execute("UPDATE moeda SET mfi_atual = ? WHERE nome_moeda = ?", (novo_mfi, nome_moeda))
            self.conn.commit()
            #print(f"MFI atualizado para a moeda {nome_moeda}: {novo_mfi}")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar MFI para a moeda {nome_moeda}: {e}")

    def atualizar_historico_valorizacao(self, nome_moeda, historico_valorizacao):
        try:
            self.cursor.execute("UPDATE moeda SET historico_valorizacao = ? WHERE nome_moeda = ?", (historico_valorizacao, nome_moeda))
            self.conn.commit()
            #print(f"Histórico de valorização atualizado para a moeda {nome_moeda}: {historico_valorizacao}")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar histórico de valorização para a moeda {nome_moeda}: {e}")


    def fechar_conexao(self):
        self.conn.close()



