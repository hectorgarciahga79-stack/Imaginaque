# AMAZON SNIPER

Motor autónomo y propio para detectar **errores de precio** en Amazon.es (tarjetas gráficas, CPU, PCs y portátiles
gaming, consolas, Apple, OLED…). No usa Keepa, CamelCamelCamel, APIs de terceros ni webs de chollos: investiga
Amazon.es directamente, construye su propio historial y **solo avisa cuando algo supera 85 puntos y está verificado**.

> Lee primero [`docs/INVESTIGACION.md`](docs/INVESTIGACION.md): qué páginas de Amazon responden, qué bloquea Amazon,
> y la limitación legal (las Condiciones de Uso de Amazon no amparan la extracción automatizada).

```
engine/   Python: motor de investigación, memoria SQLite, SNIPER SCORE, verificación, daemon
web/      Next.js + Tailwind: panel privado (lee la misma base de datos)
deploy/   servicios para arrancar con el equipo (Linux systemd, macOS launchd, Windows)
data/     sniper.db (se crea sola), logs
```

## Instalación

Requisitos: Python 3.10+ y Node.js 20+. Ejecútalo **en un equipo en España** (tu PC o un mini-servidor siempre
encendido), no en un servidor en la nube: Amazon bloquea mucho más a las IP de centros de datos y los precios
cambian según la ubicación de entrega.

Linux / macOS:
```bash
cd amazon-sniper
./install.sh                 # dependencias + compila la web + registra servicios que arrancan solos
```
Windows (PowerShell):
```powershell
cd amazon-sniper
powershell -ExecutionPolicy Bypass -File deploy\windows\install.ps1
```
Sin servicios: `./install.sh --no-service` y luego `./start.sh`.

Panel privado: **http://127.0.0.1:3210** (pulsa "Activar notificaciones" una vez para recibir avisos del navegador).
Solo escucha en tu equipo. Si lo abres a tu red local, define `SNIPER_UI_PASSWORD` para exigir contraseña.

## Primer paso: diagnóstico real

```bash
cd engine && ../.venv/bin/python -m sniper doctor
```
Hace **una** petición real de cada tipo (listado, búsqueda, ficha) y te dice cuáles funcionan desde tu conexión.
Nada inventado: si Amazon rechaza algo, lo verás como `blocked`.

## Comandos del motor

```bash
python -m sniper supervise     # motor continuo con reinicio automático (lo que usan los servicios)
python -m sniper run           # motor continuo en primer plano
python -m sniper once -n 5     # 5 tareas de investigación y salir
python -m sniper status        # resumen de la base de datos y mejores anomalías
python -m sniper reset-blocks  # olvidar pausas por bloqueo (p. ej. tras cambiar de red)
python -m pytest -q            # tests (parsers sobre páginas reales guardadas + algoritmo + pipeline completo)
```

## Cómo funciona

1. **Investigación autónoma** (`engine.py`): cola persistente de tareas con prioridad.
   - Listados de *más vendidos*, *novedades* y *en alza* de Informática, Videojuegos y Electrónica. Del árbol de
     cada página descubre subcategorías nuevas y las prioriza (tarjetas gráficas 1, procesadores 2, PCs 3…).
   - ~150 búsquedas propias (RTX 5090, Ryzen 9, PS5 Pro, MacBook Pro M4, SSD 4TB…), combinaciones marca × modelo
     y búsquedas nuevas generadas a partir de los modelos que el motor va descubriendo. Las búsquedas que no
     aportan productos nuevos se espacian; ninguna se repite antes de su enfriamiento.
2. **Memoria propia**: cada precio observado (ASIN, título, modelo, precio, precio tachado, vendedor, enviado por,
   condición, stock, variante, URL, categoría, posición, ubicación de entrega, fecha).
3. **Identificación** (`catalog.py`): modelo exacto a partir del título y banderas antifalsos (accesorio, usado,
   reacondicionado, caja vacía, repuesto, videojuego, minería…).
4. **SNIPER SCORE** (`analysis.py`, 0–100): 10 factores ponderados — descuento frente al precio habitual observado
   (22), frente al mínimo histórico propio (8), ahorro en euros (8), frente a productos equivalentes (12), valor
   del producto (8), velocidad de la bajada (8), fiabilidad del vendedor (10), estado y stock (8), coherencia del
   producto (8), calidad de la información (8). Topes estrictos: descuento < 35 % → máx. 59; < 50 % → máx. 74;
   < 65 % → máx. 89; referencia solo estimada → máx. 88; "N ofertas desde" sin ficha → máx. 84.
   0–59 descartar · 60–74 interesante (se guarda) · 75–89 excepcional · 90–100 posible error extremo.
5. **Verificación inmediata**: vuelve a consultar la ficha (precio, vendedor, Amazon / tercero con envío de Amazon /
   tercero, stock, condición, variante, envío, modelo). Si cambió o desapareció → **expirada**, sin aviso.
6. **Avisos**: solo score > 85 + verificada. Notificación del sistema operativo y del navegador, sonido y fila en
   *Historial*. Sin servicios externos.

## Ajustes

Pestaña **Configuración** del panel (se guardan en la base de datos y el motor los aplica en su siguiente ciclo):
ritmo (por defecto una página cada 15–25 s y como mucho 120/h), umbrales, fuentes, profundidad de exploración…
El umbral de aviso no puede bajar de 85.

## Limitaciones conocidas

- Amazon limita el acceso automatizado; el motor lo detecta, se pausa y nunca lo elude. Si las fichas de producto
  quedan bloqueadas en tu conexión, las anomalías solo se verifican parcialmente y rara vez llegarán a avisar.
- El parser de **fichas de producto** y de **búsqueda** se ha escrito sobre el marcado público de Amazon; la búsqueda
  se validó con páginas reales, la ficha no se pudo descargar desde el entorno de desarrollo. `sniper doctor`
  lo comprueba en tu equipo.
- Las estimaciones de catálogo (`catalog.PRIOR_EUR`) son orientativas y solo se usan sin datos propios.
