from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class LocationData(BaseModel):
    latitude: float
    longitude: float

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {"request": request, "api_key": API_KEY}
    return templates.TemplateResponse("index.html", {"request": context})

@app.post("/location")
async def save_location(request: Request, location_data: LocationData):
    latitude = location_data.latitude
    longitude = location_data.longitude

    # Получение информации о местоположении по координатам
    response = requests.get(f"https://geocode-maps.yandex.ru/1.x/?format=json&geocode={longitude},{latitude}&apikey={API_KEY}")
    location_data = response.json()

    # Обработка данных о местоположении
    if 'response' in location_data and 'GeoObjectCollection' in location_data['response']:
        geo_objects = location_data['response']['GeoObjectCollection']['featureMember']
        if len(geo_objects) > 0:
            geo_object = geo_objects[0]['GeoObject']
            address = geo_object['metaDataProperty']['GeocoderMetaData']['text']
            components = geo_object['metaDataProperty']['GeocoderMetaData']['Address']['Components']

            # Поиск города и страны в компонентах адреса
            city = ''
            country = ''
            for component in components:
                if 'locality' in component['kind']:
                    city = component['name']
                elif 'country' in component['kind']:
                    country = component['name']

            # Подготовка данных для отправки на клиент
            result = {
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'country': country,
                'address': address
            }
            return result

    # Если не удалось получить данные о местоположении
    return {'error': 'Location data not found'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
