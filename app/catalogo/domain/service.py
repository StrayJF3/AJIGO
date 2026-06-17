# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL Y JSON
import json
from typing import List, Dict, Optional
from sqlmodel import Session, text
from domain.models import Restaurante, Producto
from infrastructure.repository import (
    get_restaurant_by_slug,
    update_restaurant_data,
    save_new_restaurant,
    get_product_by_id,
    save_new_product,
    delete_product_data
)

# RETORNA LA LISTA DE RESTAURANTES CON RATING REAL CALCULADO DESDE V_RESUMEN_RESTAURANTE
def get_restaurants_list(session: Session) -> List[Dict]:
    # LA VISTA V_RESUMEN_RESTAURANTE INCLUYE: RestauranteID, NombreRestaurante, LogoURL, Descripcion,
    # SucursalID, DireccionSucursal, EstaAbierto, TotalPedidos, PromedioRating, TotalResenas
    query = text(
        "SELECT v.NombreRestaurante, v.LogoURL, v.Descripcion, v.PromedioRating, "
        "       r.Slug, r.Tagline, r.BadgeText, r.BannerColor, r.UseImage "
        "FROM V_RESUMEN_RESTAURANTE v "
        "INNER JOIN RESTAURANTES r ON v.RestauranteID = r.RestauranteID"
    )
    result = session.execute(query).fetchall()
    formatted = []
    for row in result:
        formatted.append({
            "id": row[4],           # Slug
            "name": row[0],
            "tagline": row[5],
            "rating": round(row[3], 1) if row[3] else 4.9,  # RATING REAL O 4.9 SI NO HAY RESENAS
            "badgeText": row[6],
            "bannerColor": row[7],
            "description": row[2],
            "useImage": bool(row[8]),
            "imageSrc": row[1]
        })
    return formatted

# CREA E INSERTA UN NUEVO RESTAURANTE EN LA BASE DE DATOS
def create_restaurant(session: Session, data: Dict) -> Dict:
    # VERIFICA QUE EL SLUG NO ESTE YA EN USO
    existing = get_restaurant_by_slug(session, data.get("slug", ""))
    if existing:
        raise ValueError("Ya existe un restaurante con ese slug.")

    new_restaurant = Restaurante(
        NombreRestaurante=data.get("name"),
        Descripcion=data.get("description"),
        Activo=True,
        Slug=data.get("slug"),
        Tagline=data.get("tagline"),
        BannerColor=data.get("bannerColor", "from-brand-red to-brand-orange"),
        BadgeText=data.get("badgeText"),
        LogoURL=data.get("imageSrc"),
        UseImage=data.get("useImage", False)
    )

    saved = save_new_restaurant(session, new_restaurant)

    return {
        "id": saved.Slug,
        "name": saved.NombreRestaurante,
        "tagline": saved.Tagline,
        "rating": 4.9,
        "badgeText": saved.BadgeText,
        "bannerColor": saved.BannerColor,
        "description": saved.Descripcion,
        "useImage": saved.UseImage,
        "imageSrc": saved.LogoURL
    }

# ACTUALIZA LOS PARAMETROS DE UN RESTAURANTE BUSCANDOLO POR SU SLUG
def update_restaurant(session: Session, slug: str, data: Dict) -> Dict:
    restaurante = get_restaurant_by_slug(session, slug)
    if not restaurante:
        raise ValueError("Restaurante no encontrado.")

    # REEMPLAZA LOS CAMPOS CON LOS DATOS DE ENTRADA
    if "name" in data:
        restaurante.NombreRestaurante = data["name"]
    if "tagline" in data:
        restaurante.Tagline = data["tagline"]
    if "description" in data:
        restaurante.Descripcion = data["description"]
    if "bannerColor" in data:
        restaurante.BannerColor = data["bannerColor"]
    if "badgeText" in data:
        restaurante.BadgeText = data["badgeText"]
    if "useImage" in data:
        restaurante.UseImage = data["useImage"]
    if "imageSrc" in data:
        restaurante.LogoURL = data["imageSrc"]

    updated = update_restaurant_data(session, restaurante)
    return {
        "id": updated.Slug,
        "name": updated.NombreRestaurante,
        "tagline": updated.Tagline,
        "rating": 4.9,
        "badgeText": updated.BadgeText,
        "bannerColor": updated.BannerColor,
        "description": updated.Descripcion,
        "useImage": updated.UseImage,
        "imageSrc": updated.LogoURL
    }

