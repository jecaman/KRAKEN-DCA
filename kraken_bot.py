import os
import time
import smtplib
import requests
import urllib.parse
import hashlib
import hmac
import base64
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
GMAIL_USER = "jesuscamposmanjon@gmail.com"  # Tu correo de envío
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Contraseña o clave de aplicación del correo

# Generar firma de Kraken
def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Solicitudes autenticadas a Kraken
def kraken_request(uri_path, data, key, secret):
    url = "https://api.kraken.com" + uri_path
    headers = {
        'API-Key': key,
        'API-Sign': get_kraken_signature(uri_path, data, secret)
    }
    resp = requests.post(url, headers=headers, data=data)

    print(f"HTTP Status Code: {resp.status_code}")
    print(f"Raw Response: {resp.text}")  # Mostrar el contenido de la respuesta completa

    try:
        response_json = resp.json()  # Convertir a JSON
        print("Response as JSON:", response_json)  # Mostrar el JSON procesado
        return response_json
    except ValueError as e:
        print(f"Error al procesar JSON: {e}")
        return {"error": ["No se pudo procesar la respuesta de Kraken"]}



# Obtener el precio de venta (ask price)
def get_ask_price(pair):
    resp = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={pair}").json()
    ask_price = resp['result'][pair]['a'][0]
    return float(ask_price)

# Crear una orden de mercado
def create_market_order(pair, to_invest, api_key, api_sec):
    ask_price = get_ask_price(pair)  # Precio actual
    min_volume = 0.00005  # Volumen mínimo en BTC (según Kraken)
    min_invest = min_volume * ask_price  # Monto mínimo en EUR requerido

    if to_invest < min_invest:
        print(f"Error: El monto mínimo para este par es {min_invest:.2f} EUR.")
        return {"error": ["Monto insuficiente para cumplir el volumen mínimo."]}, ask_price

    qty = round(to_invest / ask_price, 8)  # Redondear a 8 decimales

    if qty < min_volume:
        print(f"Error: El volumen calculado ({qty} BTC) no cumple con el mínimo permitido ({min_volume} BTC).")
        return {"error": ["Volumen mínimo no alcanzado."]}, ask_price

    data = {
        'nonce': str(int(1000 * time.time())),
        'ordertype': 'market',
        'type': 'buy',
        'volume': qty,
        'pair': pair,
    }
    resp = kraken_request('/0/private/AddOrder', data, api_key, api_sec)
    return resp, ask_price


# Enviar correo electrónico
def send_email(receiver, subject, msg, pwd):
    sender = GMAIL_USER
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, pwd)
        msg = f"Subject: {subject}\n\n{msg}"
        server.sendmail(sender, receiver, msg.encode('utf-8'))
        server.quit()
        print(f"Correo enviado a {receiver}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Probar la compra de 1 EUR de BTC/EUR
if __name__ == "__main__":
    try:
        pair = "XXBTZEUR"  # Par BTC/EUR
        to_invest = 16.66  # Monto en EUR
        print(f"Intentando crear una orden de {to_invest} EUR en el par {pair}...")

        order_response, ask_price = create_market_order(pair, to_invest, API_KEY, API_SECRET)
        print("Respuesta de la API (Orden):", order_response)

        if not order_response["error"]:
            # Extraer detalles de la compra
            txid = order_response['result']['txid'][0]
            print(f"Orden creada con éxito. TXID: {txid}")

            details_data = {
                'nonce': str(int(1000 * time.time())),
                'txid': txid
            }
            trade_response = kraken_request('/0/private/QueryOrders', details_data, API_KEY, API_SECRET)
            print("Respuesta de la API (Detalles de la Orden):", trade_response)

            # Obtener comisión
            trade_details = trade_response['result'][txid]
            fee = float(trade_details['fee'])
            qty = float(trade_details['vol'])
            total_cost = qty * ask_price

            # Preparar mensaje de correo
            msg = (
                f"Compra realizada:\n"
                f"Par: {pair}\n"
                f"Cantidad comprada: {qty:.8f} BTC\n"
                f"Precio unitario: {ask_price:.2f} EUR\n"
                f"Total invertido: {total_cost:.2f} EUR\n"
                f"Comisión: {fee:.2f} EUR\n"
                f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(msg)

            # Enviar correo con detalles
            send_email(
                receiver=GMAIL_USER,
                subject="DCA-KRAKEN",
                msg=msg,
                pwd=GMAIL_PASSWORD
            )
        else:
            # Enviar correo con error
            error_msg = f"Error en la compra: {order_response['error']}"
            print(error_msg)
            send_email(
                receiver=GMAIL_USER,
                subject="DCA-KRAKEN (Error)",
                msg=error_msg,
                pwd=GMAIL_PASSWORD
            )
    except Exception as e:
        print(f"Error general: {e}")

