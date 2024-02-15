import json
import requests

class BotTelegram:
    def __init__(self, config_file_path):

        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
        
        self.token = config_data['TOKEN_TELEGRAN']
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def enviar_mensagem(self, chat_id, mensagem, parse_mode=None):
        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': mensagem
        }
        
        if parse_mode:
            params['parse_mode'] = parse_mode

        response = requests.get(url, params=params)

        
        if response.status_code == 200:
            print("Mensagem enviada com sucesso!")
        else:
            print(f"Falha ao enviar mensagem. Código de status: {response.status_code}")
            print(response.text)
