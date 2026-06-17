USE master;
GO
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'AJIGO')
BEGIN
    ALTER DATABASE AJIGO SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE AJIGO;
END
GO
CREATE DATABASE AJIGO;
GO
USE AJIGO;
GO

-- TABLA: ROLES
CREATE TABLE ROLES (
    RolID INT IDENTITY(1,1) NOT NULL,
    RolSTR NVARCHAR(50) NOT NULL,
    FechaCreacion DATETIME NULL,
    CONSTRAINT PK_ROLES PRIMARY KEY (RolID)
);
GO

-- TABLA: USUARIOS (ALMACENA LOS DATOS DE LOS USUARIOS REGISTRADOS Y SUS ROLES)
CREATE TABLE USUARIOS (
    UsuarioID INT IDENTITY(1,1) NOT NULL,
    RolID INT NOT NULL,
    NombreUsuario NVARCHAR(100) NULL,
    Email NVARCHAR(150) UNIQUE NOT NULL,
    Contrasena NVARCHAR(255) NOT NULL,
    Telefono NVARCHAR(20)  NULL,
    Activo BIT NOT NULL,
    PuntosAJIGO INT NULL DEFAULT 0,
    FechaRegistro DATETIME NOT NULL,
    DriverStatus NVARCHAR(50) NULL DEFAULT 'none',
    VehicleType NVARCHAR(50) NULL,
    LicensePlate NVARCHAR(50) NULL,
    CONSTRAINT PK_USUARIOS PRIMARY KEY (UsuarioID),
    CONSTRAINT FK_USUARIOS_ROLES FOREIGN KEY (RolID)
        REFERENCES ROLES (RolID)
);
GO

-- TABLA: SECTORES
CREATE TABLE SECTORES (
    SectorID INT IDENTITY(1,1) NOT NULL,
    SectorSTR NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_SECTORES PRIMARY KEY (SectorID)
);
GO

-- TABLA: RESTAURANTES (ALMACENA LOS RESTAURANTES DEL CAMPUS UIDE Y SUS PROPIEDADES ESTETICAS)
CREATE TABLE RESTAURANTES (
    RestauranteID INT IDENTITY(1,1) NOT NULL,
    NombreRestaurante NVARCHAR(150) NOT NULL,
    LogoURL NVARCHAR(MAX) NULL,
    Descripcion NVARCHAR(500) NULL,
    Activo BIT NOT NULL,
    Slug NVARCHAR(100) NOT NULL,
    Tagline NVARCHAR(250) NULL,
    BannerColor NVARCHAR(100) NULL,
    BadgeText NVARCHAR(20) NULL,
    UseImage BIT NULL DEFAULT 0,
    CONSTRAINT PK_RESTAURANTES PRIMARY KEY (RestauranteID)
);
GO

-- TABLA: SUCURSALES
CREATE TABLE SUCURSALES (
    SucursalID INT IDENTITY(1,1) NOT NULL,
    RestauranteID INT NOT NULL,              
    SectorID INT NOT NULL,              
    UsuarioID INT NULL,             
    DireccionDesc NVARCHAR(300) NOT NULL,
    Telefono NVARCHAR(20) NULL,
    EstaAbierto BIT NOT NULL,
    Activo BIT NOT NULL,
    FechaRegistro DATETIME NOT NULL,
    CONSTRAINT PK_SUCURSALES PRIMARY KEY (SucursalID),
    CONSTRAINT FK_SUCURSALES_RESTAURANTES FOREIGN KEY (RestauranteID)
        REFERENCES RESTAURANTES (RestauranteID),
    CONSTRAINT FK_SUCURSALES_SECTORES FOREIGN KEY (SectorID)
        REFERENCES SECTORES (SectorID),
    CONSTRAINT FK_SUCURSALES_USUARIOS FOREIGN KEY (UsuarioID)
        REFERENCES USUARIOS (UsuarioID)
);
GO

