import json
import time
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from PIL import Image, ImageDraw, ImageFont  # Importa PIL per la gestione delle immagini
from waveshare_epd import epd2in13_V3  # Importa il driver per il display Waveshare V3

from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

# Funzione per ottenere dati di esempio (dummy)
def get_dummy_data():
    return []  # Aggiungi dati fittizi se necessario

# Funzione per ottenere i prezzi reali tramite l'API di Coinbase
def fetch_prices():
    logger.info('Fetching prices')
    timeslot_end = datetime.now(timezone.utc)
    end_date = timeslot_end.strftime(DATETIME_FORMAT)
    start_data = (timeslot_end - timedelta(days=DATA_SLICE_DAYS)).strftime(DATETIME_FORMAT)
    url = (f'https://api.exchange.coinbase.com/products/{config.currency}/candles?'
           f'granularity=900&start={urllib.parse.quote_plus(start_data)}&end={urllib.parse.quote_plus(end_date)}')
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    external_data = json.loads(response.text)
    prices = [entry[1:5] for entry in external_data[::-1]]
    return prices

# Funzione per migliorare la visibilità del display
def update_display(prices):
    logger.info('Updating display')
    
    # Crea un'immagine di dimensioni appropriate per il display
    image = Image.new('1', (epd.width, epd.height), 255)  # Bianco come sfondo
    draw = ImageDraw.Draw(image)
    
    # Imposta un font leggibile
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)  # Font più piccolo per visibilità
    
    # Pulisci il display per evitare sovrapposizioni
    epd.Clear(0xFF)
    
    # Scrivi i prezzi sullo schermo
    y_position = 10  # Posizione verticale iniziale
    for price in prices:
        text = f"BTC: {price[0]} USD"
        draw.text((10, y_position), text, font=font, fill=0)  # Usa il font grassetto
        y_position += 20  # Spazio tra le righe (ridotto per adattarsi meglio)
        if y_position > epd.height - 20:  # Aggiungi limite per evitare che il testo vada fuori schermo
            break
    
    # Mostra l'immagine sul display
    epd.display(epd.getbuffer(image))
    epd.sleep()  # Mette il display in modalità sleep per ridurre il consumo energetico

# Funzione principale
def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)

    # **Inizializza il display Waveshare 2.13 V3**
    epd = epd2in13_V3.EPD()  # Inizializzazione del display per il modello V3
    epd.init()  # Inizializza il display
    epd.Clear(0xFF)  # Pulisce il display (colore bianco)
    
    try:
        while True:
            try:
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                data_sink.update_observers(prices)
                
                # Aggiorna il display con i nuovi prezzi
                update_display(prices)

                time.sleep(config.refresh_interval * 60)  # Intervallo di aggiornamento in minuti

            except (HTTPError, URLError) as e:
                logger.error(str(e))
                time.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                time.sleep(5)

    except IOError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info('Exit')
        data_sink.close()
        epd.sleep()  # Mette il display in modalità sleep prima di uscire
        exit()

if __name__ == "__main__":
    main()
