# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import List, Dict, Optional
from sqlmodel import SQLModel

# ESQUEMA DE ENTRADA PARA CREAR UN RESTAURANTE NUEVO
class RestaurantCreateRequest(SQLModel):
    name: str
    slug: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    bannerColor: Optional[str] = 'from-brand-red to-brand-orange'
    badgeText: Optional[str] = None
    imageSrc: Optional[str] = None
    useImage: Optional[bool] = False

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
