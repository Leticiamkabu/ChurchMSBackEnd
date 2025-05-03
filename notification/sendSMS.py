
import os
import requests

SMS_URL = os.getenv('SMS_API_URL')
SMS_API_KEY = os.getenv('API_KEY')
SMS_SENDER_ID = os.getenv('SENDER_ID')


async def send_sms(to, message):
    url = SMS_URL+ "?key=" + SMS_API_KEY + "&to=" + to + "&msg=" + message + "&sender_id=" + SMS_SENDER_ID 
    response = requests.get(url)
    data = response.json()

    return data 


async def send_bulk_sms(to, message):
    url = SMS_URL+ "?key=" + SMS_API_KEY + "&to=" + to + "&msg=" + message + "&sender_id=" + SMS_SENDER_ID 
    response = requests.get(url)
    data = response.json()

    return data 