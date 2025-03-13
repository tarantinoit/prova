import json
import time
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError

from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V3  # **MODIFICA: Importa il driver per il modello V3 del display**

# Costanti per la gestione dei dati e delle date
DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

# **MODIFICA: Inizializzazione del display per il modello V3**
epd = epd2in13_V3.EPD()  # **MODIFICA: Inizializzazione del driver display per il modello V3**
epd.init()  # **MODIFICA: Inizializzazione del display V3**
epd.Clear(0xFF)  # **MODIFICA: Pulisce il display con il colore bianco**

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

# **MODIFICA: Funzione per aggiornare e mostrare i dati sul display**
def update_display(prices):
    logger.info('Updating display')
    
    # **MODIFICA: Crea un'immagine di dimensioni appropriate per il display**
    image = Image.new('1', (epd.width, epd.height), 255)  # Bianco come sfondo
    draw = ImageDraw.Draw(image)
    
    # **MODIFICA: Imposta un font più leggibile (grassetto e dimensione maggiore)**
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)  # **Font grassetto e dimensione 20**
    
    # Scrivi i prezzi sullo schermo
    y_position = 10  # Posizione verticale iniziale
    for price in prices:
        text = f"BTC: {price[0]} USD"
        draw.text((10, y_position), text, font=font, fill=0)
        y_position += 30  # Spazio tra le righe
        
    # **MODIFICA: Carica l'immagine nel display**
    epd.display(epd.getbuffer(image))
    epd.sleep()

# Funzione principale
def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)

    counter = 0  # Contatore per il refresh completo ogni X aggiornamenti

    try:
        while True:
            try:
                # Ottieni i dati
                prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()

                # **MODIFICA: Aggiorna il display con i nuovi dati**
                update_display(prices)
                
                # Incrementa il contatore
                counter += 1

                # **MODIFICA: Ogni 5 aggiornamenti forziamo un refresh completo**
                if counter % 5 == 0:
                    epd.Clear(0xFF)  # Pulisce il display

                # Tempo di attesa prima del prossimo aggiornamento (in secondi)
                time.sleep(config.refresh_interval * 60)

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
        epd.sleep()  # **MODIFICA: Rilascia risorse del display**
        exit()

if __name__ == "__main__":
    main()