-- TABLA: CATEGORIAS
CREATE TABLE CATEGORIAS (
    CategoriaID INT IDENTITY(1,1) NOT NULL,
    NombreCategoria NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_CATEGORIAS PRIMARY KEY (CategoriaID)
);
GO

-- TABLA: PRODUCTOS (ALMACENA LOS PLATILLOS Y ARTICULOS DISPONIBLES EN CADA SUCURSAL)
CREATE TABLE PRODUCTOS (
    ProductoID INT IDENTITY(1,1) NOT NULL,
    SucursalID INT NOT NULL,              
    CategoriaID INT NOT NULL,           
    NombreProducto NVARCHAR(150) NOT NULL,
    Descripcion NVARCHAR(500) NULL,
    ImagenURL NVARCHAR(MAX) NULL,
    Precio FLOAT NOT NULL,
    Stock INT NOT NULL,
    Activo BIT NOT NULL,
    Tag NVARCHAR(50) NULL,
    BadgeText NVARCHAR(20) NULL,
    SpicyLevel INT NULL DEFAULT 0,
    Sizes NVARCHAR(MAX) NULL,
    Extras NVARCHAR(MAX) NULL,
    CONSTRAINT PK_PRODUCTOS PRIMARY KEY (ProductoID),
    CONSTRAINT FK_PRODUCTOS_SUCURSALES FOREIGN KEY (SucursalID)
        REFERENCES SUCURSALES (SucursalID),
    CONSTRAINT FK_PRODUCTOS_CATEGORIAS FOREIGN KEY (CategoriaID)
        REFERENCES CATEGORIAS (CategoriaID)
);
GO

-- TABLA: TIPO_ENTREGA
CREATE TABLE TIPO_ENTREGA (
    TipoEntregaID INT IDENTITY(1,1) NOT NULL,
    TipoEntregaSTR NVARCHAR(50) NOT NULL,
    CONSTRAINT PK_TIPO_ENTREGA PRIMARY KEY (TipoEntregaID)
);
GO

-- TABLA: ESTADOS_PEDIDO
CREATE TABLE ESTADOS_PEDIDO (
    EstadoPedidoID INT IDENTITY(1,1) NOT NULL,
    EstadoSTR NVARCHAR(50)  NOT NULL,
    CONSTRAINT PK_ESTADOS_PEDIDO PRIMARY KEY (EstadoPedidoID)
);
GO

-- TABLA: METODOS_PAGO
CREATE TABLE METODOS_PAGO (
    MetodoPagoID INT IDENTITY(1,1) NOT NULL,
    NombreMetodo NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_METODOS_PAGO PRIMARY KEY (MetodoPagoID)
);
GO

-- TABLA: ESTADO_ENVIO
CREATE TABLE ESTADO_ENVIO (
    EstadoID  INT IDENTITY(1,1) NOT NULL,
    EstadoSTR NVARCHAR(50) NOT NULL,
    CONSTRAINT PK_ESTADO_ENVIO PRIMARY KEY (EstadoID)
);
GO

-- TABLA: DIRECCION_USUARIOS
CREATE TABLE DIRECCION_USUARIOS (
    DireccionUsuarioID INT IDENTITY(1,1) NOT NULL,
    UsuarioID INT NOT NULL,                  
    SectorID INT NOT NULL,                  
    Descripcion NVARCHAR(300) NULL,
    CONSTRAINT PK_DIRECCION_USUARIOS PRIMARY KEY (DireccionUsuarioID),
    CONSTRAINT FK_DIRECCION_USUARIOS_USUARIOS FOREIGN KEY (UsuarioID)
        REFERENCES USUARIOS (UsuarioID),
    CONSTRAINT FK_DIRECCION_USUARIOS_SECTORES FOREIGN KEY (SectorID)
        REFERENCES SECTORES (SectorID)
);
GO

