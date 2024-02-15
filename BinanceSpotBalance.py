import requests
import hashlib
import hmac
import time

class BinanceSpotBalance:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.binance.com'

    def get_server_time(self):
        url = "https://api.binance.com/api/v1/time"
        response = requests.get(url)
        server_time = response.json()
        return server_time["serverTime"]
        
    def get_balance(self):
        server_time = self.get_server_time()
        endpoint = '/api/v3/account'
        params = {'timestamp': server_time, 'recvWindow': 15000} #6000
        headers = {'X-MBX-APIKEY': self.api_key}
        signature = self.generate_signature(params)
        params['signature'] = signature

        response = requests.get(self.base_url + endpoint, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data['balances']
        else:
            raise Exception(f"Failed to retrieve balance: {response.status_code} - {response.text}")
    
    def generate_signature(self, params):
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature
    
    def check_balance_usdt(self, balances):
        for item in balances:
            if item['asset'] == 'USDT':
                return float(item['free'])

def check_balance_min(balances, symbol, value):
    for item in balances:
        if item['asset'] == symbol:
            free_balance = float(item['free'])
            if free_balance >= value:
                return free_balance
            else:
                return 0.0
    return 0.0


