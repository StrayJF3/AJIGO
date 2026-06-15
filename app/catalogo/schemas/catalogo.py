# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import List, Dict, Optional
from sqlmodel import SQLModel

# ESQUEMA DE ENTRADA PARA ACTUALIZAR RESTAURANTES
class RestaurantUpdateRequest(SQLModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    bannerColor: Optional[str] = None
    badgeText: Optional[str] = None
    useImage: Optional[bool] = None
    imageSrc: Optional[str] = None

# ESQUEMA DE ENTRADA PARA CREAR PRODUCTOS DE COMIDA
class DishCreateRequest(SQLModel):
    name: str
    description: str
    price: float
    category: str
    tag: str
    badgeText: str
    spicyLevel: int = 0
    imageSrc: Optional[str] = None
    sizes: Optional[List[Dict]] = None
    extras: Optional[List[Dict]] = None

# ESQUEMA DE ENTRADA PARA ACTUALIZAR PRODUCTOS EXISTENTES
class DishUpdateRequest(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tag: Optional[str] = None
    badgeText: Optional[str] = None
    spicyLevel: Optional[int] = None
    imageSrc: Optional[str] = None
    sizes: Optional[List[Dict]] = None
    extras: Optional[List[Dict]] = None