-- TABLA: PEDIDOS
CREATE TABLE PEDIDOS (
    PedidoID INT IDENTITY(1,1) NOT NULL,  
    UsuarioID INT NOT NULL,                
    SucursalID INT NOT NULL,                
    DireccionUsuarioID INT NULL,
    TipoEntregaID INT NOT NULL,                
    EstadoPedidoID INT NOT NULL,                
    Subtotal FLOAT NOT NULL,
    CostoEnvio FLOAT NOT NULL,
    MontoTotal FLOAT NOT NULL,
    FechaPedido DATETIME NOT NULL,
    CONSTRAINT PK_PEDIDOS PRIMARY KEY (PedidoID),
    CONSTRAINT FK_PEDIDOS_USUARIOS FOREIGN KEY (UsuarioID)
        REFERENCES USUARIOS (UsuarioID),
    CONSTRAINT FK_PEDIDOS_SUCURSALES FOREIGN KEY (SucursalID)
        REFERENCES SUCURSALES (SucursalID),
    CONSTRAINT FK_PEDIDOS_DIRECCION_USUARIOS FOREIGN KEY (DireccionUsuarioID)
        REFERENCES DIRECCION_USUARIOS (DireccionUsuarioID),
    CONSTRAINT FK_PEDIDOS_TIPO_ENTREGA FOREIGN KEY (TipoEntregaID)
        REFERENCES TIPO_ENTREGA (TipoEntregaID),
    CONSTRAINT FK_PEDIDOS_ESTADOS_PEDIDO FOREIGN KEY (EstadoPedidoID)
        REFERENCES ESTADOS_PEDIDO (EstadoPedidoID)
);
GO

-- TABLA: DETALLE_PEDIDO
CREATE TABLE DETALLE_PEDIDO (
    DetalleID INT IDENTITY(1,1) NOT NULL,
    PedidoID INT NOT NULL,
    ProductoID INT NOT NULL,
    Cantidad INT NOT NULL,
    PrecioUnitario FLOAT NOT NULL,
    PrecioFinal FLOAT NOT NULL,
    Notas NVARCHAR(300) NULL,
    CONSTRAINT PK_DETALLE_PEDIDO PRIMARY KEY (DetalleID),
    CONSTRAINT FK_DETALLE_PEDIDO_PEDIDOS FOREIGN KEY (PedidoID)
        REFERENCES PEDIDOS (PedidoID),
    CONSTRAINT FK_DETALLE_PEDIDO_PRODUCTOS FOREIGN KEY (ProductoID)
        REFERENCES PRODUCTOS (ProductoID)
);
GO

-- TABLA: PAGOS
CREATE TABLE PAGOS (
    PagoID INT IDENTITY(1,1) NOT NULL,
    PedidoID INT NOT NULL,
    MetodoPagoID INT NOT NULL,
    Monto FLOAT NOT NULL,
    EstadoPago NVARCHAR(50) NOT NULL,
    ComprobanteURL NVARCHAR(MAX) NULL,
    FechaPago DATETIME NULL,
    CONSTRAINT PK_PAGOS PRIMARY KEY (PagoID),
    CONSTRAINT FK_PAGOS_PEDIDOS FOREIGN KEY (PedidoID)
        REFERENCES PEDIDOS (PedidoID),
    CONSTRAINT FK_PAGOS_METODOS_PAGO FOREIGN KEY (MetodoPagoID)
        REFERENCES METODOS_PAGO (MetodoPagoID)
);
GO

-- TABLA: RESENAS
CREATE TABLE RESENAS (
    ResenaID INT IDENTITY(1,1) NOT NULL,
    PedidoID INT NOT NULL,
    Puntuacion INT NOT NULL,
    Comentario NVARCHAR(500) NULL,
    FechaResena DATETIME NOT NULL,
    CONSTRAINT PK_RESENAS PRIMARY KEY (ResenaID),
    CONSTRAINT FK_RESENAS_PEDIDOS FOREIGN KEY (PedidoID)
        REFERENCES PEDIDOS (PedidoID),
    CONSTRAINT CHK_RESENAS_PUNTUACION CHECK (Puntuacion BETWEEN 1 AND 5)
);
GO

