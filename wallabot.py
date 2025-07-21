import logging
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
TOPICO_OBJETIVO_ID = int(os.getenv("7621263236:AAHH8o1TkEdcIh1DXN7Z2DNBX0Udqy2Kzu0"))  # ID del tópico 'chollos'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

WALLAPOP_REGEX = r'(https?://(?:www\.)?wallapop\.com/item/[^\s]+)'

def obtener_info_wallapop(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    ubicacion = soup.find('span', class_='card-location')
    precio = soup.find('span', class_='card-price')
    envio = soup.find('div', class_='shipment-tag')

    return {
        'ubicacion': ubicacion.text.strip() if ubicacion else 'No detectada',
        'precio': precio.text.strip() if precio else 'No disponible',
        'envio': 'Disponible' if envio and 'Envío disponible' in envio.text else 'Solo entrega en mano'
    }

aasync def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"ID del tópico: {update.message.message_thread_id}")
    return  # solo imprimir, sin hacer nada más por ahora

    texto = update.message.text
    match = re.search(WALLAPOP_REGEX, texto)
    if match:
        url = match.group(1)
        info = obtener_info_wallapop(url)
        if info:
            maps = f"https://www.google.com/maps/search/?api=1&query={info['ubicacion'].replace(' ', '+')}"
            respuesta = (
                f"📍 *Ubicación*: {info['ubicacion']}\n"
                f"💰 *Precio*: {info['precio']}\n"
                f"📦 *Envío*: {info['envio']}\n"
                f"🗺️ [Ver en Google Maps]({maps})"
            )
            await update.message.reply_text(respuesta, parse_mode='Markdown')

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
