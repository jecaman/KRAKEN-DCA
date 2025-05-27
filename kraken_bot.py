import os
import time
import random
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
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Nueva variable: Control de ejecución
EXECUTE_BOT = os.getenv("EXECUTE_BOT", "false").lower() == "true"
if not EXECUTE_BOT:
    print("Ejecución del bot desactivada. Saliendo...")
    exit(0)

# Configuración de reintentos y bloqueo
MAX_RETRIES = 5
RETRY_INTERVAL = 3600
LOCK_FILE = "bot.lock"

# Función mejorada para generar un nonce único
def generate_nonce():
    """Genera un nonce aleatorio basado en timestamp para evitar errores de Kraken."""
    return str(int(time.time() * 1000) + random.randint(1, 1000))

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
    data['nonce'] = generate_nonce()  # Nuevo nonce más robusto
    headers = {
        'API-Key': key,
        'API-Sign': get_kraken_signature(uri_path, data, secret)
    }
    
    resp = requests.post(url, headers=headers, data=data)
    print(f"HTTP Status Code: {resp.status_code}")
    print(f"Raw Response: {resp.text}")

    try:
        response_json = resp.json()
        print("Response as JSON:", response_json)
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
def create_limit_order_post_only(pair, to_invest, api_key, api_sec, price_offset=0.001):
    ask_price = get_ask_price(pair)
    min_volume = 0.00005
    min_invest = min_volume * ask_price

    if to_invest < min_invest:
        print(f"Error: El monto mínimo para este par es {min_invest:.2f} EUR.")
        return {"error": ["Monto insuficiente para cumplir el volumen mínimo."]}, ask_price

    qty = round(to_invest / ask_price, 8)
    if qty < min_volume:
        print(f"Error: El volumen calculado ({qty} BTC) no cumple con el mínimo permitido ({min_volume} BTC).")
        return {"error": ["Volumen mínimo no alcanzado."]}, ask_price

    # Definir un precio límite ligeramente inferior al precio actual para que sea post-only
    limit_price = round(ask_price * (1 - price_offset), 1)  # Ajusta a 1 decimal

    data = {
        'ordertype': 'limit',
        'type': 'buy',
        'volume': qty,
        'pair': pair,
        'price': limit_price,  # Orden límite a un precio menor
        'oflags': 'post',  # Activa el modo post-only
    }

    resp = kraken_request('/0/private/AddOrder', data, api_key, api_sec)
    return resp, ask_price

# Intentar obtener detalles de la orden con más tiempo entre intentos
def get_order_details(txid, api_key, api_sec, retries=10, delay=10):
    data = {'txid': txid}
    
    for attempt in range(retries):
        trade_response = kraken_request('/0/private/QueryOrders', data, api_key, api_sec)
        print(f"Intento {attempt + 1}/{retries}: {trade_response}")

        if trade_response["error"]:
            print(f"Error al consultar la orden: {trade_response['error']}")
        elif txid in trade_response.get("result", {}):
            order_details = trade_response["result"][txid]
            order_type = order_details.get("descr", {}).get("ordertype", "desconocido")  # Extraer el tipo de orden
            return order_details, order_type

        print(f"Esperando {delay} segundos antes de volver a intentar...")
        time.sleep(delay)

    print(f"⚠️ Advertencia: No se obtuvieron detalles de la orden después de {retries} intentos.")
    print(f"Última respuesta de Kraken: {trade_response}")
    return None

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

# Manejo de archivo de bloqueo
def create_lock_file():
    with open(LOCK_FILE, "w") as lock:
        lock.write(str(time.time()))

def remove_lock_file():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def is_locked():
    return os.path.exists(LOCK_FILE)

# Ejecutar el bot
if __name__ == "__main__":
    print("🚀 Script iniciado")
    print(f"EXECUTE_BOT: {EXECUTE_BOT}")
    time.sleep(5)
    try:
        if is_locked():
            print("El bot ya se está ejecutando. Cancelando esta instancia.")
            exit(0)

        create_lock_file()

        pair = "XXBTZEUR"
        to_invest = 36.66
        print(f"Intentando crear una orden de {to_invest} EUR en el par {pair}...")

        retry_count = 0
        while retry_count < MAX_RETRIES:
            order_response, ask_price = create_limit_order_post_only(pair, to_invest, API_KEY, API_SECRET)
            print("Respuesta de la API (Orden):", order_response)

            if not order_response["error"]:
                txid = order_response['result']['txid'][0]
                print(f"Orden creada con éxito. TXID: {txid}")

                trade_details, order_type = get_order_details(txid, API_KEY, API_SECRET)

                if trade_details:
                    fee = float(trade_details['fee'])
                    qty = float(trade_details['vol'])
                    total_cost = qty * ask_price

                    msg = (
                        f"Compra realizada:\n"
                        f"Par: {pair}\n"
                        f"Tipo de orden: {order_type}\n"
                        f"Cantidad comprada: {qty:.8f} BTC\n"
                        f"Precio unitario: {ask_price:.2f} EUR\n"
                        f"Total invertido: {total_cost:.2f} EUR\n"
                        f"Comisión: {fee:.2f} EUR\n"
                        f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    msg = f"Compra realizada:\nPar: {pair}\nTXID: {txid}\nNo se pudieron obtener los detalles completos de la orden."

                print(msg)
                send_email(GMAIL_USER, "DCA-KRAKEN", msg, GMAIL_PASSWORD)
                break
            else:
                error_msg = order_response["error"]
                msg = (
                    f"⚠️ ERROR EN LA COMPRA\n\n"
                    f"Par: {pair}\n"
                    f"Monto intentado: {to_invest:.2f} EUR\n"
                    f"Precio unitario estimado: {ask_price:.2f} EUR\n"
                    f"Error: {error_msg}\n"
                    f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print(msg)
                send_email(GMAIL_USER, "DCA-KRAKEN - Estado de Compra", msg, GMAIL_PASSWORD)
                break

    except Exception as e:
        error_msg = f"⚠️ ERROR GENERAL EN EL BOT\n\nError: {e}\nFecha: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(error_msg)
        send_email(GMAIL_USER, "DCA-KRAKEN - ERROR GENERAL", error_msg, GMAIL_PASSWORD)
    
    finally:
        remove_lock_file()