-- TABLA: ENVIOS
CREATE TABLE ENVIOS (
    EnvioID INT IDENTITY(1,1) NOT NULL,
    PedidoID INT NOT NULL,             
    UsuarioID INT NOT NULL,            
    EstadoID INT NOT NULL,             
    FechaInicio DATETIME NOT NULL,
    FechaEntrega DATETIME NULL,
    CONSTRAINT PK_ENVIOS PRIMARY KEY (EnvioID),
    CONSTRAINT FK_ENVIOS_PEDIDOS FOREIGN KEY (PedidoID)
        REFERENCES PEDIDOS (PedidoID),
    CONSTRAINT FK_ENVIOS_USUARIOS FOREIGN KEY (UsuarioID)
        REFERENCES USUARIOS (UsuarioID),
    CONSTRAINT FK_ENVIOS_ESTADO_ENVIO FOREIGN KEY (EstadoID)
        REFERENCES ESTADO_ENVIO (EstadoID)
);
GO

-- TABLA: HISTORIAL_PEDIDOS
CREATE TABLE HISTORIAL_PEDIDOS (
    HistorialID INT IDENTITY(1,1) NOT NULL,  
    PedidoID INT NOT NULL,                  
    EstadoPedidoID INT NOT NULL,                  
    FechaCambio DATETIME NOT NULL,
    CONSTRAINT PK_HISTORIAL_PEDIDOS PRIMARY KEY (HistorialID),
    CONSTRAINT FK_HISTORIAL_PEDIDOS_PEDIDOS FOREIGN KEY (PedidoID)
        REFERENCES PEDIDOS (PedidoID),
    CONSTRAINT FK_HISTORIAL_PEDIDOS_ESTADOS_PEDIDO FOREIGN KEY (EstadoPedidoID)
        REFERENCES ESTADOS_PEDIDO (EstadoPedidoID)
);
GO

-- TABLA: CARRITOS
CREATE TABLE CARRITOS (
    CarritoID INT IDENTITY(1,1) NOT NULL,
    UsuarioID INT NOT NULL,
    SucursalID INT NOT NULL,
    FechaActualizacion DATETIME NOT NULL,
    CONSTRAINT PK_CARRITOS PRIMARY KEY (CarritoID),
    CONSTRAINT FK_CARRITOS_USUARIOS FOREIGN KEY (UsuarioID)
        REFERENCES USUARIOS (UsuarioID),
    CONSTRAINT FK_CARRITOS_SUCURSALES FOREIGN KEY (SucursalID)
        REFERENCES SUCURSALES (SucursalID)
);
GO

-- TABLA: CARRITO_ITEMS
CREATE TABLE CARRITO_ITEMS (
    ItemID INT IDENTITY(1,1) NOT NULL,
    CarritoID  INT NOT NULL,              
    ProductoID INT NOT NULL,
    Cantidad INT NOT NULL,
    Notas NVARCHAR(300) NULL,
    CONSTRAINT PK_CARRITO_ITEMS PRIMARY KEY (ItemID),
    CONSTRAINT FK_CARRITO_ITEMS_CARRITOS FOREIGN KEY (CarritoID)
        REFERENCES CARRITOS (CarritoID),
    CONSTRAINT FK_CARRITO_ITEMS_PRODUCTOS FOREIGN KEY (ProductoID)
        REFERENCES PRODUCTOS (ProductoID)
);

GO

-- VISTAS

CREATE VIEW V_PEDIDOS_COMPLETO AS
SELECT
    p.PedidoID, p.FechaPedido, p.Subtotal, p.CostoEnvio, p.MontoTotal,
    u.UsuarioID, u.NombreUsuario, u.Email,
    s.SucursalID, s.DireccionDesc AS DireccionSucursal,
    r.NombreRestaurante,
    ep.EstadoSTR      AS EstadoPedido,
    te.TipoEntregaSTR AS TipoEntrega,
    du.Descripcion    AS DireccionEntrega
