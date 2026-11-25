# AMAZON SNIPER — Investigación técnica de viabilidad

Fecha de las pruebas: 25-11-2026. Todas las conclusiones salen de peticiones reales a `https://www.amazon.es`
hechas desde el contenedor de desarrollo (un centro de datos con IP de **Estados Unidos**). Las páginas reales
quedaron guardadas en `engine/tests/fixtures/` y los tests del parser trabajan sobre ellas.

## 1. Qué responde Amazon a un acceso automatizado

| Página | Ejemplo | Resultado real desde el centro de datos | Qué contiene |
|---|---|---|---|
| Más vendidos | `/gp/bestsellers/computers/937935031/` | **OK** al principio (HTTP 200, ~125 KB). Tras ~20 peticiones en pocos minutos, Amazon empezó a rechazarla | 30 productos por página (`?pg=2` da los siguientes 30): ASIN, título, imagen, precio, posición, aviso "N ofertas desde X €", árbol de subcategorías |
| Novedades | `/gp/new-releases/...` | **OK** | Igual que más vendidos (productos recién incorporados) |
| Productos en alza | `/gp/movers-and-shakers/...` | Rechazada | — |
| Búsqueda | `/s?k=RTX+5090` | **Intermitente**: primero 503, luego 5 búsquedas seguidas OK (48–49 resultados cada una) y después bloqueada otra vez | ASIN, título, precio, precio tachado, patrocinado, reacondicionado |
| Ficha de producto | `/dp/ASIN` | Rechazada (página intermedia con formulario de CAPTCHA) | Vendedor, "enviado por", stock, condición, variante, envío |
| Portada con navegador real (Chromium) | `/` | Desafío JavaScript de AWS WAF | — |

Las páginas de rechazo dicen literalmente: *"Para tratar el acceso automatizado a los datos de Amazon, ponte en
contacto con api-services-support@amazon.com… consulta nuestras API"*. El motor las reconoce (`fetcher.detect_block`)
y **no intenta eludirlas**: no resuelve CAPTCHA, no ejecuta el desafío WAF para conseguir el token, no rota IP ni
identidades, no inicia sesión. Pausa ese tipo de página con esperas crecientes (20 min → 1 h → 3 h → 6 h → 12 h)
y sigue con las fuentes que sí responden.

Es muy probable que desde una conexión doméstica española, a ritmo bajo, Amazon sirva búsquedas y fichas con
normalidad: el bloqueo observado depende de la reputación de la IP del centro de datos. **Esto no se ha podido
comprobar desde aquí**. Por eso existe `python -m sniper doctor`, que hace una prueba real de cada tipo de página
en el equipo donde se instale y dice qué funciona.

## 2. Ubicación de entrega e IVA

Cada página indica la ubicación de entrega (`#glow-ingress-line2`). Desde el centro de datos era
**"Estados Unidos"**, y los precios parecen ir sin IVA español (ej.: un DualSense a 45,37 € ≈ 54,90 € / 1,21).
Consecuencias en el diseño:

- cada observación guarda `geo`; el historial y los productos equivalentes **solo comparan precios de la misma ubicación**;
- el panel avisa cuando la ubicación no es España.

Precios reales vistos con esa ubicación: RTX 5090 entre **9.530 € y 21.142 €**, RTX 5080 entre 1.611 € y 3.779 €,
kits DDR5 de 32 GB a 429 €. Confirma que no se pueden usar precios "de referencia" fijos: el motor tiene que
aprender el precio habitual de sus propias observaciones.

## 3. robots.txt y condiciones de uso

- `robots.txt` (sección `User-agent: *`) **permite** `/s?k=`, `/dp/`, `/gp/bestsellers`, `/gp/new-releases` y prohíbe,
  entre otras, `/gp/offer-listing`, `/dp/product-availability/` y las búsquedas con varios filtros `p_` encadenados.
  El motor lo respeta (`respect_robots = true`) y nunca visita las rutas prohibidas.
- Las **Condiciones de Uso de Amazon** no incluyen en la licencia el uso de robots o herramientas de extracción
  de datos. Es decir: aunque `robots.txt` lo permita y el motor vaya despacio, **automatizar la consulta de
  Amazon.es choca con sus condiciones**. Esa es la limitación legal real del proyecto y la decisión es tuya.
  Riesgos realistas: bloqueos de IP temporales (ya observados). El motor **no usa ninguna cuenta**, así que no pone
  en riesgo una cuenta de Amazon.
