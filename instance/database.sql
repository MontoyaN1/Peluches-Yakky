BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "product" (
	"id"	INTEGER NOT NULL,
	"product_name"	VARCHAR(100) NOT NULL,
	"current_price"	INTEGER NOT NULL,
	"precio_costo"	INTEGER NOT NULL,
	"previous_price"	INTEGER NOT NULL,
	"in_stock"	INTEGER NOT NULL,
	"product_picture"	VARCHAR(1000) NOT NULL,
	"flash_sale"	BOOLEAN,
	"date_added"	DATETIME,
	"descripcion"	VARCHAR(1000) NOT NULL,
	"is_deleted"	BOOLEAN,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "rol" (
	"id_rol"	INTEGER NOT NULL,
	"nombre_rol"	VARCHAR(100) NOT NULL,
	PRIMARY KEY("id_rol")
);
CREATE TABLE IF NOT EXISTS "cart" (
	"id"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"customer_link"	INTEGER NOT NULL,
	"product_link"	INTEGER NOT NULL,
	FOREIGN KEY("customer_link") REFERENCES "customer"("id"),
	FOREIGN KEY("product_link") REFERENCES "product"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "order" (
	"id"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"price"	FLOAT NOT NULL,
	"status"	VARCHAR(100),
	"payment_id"	VARCHAR(1000),
	"address"	VARCHAR(1000) NOT NULL,
	"phone"	VARCHAR(20) NOT NULL,
	"forma_pago"	VARCHAR(20) NOT NULL,
	"fecha_creacion"	DATETIME,
	"customer_link"	INTEGER NOT NULL,
	"product_link"	INTEGER NOT NULL,
	FOREIGN KEY("customer_link") REFERENCES "customer"("id"),
	FOREIGN KEY("product_link") REFERENCES "product"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "interacciones" (
	"id_interaccion"	INTEGER NOT NULL,
	"id_contacto"	INTEGER NOT NULL,
	"id_oportunidad"	INTEGER,
	"id_agente"	INTEGER NOT NULL,
	"id_actividad"	INTEGER,
	"tipo_interaccion"	VARCHAR(50) NOT NULL,
	"descripcion"	TEXT NOT NULL,
	"resultado"	VARCHAR(100),
	"fecha_interaccion"	DATETIME NOT NULL,
	FOREIGN KEY("id_agente") REFERENCES "customer"("id"),
	PRIMARY KEY("id_interaccion"),
	FOREIGN KEY("id_contacto") REFERENCES "contactos"("id_contacto"),
	FOREIGN KEY("id_oportunidad") REFERENCES "oportunidades"("id_oportunidad"),
	FOREIGN KEY("id_actividad") REFERENCES "actividades"("id_actividad")
);
CREATE TABLE IF NOT EXISTS "oportunidades" (
	"id_oportunidad"	INTEGER NOT NULL,
	"id_contacto"	INTEGER NOT NULL,
	"id_cliente"	INTEGER,
	"id_agente"	INTEGER NOT NULL,
	"titulo"	VARCHAR(150) NOT NULL,
	"valor_estimado"	DECIMAL(10, 2),
	"etapa"	VARCHAR(50) DEFAULT 'Prospecto',
	"probabilidad"	INTEGER,
	"fecha_creacion"	DATETIME,
	"fecha_cierre"	DATETIME,
	"descripcion"	TEXT,
	PRIMARY KEY("id_oportunidad"),
	FOREIGN KEY("id_contacto") REFERENCES "contactos"("id_contacto"),
	FOREIGN KEY("id_cliente") REFERENCES "customer"("id"),
	FOREIGN KEY("id_agente") REFERENCES "customer"("id")
);
CREATE TABLE IF NOT EXISTS "actividades" (
	"id_actividad"	INTEGER NOT NULL,
	"id_contacto"	INTEGER NOT NULL,
	"id_oportunidad"	INTEGER,
	"id_agente"	INTEGER NOT NULL,
	"tipo_actividad"	VARCHAR(50) NOT NULL,
	"titulo"	VARCHAR(200) NOT NULL,
	"descripcion"	TEXT,
	"fecha_programada"	DATETIME NOT NULL,
	"estado"	VARCHAR(50) DEFAULT 'Pendiente',
	"fecha_creacion"	DATETIME,
	"fecha_completada"	DATETIME,
	PRIMARY KEY("id_actividad"),
	FOREIGN KEY("id_agente") REFERENCES "customer"("id"),
	FOREIGN KEY("id_oportunidad") REFERENCES "oportunidades"("id_oportunidad"),
	FOREIGN KEY("id_contacto") REFERENCES "contactos"("id_contacto")
);
CREATE TABLE IF NOT EXISTS "customer" (
	"id"	INTEGER NOT NULL,
	"rol_id"	INTEGER,
	"email"	VARCHAR(100),
	"username"	VARCHAR(100),
	"password_hash"	VARCHAR(150),
	"date_joined"	DATETIME,
	"active"	BOOLEAN DEFAULT 'True',
	"telefono"	INTEGER,
	UNIQUE("email"),
	FOREIGN KEY("rol_id") REFERENCES "rol"("id_rol"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "contactos" (
	"id_contacto"	INTEGER NOT NULL,
	"id_agente"	INTEGER NOT NULL,
	"nombre"	VARCHAR(100) NOT NULL,
	"email"	VARCHAR(150) NOT NULL,
	"telefono"	VARCHAR(20),
	"empresa"	VARCHAR(100) DEFAULT 'Independiente',
	"canal"	VARCHAR(50),
	"estado"	VARCHAR(50) DEFAULT 'Nuevo',
	"fecha_registro"	DATETIME,
	"fecha_actulizar"	DATETIME,
	"satisfaccion"	INTEGER DEFAULT 0,
	UNIQUE("email"),
	FOREIGN KEY("id_agente") REFERENCES "customer"("id"),
	PRIMARY KEY("id_contacto")
);
INSERT INTO "product" ("id","product_name","current_price","precio_costo","previous_price","in_stock","product_picture","flash_sale","date_added","descripcion","is_deleted") VALUES (1,'Papa Noel',45000,20000,60000,34,'media/1759631888.354693_1755463076.536121_papa_noel.png',1,'2025-10-05 02:38:08.358363','repisa de Papa Noel',0),
 (2,'Muñeco de nieve mediano',34000,15000,50000,23,'media/1759631948.361812_1755463033.067524_muneco_nieve_faro.png',1,'2025-10-05 02:39:08.363705','Repísa de muñeco de nieve mediano',0),
 (3,'Muñeco de nieve grande',50000,30000,65000,26,'media/1759631997.756934_1755548377.966533_muneco_nieve_faro_grande.png',1,'2025-10-05 02:39:57.759212','Repisa de muñeco de nieve grande',0),
 (4,'Pesebre en domo',55000,30000,70000,37,'media/1759632054.97634_1755637665.101188_pesebre_domo.png',1,'2025-10-05 02:40:54.977416','Repisa de pesebre dentro de un domo de vidrió',0),
 (5,'Reno navideño',55000,28000,68000,15,'media/1759632102.318513_1758054315.904478_1755475074.392591_reno_decoracion.png',1,'2025-10-05 02:41:42.319596','Repisa de reno navideño',0);
INSERT INTO "rol" ("id_rol","nombre_rol") VALUES (1,'administrador'),
 (2,'empleado'),
 (3,'cliente');
INSERT INTO "interacciones" ("id_interaccion","id_contacto","id_oportunidad","id_agente","id_actividad","tipo_interaccion","descripcion","resultado","fecha_interaccion") VALUES (1,4,6,2,NULL,'Mensaje','Cliente preguntó por precios','Es posible que compre','2025-09-30 20:41:41.756377'),
 (2,4,6,2,NULL,'Mensaje','Cliente preguntó por precios','Es posible que compre','2025-09-30 20:43:50.229378'),
 (3,4,6,2,NULL,'Mensaje','Cliente preguntó por precios','Es posible que compre','2025-09-30 20:44:07.836672');
INSERT INTO "oportunidades" ("id_oportunidad","id_contacto","id_cliente","id_agente","titulo","valor_estimado","etapa","probabilidad","fecha_creacion","fecha_cierre","descripcion") VALUES (1,3,NULL,2,'Oferta de peluches',2.5,'Propuesta',50,'2025-09-29 03:27:49.728009',NULL,'Cliente pregunta por ofertas de peluches'),
 (2,3,NULL,2,'Oferta de peluches',2.5,'Propuesta',50,'2025-09-29 03:28:53.975097',NULL,'Cliente pregunta por ofertas de peluches'),
 (3,3,NULL,2,'Oferta de peluches',2.5,'Prospecto',50,'2025-09-29 03:30:43.815813',NULL,'Cliente pregunta por ofertas de peluches'),
 (4,3,NULL,2,'Oferta de peluches',2.5,'Propuesta',50,'2025-09-29 03:33:45.261069',NULL,'Cliente pregunta por ofertas de peluches'),
 (5,3,NULL,2,'Oferta de peluches',2.5,'Prospecto',50,'2025-09-29 03:34:00.196504',NULL,'Cliente pregunta por ofertas de peluches'),
 (6,4,NULL,2,'Ofrecer descuentos navideños',4,'Propuesta',70,'2025-09-30 20:25:53.872527',NULL,'Cliente preguntó por precios de productos navideños');
INSERT INTO "actividades" ("id_actividad","id_contacto","id_oportunidad","id_agente","tipo_actividad","titulo","descripcion","fecha_programada","estado","fecha_creacion","fecha_completada") VALUES (1,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-09-29 12:00:00.000000','Pendiente','2025-09-29 03:58:56.709115',NULL),
 (2,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-26 16:00:00.000000','En seguimiento','2025-09-29 03:59:28.914426',NULL),
 (3,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-17 18:00:00.000000','Pendiente','2025-09-29 04:11:27.801896',NULL),
 (4,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-09-30 12:00:00.000000',NULL,'2025-09-29 04:25:38.680432',NULL),
 (5,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-10 16:00:00.000000',NULL,'2025-09-29 04:25:47.082785',NULL),
 (6,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-07 12:00:00.000000',NULL,'2025-09-29 04:26:03.299785',NULL),
 (7,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-09-05 17:00:00.000000',NULL,'2025-09-29 04:48:39.260930',NULL),
 (8,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-03 15:00:00.000000',NULL,'2025-09-29 04:49:22.099350',NULL),
 (9,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-10-03 14:00:00.000000',NULL,'2025-09-29 04:49:40.388225',NULL),
 (10,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-09-03 14:00:00.000000',NULL,'2025-09-29 04:50:16.972230',NULL),
 (11,3,5,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Se hará llamada al cliente','2025-09-02 17:00:00.000000',NULL,'2025-09-29 04:51:19.091774',NULL),
 (12,4,6,2,'Ofrecer ofertas','Llama para ofrecer productos de temporada','Se va realizar una llamada para ofrecer productos','2025-10-02 17:00:00.000000','Completado','2025-09-30 20:27:44.763748','2025-10-01 00:21:37.334423'),
 (13,4,6,2,'Ofrecer ofertas','Llama para ofrecer productos','Se va realizar una llamada para ofrecer productos','2025-10-02 17:00:00.000000','Completado','2025-09-30 20:32:22.570644','2025-10-01 01:38:50.173334'),
 (14,4,6,2,'Ofrecer ofertas','Llama para ofrecer productos','Se va realizar una llamada para ofrecer productos','2025-10-02 17:00:00.000000','Completado','2025-09-30 20:33:39.060568','2025-10-01 01:39:05.061054'),
 (15,4,6,2,'Ofrecer ofertas','Llama para ofrecer productos','Se va realizar una llamada para ofrecer productos','2025-10-02 17:00:00.000000','Completado','2025-09-30 20:36:28.016716','2025-10-01 01:51:01.672869'),
 (16,4,6,2,'Ofrecer ofertas','Llama para ofrecer productos','Se va realizar una llamada para ofrecer productos','2025-10-01 16:00:00.000000','Pendiente','2025-09-30 20:37:26.885035',NULL),
 (17,4,6,2,'Ofrecer ofertas','Ofrecer descuentos navideños','Cliente preguntó por precios','2025-10-01 16:00:00.000000','Pendiente','2025-09-30 20:41:19.070993',NULL);
INSERT INTO "customer" ("id","rol_id","email","username","password_hash","date_joined","active","telefono") VALUES (1,1,'admin@peluchesyakky.com','Admin','pbkdf2:sha256:600000$Ewj25RHtE2vSFhvM$96ebfa30734f7f692fdf174a42b1d7630ef3f479186af2ef52bbb4f44ba2cef1','2025-09-28 19:36:25.255133','True',NULL),
 (2,2,'juanpablomontoyajpmv@gmail.com','Juan Pablo','pbkdf2:sha256:600000$boXSBIcWYHP8Imls$e0eddcbdc0986d62bf480b4a300c2757775cd178d46e5cc4601cf4d42e7ad602','2025-09-28 20:53:52.441938','True',NULL);
INSERT INTO "contactos" ("id_contacto","id_agente","nombre","email","telefono","empresa","canal","estado","fecha_registro","fecha_actulizar","satisfaccion") VALUES (1,2,'Wilson','wilson@correo.com','3026265537','Independiente','Llamada','En seguimiento','2025-09-29 00:46:51.212855','2025-10-01 19:28:36.128629',2),
 (2,2,'Pablo','pablo@correo.com','23423434','Independiente','Mensaje','En seguimiento','2025-09-29 03:13:03.709071','2025-10-01 19:28:28.455951',4),
 (3,2,'Prueba','prueba2@correo.com','23423434','Independiente','Mensaje','Nuevo','2025-09-29 03:14:32.019024','2025-10-01 19:28:14.110081',3),
 (4,2,'Juan','juanpablomontoyajpmv@gmail.com','3135484798','Independiente','Correo','Nuevo','2025-09-30 20:23:35.885160','2025-10-01 19:28:05.241453',4);
COMMIT;