FROM PEDIDOS p
    INNER JOIN USUARIOS           u  ON p.UsuarioID          = u.UsuarioID
    INNER JOIN SUCURSALES         s  ON p.SucursalID         = s.SucursalID
    INNER JOIN RESTAURANTES       r  ON s.RestauranteID      = r.RestauranteID
    INNER JOIN ESTADOS_PEDIDO     ep ON p.EstadoPedidoID     = ep.EstadoPedidoID
    INNER JOIN TIPO_ENTREGA       te ON p.TipoEntregaID      = te.TipoEntregaID
    LEFT  JOIN DIRECCION_USUARIOS du ON p.DireccionUsuarioID = du.DireccionUsuarioID;
GO

CREATE VIEW V_DETALLE_PEDIDO_PRODUCTOS AS
SELECT
    dp.DetalleID, dp.PedidoID, dp.Cantidad, dp.PrecioUnitario, dp.PrecioFinal, dp.Notas,
    pr.ProductoID, pr.NombreProducto, pr.ImagenURL,
    c.NombreCategoria
FROM DETALLE_PEDIDO dp
    INNER JOIN PRODUCTOS  pr ON dp.ProductoID  = pr.ProductoID
    INNER JOIN CATEGORIAS c  ON pr.CategoriaID = c.CategoriaID;
GO

CREATE VIEW V_MENU_SUCURSAL AS
SELECT
    pr.ProductoID, pr.NombreProducto, pr.Descripcion, pr.ImagenURL, pr.Precio, pr.Stock,
    c.NombreCategoria,
    s.SucursalID, s.DireccionDesc AS DireccionSucursal,
    r.RestauranteID, r.NombreRestaurante
FROM PRODUCTOS pr
    INNER JOIN CATEGORIAS   c ON pr.CategoriaID  = c.CategoriaID
    INNER JOIN SUCURSALES   s ON pr.SucursalID   = s.SucursalID
    INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID
WHERE pr.Activo = 1 AND pr.Stock > 0 AND s.Activo = 1 AND s.EstaAbierto = 1;
GO

CREATE VIEW V_HISTORIAL_ESTADOS AS
SELECT
    hp.HistorialID, hp.PedidoID, hp.FechaCambio,
    ep.EstadoSTR AS Estado,
    u.NombreUsuario, u.Email
FROM HISTORIAL_PEDIDOS hp
    INNER JOIN ESTADOS_PEDIDO ep ON hp.EstadoPedidoID = ep.EstadoPedidoID
    INNER JOIN PEDIDOS        p  ON hp.PedidoID       = p.PedidoID
    INNER JOIN USUARIOS       u  ON p.UsuarioID       = u.UsuarioID;
GO

CREATE VIEW V_RESUMEN_RESTAURANTE AS
SELECT
    r.RestauranteID, r.NombreRestaurante, r.LogoURL, r.Descripcion,
    s.SucursalID, s.DireccionDesc AS DireccionSucursal, s.EstaAbierto,
    COUNT(DISTINCT p.PedidoID)              AS TotalPedidos,
    AVG(CAST(re.Puntuacion AS FLOAT))       AS PromedioRating,
    COUNT(DISTINCT re.ResenaID)             AS TotalResenas
FROM RESTAURANTES r
    INNER JOIN SUCURSALES s  ON r.RestauranteID = s.RestauranteID
    LEFT  JOIN PEDIDOS    p  ON s.SucursalID    = p.SucursalID
    LEFT  JOIN RESENAS    re ON p.PedidoID      = re.PedidoID
WHERE r.Activo = 1
GROUP BY
    r.RestauranteID, r.NombreRestaurante, r.LogoURL, r.Descripcion,
    s.SucursalID, s.DireccionDesc, s.EstaAbierto;
GO

-- TRIGGERS

