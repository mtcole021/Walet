from config import BOT_TOKEN,CHAT_ID
import requests

def send_log(text):
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',data={
        'chat_id':CHAT_ID,
        'text':text
    })