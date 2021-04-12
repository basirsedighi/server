from pydantic import BaseModel


class freq(BaseModel):
    fps:int

class GpsData(BaseModel):
    velocity: str
    timestamp:str
    lat:str
    lon:str
    quality:int