# RETORNA LA LISTA DE PRODUCTOS ACTIVOS USANDO LA VISTA V_MENU_SUCURSAL
def get_dishes_list(session: Session) -> List[Dict]:
    # LA VISTA V_MENU_SUCURSAL FILTRA: Activo=1, Stock>0, Sucursal activa y abierta
    # INCLUYE: ProductoID, NombreProducto, Descripcion, ImagenURL, Precio, Stock,
    #          NombreCategoria, SucursalID, DireccionSucursal, RestauranteID, NombreRestaurante
    query = text(
        "SELECT v.ProductoID, v.NombreProducto, v.Descripcion, v.ImagenURL, v.Precio, v.Stock, "
        "       v.NombreCategoria, pr.BadgeText, pr.SpicyLevel, pr.Sizes, pr.Extras, "
        "       r.Slug AS RestaurantSlug, v.NombreRestaurante AS RestaurantName "
        "FROM V_MENU_SUCURSAL v "
        "INNER JOIN PRODUCTOS pr ON v.ProductoID = pr.ProductoID "
        "INNER JOIN RESTAURANTES r ON v.RestauranteID = r.RestauranteID"
    )
    result = session.execute(query).fetchall()

    dishes = []
    for row in result:
        # COORDINA LAS OPCIONES DE TAMAÑO Y ADICIONALES (PARSEA EL FORMATO JSON)
        sizes = None
        if row[9]:
            try:
                sizes = json.loads(row[9])
            except Exception:
                sizes = []

        extras = None
        if row[10]:
            try:
                extras = json.loads(row[10])
            except Exception:
                extras = []

        dishes.append({
            "id": str(row[0]),
            "name": row[1],
            "description": row[2],
            "price": row[4],
            "category": row[11],
            "restaurant": row[12],
            "rating": 4.8,
            "badgeText": row[7],
            "tag": row[6],
            "spicyLevel": row[8],
            "imageSrc": row[3],
            "sizes": sizes,
            "extras": extras
        })
    return dishes

# CREA E INSERTA UN NUEVO PLATO ASOCIADO A UN RESTAURANTE
def add_dish(session: Session, data: Dict) -> Dict:
    category_slug = data.get("category", "piedra-negra")
    
    # BUSCA LA SUCURSAL ASOCIADA AL RESTAURANTE SLUG
    query_suc = text(
        "SELECT s.SucursalID, r.NombreRestaurante FROM SUCURSALES s "
        "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
        "WHERE r.Slug = :slug"
    )
    suc_result = session.execute(query_suc, {"slug": category_slug}).first()
    if not suc_result:
        raise ValueError("Sucursal no encontrada para el restaurante especificado.")
    
    suc_id = suc_result[0]
    rest_name = suc_result[1]

    # COMPILA LOS TAMANOS Y EXTRAS A JSON CADENA
    sizes_json = json.dumps(data.get("sizes")) if data.get("sizes") else None
    extras_json = json.dumps(data.get("extras")) if data.get("extras") else None

    # BUSCA LA CATEGORIA CORRESPONDIENTE EN LA BASE DE DATOS
    tag_name = data.get("tag", "Plato Fuerte")
    cat_query = text("SELECT CategoriaID FROM CATEGORIAS WHERE NombreCategoria = :name")
    cat_res = session.execute(cat_query, {"name": tag_name}).first()
    if cat_res:
        categoria_id = cat_res[0]
    else:
        # fallback a la primera categoria
        first_cat = session.execute(text("SELECT TOP 1 CategoriaID FROM CATEGORIAS")).first()
        categoria_id = first_cat[0] if first_cat else 1

    # CREA LA ENTIDAD DE PRODUCTO
    new_product = Producto(
        SucursalID=suc_id,
        CategoriaID=categoria_id,
        NombreProducto=data.get("name"),
        Descripcion=data.get("description"),
        ImagenURL=data.get("imageSrc"),
        Precio=data.get("price", 0.0),
        Stock=50,  # STOCK INICIAL POR DEFECTO
        Activo=True,
        Tag=tag_name,
        BadgeText=data.get("badgeText", "AJ"),
        SpicyLevel=data.get("spicyLevel", 0),
        Sizes=sizes_json,
        Extras=extras_json
    )

    saved_prod = save_new_product(session, new_product)
    
    # RETORNA EL PLATO CREADO CON LA TIPACION REQUERIDA
    return {
        "id": str(saved_prod.ProductoID),
        "name": saved_prod.NombreProducto,
        "description": saved_prod.Descripcion,
        "price": saved_prod.Precio,
        "category": category_slug,
        "restaurant": rest_name,
        "rating": 4.8,
        "badgeText": saved_prod.BadgeText,
        "tag": saved_prod.Tag,
        "spicyLevel": saved_prod.SpicyLevel,
        "imageSrc": saved_prod.ImagenURL,
        "sizes": data.get("sizes"),
        "extras": data.get("extras")
    }