CREATE TRIGGER TRG_PEDIDOS_HISTORIAL
ON PEDIDOS
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    IF UPDATE(EstadoPedidoID)
    BEGIN
        INSERT INTO HISTORIAL_PEDIDOS (PedidoID, EstadoPedidoID, FechaCambio)
        SELECT i.PedidoID, i.EstadoPedidoID, GETDATE()
        FROM inserted i;
    END
END;
GO

CREATE TRIGGER TRG_DETALLE_PEDIDO_STOCK
ON DETALLE_PEDIDO
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
            INNER JOIN PRODUCTOS pr ON i.ProductoID = pr.ProductoID
        WHERE pr.Stock < i.Cantidad
    )
    BEGIN
        RAISERROR('Stock insuficiente para uno o mas productos del pedido.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
    UPDATE pr
    SET pr.Stock = pr.Stock - i.Cantidad
    FROM PRODUCTOS pr INNER JOIN inserted i ON pr.ProductoID = i.ProductoID;
END;
GO

CREATE TRIGGER TRG_CARRITO_SUCURSAL_UNICA
ON CARRITO_ITEMS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
            INNER JOIN CARRITOS  ca ON i.CarritoID  = ca.CarritoID
            INNER JOIN PRODUCTOS pr ON i.ProductoID = pr.ProductoID
        WHERE ca.SucursalID <> pr.SucursalID
    )
    BEGIN
        RAISERROR('No puedes agregar productos de distintas sucursales al mismo carrito.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

CREATE TRIGGER TRG_RESENA_VALIDAR_PEDIDO
ON RESENAS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
            INNER JOIN PEDIDOS p ON i.PedidoID = p.PedidoID
        WHERE p.EstadoPedidoID <> 4
    )
    BEGIN
        RAISERROR('Solo puedes resenar un pedido que ya fue entregado.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

CREATE TRIGGER TRG_ENVIO_SOLO_REPARTIDOR
ON ENVIOS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (
        SELECT 1 FROM inserted i
            INNER JOIN USUARIOS u ON i.UsuarioID = u.UsuarioID
        WHERE u.RolID <> 2
    )
    BEGIN
        RAISERROR('El usuario asignado al envio debe tener el rol de Repartidor.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

-- DATOS INICIALES (SEMBRA DE DATOS GENERALES DEL SISTEMA)
INSERT INTO ROLES (RolSTR, FechaCreacion) VALUES
    ('Cliente',        GETDATE()),  -- RolID = 1
    ('Repartidor',     GETDATE()),  -- RolID = 2
    ('Administrador',  GETDATE()),  -- RolID = 3
    ('Usuario Maestro', GETDATE()); -- RolID = 4
GO

-- INSERTA LAS CATEGORIAS DE PRODUCTOS
INSERT INTO CATEGORIAS (NombreCategoria) VALUES 
    ('Bebida'),
    ('Postre'),
    ('Entrada'),
    ('Plato Fuerte'),
    ('Sándwich');
GO

-- INSERTA LOS METODOS DE PAGO (MEDIOS ADMITIDOS PARA CANCELAR PEDIDOS)
INSERT INTO METODOS_PAGO (NombreMetodo) VALUES 
    ('Efectivo'),
    ('Transferencia Bancaria'),
    ('Tarjeta de Credito/Debito');
GO

-- INSERTA LOS TIPOS DE ENTREGA (OPCIONES DE LOGISTICA DISPONIBLES)
INSERT INTO TIPO_ENTREGA (TipoEntregaSTR) VALUES 
    ('Delivery'),
    ('Retiro');
GO

-- INSERTA LOS ESTADOS DE PEDIDO (FLUJO DE ESTADOS DE UN PEDIDO)
INSERT INTO ESTADOS_PEDIDO (EstadoSTR) VALUES 
    ('Recibido'),
    ('En Preparacion'),
    ('Listo / En Camino'),
    ('Entregado');
GO

-- INSERTA LOS ESTADOS DE ENVIO (FLUJO DE ESTADOS DE LA ENTREGA)
INSERT INTO ESTADO_ENVIO (EstadoSTR) VALUES 
    ('Asignado'),
    ('En Camino'),
    ('Entregado');
GO

-- INSERTA LOS SECTORES (AREAS DE LOGISTICA Y UBICACION)
INSERT INTO SECTORES (SectorSTR) VALUES 
    ('UIDE Campus');
GO

-- INSERTA LOS RESTAURANTES (COMERCIOS ASOCIADOS EN EL CAMPUS UIDE)
INSERT INTO RESTAURANTES (NombreRestaurante, LogoURL, Descripcion, Activo, Slug, Tagline, BannerColor, BadgeText, UseImage) VALUES
    ('Piedra Negra', '/piedra-negra-logo.png', 'El rincon del buen cafe y los postres artesanales en la UIDE. Espresso, lattes, tartas y reposteria recien horneada.', 1, 'piedra-negra', 'Cafeteria Fina & Postres Exclusivos', 'from-pink-950 to-pink-900', 'PN', 1),
    ('El Capi', NULL, 'Los bolones de verde y tigrillos mas crujientes del campus. Sabor criollo tradicional con extra queso y chicharron.', 1, 'el-capi', 'Especialistas en Bolones & Tigrillos criollos', 'from-cyan-950 to-cyan-900', 'EC', 0),
    ('Collage', NULL, 'Piqueos, chocolates, gaseosas, energizantes y suministros rapidos de mini market directamente a tu facultad.', 1, 'collage', 'Tu Mini Market Universitario', 'from-purple-950 to-purple-900', 'CO', 0),
    ('UIDE Bakery', '/uide-bakery-1.png', 'Panaderia artesanal horneada directamente en el campus de la UIDE. Croissants de mantequilla, pan rustico y reposteria dulce selecta.', 1, 'uide-bakery', 'Panes de Masa Madre & Reposteria Fina', 'from-amber-950 to-amber-900', 'UB', 1),
    ('El Cargo', NULL, 'Hamburguesas artesanales a la parrilla y papas rusticas recien hechas. Sabor y calidad premium en cualquier momento del dia en la UIDE.', 1, 'el-cargo', 'Hamburguesas & Papas Fritas', 'from-emerald-950 to-emerald-900', 'ECG', 0),
    ('Toscana', NULL, 'Sabores tradicionales de Italia en la UIDE. Pizzas crujientes de masa delgada y pastas frescas preparadas al momento.', 1, 'toscana', 'Pizzas Artesanales & Pastas Italianas', 'from-rose-950 to-rose-900', 'TO', 0),
    ('Happy Coffee', NULL, 'Variedad de bebidas calientes y heladas, sanduches gourmet y postres perfectos para tus horas de estudio.', 1, 'happy-coffee', 'El Cafe que Alegra tus Mananas', 'from-yellow-950 to-yellow-900', 'HC', 0),
    ('La Hueca', NULL, 'Los mejores cevichochos del campus, ceviches frescos y platos tipicos ecuatorianos con el autentico sabor tradicional.', 1, 'la-hueca', 'Cevichochos & Tradicion Ecuatoriana', 'from-orange-950 to-orange-900', 'LH', 0),
    ('Hanaska', NULL, 'Comida gourmet saludable, ensaladas personalizadas, bowls y wraps frescos con ingredientes locales seleccionados.', 1, 'hanaska', 'Gourmet Catering & Comidas Saludables', 'from-indigo-950 to-indigo-900', 'HA', 0);
GO

-- INSERTA LOS USUARIOS ADMINISTRADORES DE LOS RESTAURANTES (PRIMEROS EN LA BD PARA QUE COINCIDAN CON IDs 1 A 9)
INSERT INTO USUARIOS (RolID, NombreUsuario, Email, Contrasena, Activo, PuntosAJIGO, FechaRegistro, DriverStatus) VALUES
    (3, 'Admin Piedra Negra', 'adminpn@gmail.com', '$2b$12$/CrQAkq/x068m9EzSNxwoe.dPVdOr70IuhID/AYx.95oRHy9uxUVS', 1, 0, GETDATE(), 'none'),
    (3, 'Admin El Capi', 'admincp@gmail.com', '$2b$12$23T34lRhqOBs0VVyXAPcJuy6fA.gNkgH0kD9ZAEmIWxUWzvgusH8a', 1, 0, GETDATE(), 'none'),
    (3, 'Admin Collage', 'admincg@gmail.com', '$2b$12$hq254Nt2/LVgeR3O3.2x.OfXxp1M0tzo6a3iAZLQaMcykLmH57GYO', 1, 0, GETDATE(), 'none'),
    (3, 'Admin UIDE Bakery', 'adminbk@gmail.com', '$2b$12$CM6mfUpWb6evJfVppTx12OZrajclcstAAowPTAl2fzJifq5odnIVS', 1, 0, GETDATE(), 'none'),
    (3, 'Admin El Cargo', 'adminco@gmail.com', '$2b$12$OjJxb9EqIx7gVcgQMIlqfOXoTNgMAu4vtxZTSLUpOLIzg2xhQW3TO', 1, 0, GETDATE(), 'none'),
    (3, 'Admin Toscana', 'admints@gmail.com', '$2b$12$wMhthl51TN0l0r1b1.b/W.mDiH2aKx.GB1zdyxU1UPbdqlRLfwOKq', 1, 0, GETDATE(), 'none'),
    (3, 'Admin Happy Coffee', 'adminhc@gmail.com', '$2b$12$PSpYwkm/seYt5tTLqKx1ZOBaopDAWid7QrW/aPepiwWyPWoLkMkuG', 1, 0, GETDATE(), 'none'),
    (3, 'Admin La Hueca', 'adminLh@gmail.com', '$2b$12$5sO4h90RKosfTroGyn8fa.2Wqp9I4zUfAQruI2hlAqknvvZPR0vZK', 1, 0, GETDATE(), 'none'),
    (3, 'Admin Hanaska', 'adminhk@gmail.com', '$2b$12$kCRVAd2.HXJusDtbQ7l.CuN.cxOT2bzhI.TXWXbtQnUUNO/xMKbUe', 1, 0, GETDATE(), 'none'),
    (4, 'Usuario Maestro', 'adminmaestro@gmail.com', '$2b$12$XwWQIJpOt1KkhMnlPF9w0./Cl1jn8qKmfyE34INiIQknfv76i6nyK', 1, 0, GETDATE(), 'none');
GO

-- INSERTA LAS SUCURSALES (ESTABLECIMIENTOS FISICOS VINCULADOS A CADA LOCAL ASIGNANDO SUS USUARIOS RESPECTIVOS)
INSERT INTO SUCURSALES (RestauranteID, SectorID, UsuarioID, DireccionDesc, Telefono, EstaAbierto, Activo, FechaRegistro) VALUES
    (1, 1, 1, 'Plaza Central UIDE', '02-111-2222', 1, 1, GETDATE()),
    (2, 1, 2, 'Bloque de Aulas UIDE', '02-111-2223', 1, 1, GETDATE()),
    (3, 1, 3, 'Facultad de Medicina UIDE', '02-111-2224', 1, 1, GETDATE()),
    (4, 1, 4, 'Edificio Administrativo UIDE', '02-111-2225', 1, 1, GETDATE()),
    (5, 1, 5, 'Cancha de Futbol UIDE', '02-111-2226', 1, 1, GETDATE()),
    (6, 1, 6, 'Bloque de Ingenieria UIDE', '02-111-2227', 1, 1, GETDATE()),
    (7, 1, 7, 'Biblioteca General UIDE', '02-111-2228', 1, 1, GETDATE()),
    (8, 1, 8, 'Edificio de Ciencias Tecnicas UIDE', '02-111-2229', 1, 1, GETDATE()),
    (9, 1, 9, 'Patio de Comidas UIDE', '02-111-2230', 1, 1, GETDATE());
GO
