import json
import time
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V3
from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

# Funzione per ottenere i dati di esempio (dummy)
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

# Funzione per ottenere i dati meteo da Serra Riccò
def get_weather():
    api_key = "c4f0f5faa1ec05bba4b975552a571784"
    city_id = "3166656"  # Serra Riccò's city ID
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather_data = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["description"]
            }
            return weather_data
        else:
            logger.error(f"Error fetching weather data: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching weather data: {e}")
        return None

# Funzione per migliorare la visibilità del display
def update_display(prices=None, weather_data=None):
    logger.info('Updating display')
    
    # Crea un'immagine di dimensioni appropriate per il display
    image = Image.new('1', (epd.width, epd.height), 255)  # Bianco come sfondo
    draw = ImageDraw.Draw(image)
    
    # Imposta un font leggibile
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)  # Font più piccolo per visibilità
    
    # Pulisci il display per evitare sovrapposizioni
    epd.Clear(0xFF)
    
    # Se i dati dei prezzi sono presenti, visualizzali
    if prices:
        y_position = 10
        for price in prices:
            text = f"BTC: {price[0]} USD"
            draw.text((10, y_position), text, font=font, fill=0)
            y_position += 20
            if y_position > epd.height - 20:
                break
    
    # Se i dati meteo sono presenti, visualizzali
    if weather_data:
        text = f"Temp: {weather_data['temperature']}°C"
        draw.text((10, y_position), text, font=font, fill=0)
        y_position += 20
        
        text = f"Humidity: {weather_data['humidity']}%"
        draw.text((10, y_position), text, font=font, fill=0)
        y_position += 20
        
        text = f"Weather: {weather_data['weather']}"
        draw.text((10, y_position), text, font=font, fill=0)

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
    epd = epd2in13_V3.EPD()  
    epd.init()  
    epd.Clear(0xFF)  
    
    try:
        while True:
            try:
                if time.time() % 120 < 60:  # Prima metà del ciclo: mostriamo i prezzi delle criptovalute
                    prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices()
                    data_sink.update_observers(prices)
                    update_display(prices=prices)
                else:  # Seconda metà del ciclo: mostriamo i dati meteo
                    weather_data = get_weather()
                    if weather_data:
                        update_display(weather_data=weather_data)
                
                time.sleep(60)  # 60 secondi per alternare

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
        epd.sleep()  
        exit()

if __name__ == "__main__":
    main()