# ACTUALIZA LOS VALORES DE UN PLATO DE COMIDA
def edit_dish(session: Session, dish_id: str, data: Dict) -> Dict:
    try:
        prod_id = int(dish_id)
    except ValueError:
        # SI EL ID ES TEXTO (EJ. MOCK), INTENTA OBTENERLO
        raise ValueError("Identificador de producto no numerico.")

    product = get_product_by_id(session, prod_id)
    if not product:
        raise ValueError("Plato no encontrado.")

    # ACTUALIZA LOS CAMPOS
    if "name" in data:
        product.NombreProducto = data["name"]
    if "description" in data:
        product.Descripcion = data["description"]
    if "price" in data:
        product.Precio = data["price"]
    if "tag" in data:
        product.Tag = data["tag"]
        cat_query = text("SELECT CategoriaID FROM CATEGORIAS WHERE NombreCategoria = :name")
        cat_res = session.execute(cat_query, {"name": data["tag"]}).first()
        if cat_res:
            product.CategoriaID = cat_res[0]
    if "badgeText" in data:
        product.BadgeText = data["badgeText"]
    if "spicyLevel" in data:
        product.SpicyLevel = data["spicyLevel"]
    if "imageSrc" in data:
        product.ImagenURL = data["imageSrc"]
    if "sizes" in data:
        product.Sizes = json.dumps(data["sizes"]) if data["sizes"] else None
    if "extras" in data:
        product.Extras = json.dumps(data["extras"]) if data["extras"] else None

    saved_prod = save_new_product(session, product)

    # BUSCA LOS DETALLES DEL RESTAURANTE NUEVAMENTE
    query_rest = text(
        "SELECT r.Slug, r.NombreRestaurante FROM SUCURSALES s "
        "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
        "WHERE s.SucursalID = :sid"
    )
    rest_result = session.execute(query_rest, {"sid": saved_prod.SucursalID}).first()
    category_slug = rest_result[0] if rest_result else "general"
    rest_name = rest_result[1] if rest_result else "Restaurante"

    # PARSEA LOS TAMANOS Y EXTRAS ANTES DE RETORNAR
    sizes = data.get("sizes") if "sizes" in data else (json.loads(saved_prod.Sizes) if saved_prod.Sizes else None)
    extras = data.get("extras") if "extras" in data else (json.loads(saved_prod.Extras) if saved_prod.Extras else None)

    return {
        "id": str(saved_prod.ProductoID),
        "name": saved_prod.NombreProducto,
        "description": saved_prod.Descripcion,
        "price": saved_prod.Precio,
        "category": category_slug,
        "restaurant": rest_name,
        "rating": 4.8,
        "badgeText": saved_prod.BadgeText,
        "tag": saved_prod.Tag,
        "spicyLevel": saved_prod.SpicyLevel,
        "imageSrc": saved_prod.ImagenURL,
        "sizes": sizes,
        "extras": extras
    }

# DESACTIVA UN PRODUCTO (ELIMINACION LOGICA)
def disable_dish(session: Session, dish_id: str) -> None:
    try:
        prod_id = int(dish_id)
    except ValueError:
        raise ValueError("Identificador de producto no numerico.")

    product = get_product_by_id(session, prod_id)
    if not product:
        raise ValueError("Plato no encontrado.")

    # REALIZA UNA ELIMINACION LOGICA DESACTIVANDO EL ITEM
    product.Activo = False
    save_new_product(session, product)