- La vía que Amazon ofrece de forma explícita es su API oficial para afiliados (Product Advertising API), que exige
  una cuenta de afiliado con ventas. Es Amazon mismo (no un tercero) y la lógica de detección seguiría siendo la
  nuestra, pero tú la excluiste como fuente. Si algún día quieres usarla, encaja como un `fetch_backend` más; no
  está implementada.

## 4. Identificación de productos (ASIN y variantes)

- **ASIN**: identificador de 10 caracteres. En listados viene en `id` / `data-asin`; en enlaces, en `/dp/ASIN`.
  La URL canónica es `https://www.amazon.es/dp/ASIN`.
- **Variantes**: cada variante (memoria, color, capacidad) tiene su propio ASIN, así que el historial por ASIN ya
  separa variantes. El modelo exacto se extrae del título (`catalog.identify`): `gpu:rtx-5090`, `gpu:rtx-5060-ti-16gb`,
  `cpu:ryzen-9-9950x3d`, `console:ps5-pro`, `laptop:rtx-5090`… Para modelos donde la memoria cambia el precio
  (5060 Ti 8/16 GB, 9060 XT) la memoria forma parte de la clave. En la ficha se guarda además la variante
  seleccionada (`#twister .selection`).
- Probado sobre 90 títulos reales: distingue tarjetas de **soportes anti-sag** ("Soporte para Tarjeta Gráfica"),
  mandos DualSense de consolas, juegos "(PS5)" de consolas, portátiles con RTX de tarjetas RTX, lectores de DVD
  "compatibles con MacBook" de MacBooks.

## 5. Verificar precios y evitar falsos positivos

- **Precio tachado / recomendado**: se guarda (`list_price`) pero **nunca** se usa como referencia.
- **"N ofertas desde X €"** en listados: es la oferta más barata de varias y puede ser usada o de terceros. Se marca
  (`offers_from`) y su score queda limitado a 84 (no notifica) hasta verificarla en la ficha.
- **Precio de listado normal**: es la oferta destacada (buy box), que Amazon solo da a ofertas nuevas y comprables;
  aun así, vendedor y condición quedan "sin confirmar" hasta ver la ficha.
- **Verificación inmediata**: cualquier anomalía con ≥ 50 % de descuento sobre referencia propia, o score ≥ 75,
  se vuelve a consultar al momento: primero la ficha (precio, vendedor, vendido/enviado por Amazon o terceros,
  stock, condición, variante, envío, modelo coherente); si Amazon no deja ver la ficha, se relee el listado donde
  apareció (verificación **parcial**). Si el precio desapareció o cambió, la oferta se marca **expirada** y no se avisa.
  Las ofertas vivas se recomprueban cada 15 min.

## 6. Historial propio

SQLite (`data/sniper.db`): `products`, `observations` (cada precio visto con fecha, fuente, vendedor, condición,
stock, ubicación, posición), `opportunities`, `verifications`, `alerts`, `tasks` (cola persistente), `categories`
(árbol descubierto), `fetch_log`. El "precio habitual" es la mediana de las observaciones propias del ASIN; si aún
no hay suficientes, la mediana actual de los **productos equivalentes** (mismo modelo, otros ASIN) que el motor ha
visto; y solo en último recurso una estimación de catálogo marcada como tal (confianza BAJA, score máx. 88).

## 7. Funcionamiento continuo

Proceso Python independiente (`python -m sniper supervise`) con: cola de tareas persistente en SQLite, bloqueo de
instancia única, latido cada pocos segundos, reinicio automático con espera exponencial si el proceso cae (probado
matando el proceso con SIGKILL: reinicio en 5 s), límite de peticiones por hora y pausa entre peticiones, y
servicios del sistema operativo para arrancar con el equipo (systemd, launchd, Programador de tareas de Windows).
No necesita Claude Code abierto.

## 8. Conclusión

- **Viable** construir el motor propio: descubrimiento por categorías y novedades, búsquedas propias, memoria de
  precios, puntuación y verificación funcionan con datos reales de Amazon.es.
- **Limitación principal**: Amazon decide cuánto acceso automatizado tolera. Desde un centro de datos, búsqueda y
  fichas se bloquean rápido; desde una conexión doméstica española, a ritmo bajo, previsiblemente mucho menos
  (por comprobar con `sniper doctor`). Sin ficha de producto, una anomalía solo puede verificarse parcialmente y
  normalmente no llegará a los 85 puntos necesarios para avisar: es preferible a avisar de algo no comprobado.
- **Dónde ejecutarlo**: en tu ordenador o un mini-servidor en casa, en España, siempre encendido. No en un servidor
  en la nube.
