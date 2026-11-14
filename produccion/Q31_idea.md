# Q31 · ¿Y si pudieras vender tus recuerdos? — propuesta (prueba de generación de ideas)

Estado: **idea + guion, sin producir**. No se ha gastado voz ni se ha escrito en la Bandeja.

- **Origen:** idea 14 de `series.json → independientes.lista_hector` («Puedes vender tus recuerdos»). Comprobada con `scripts/cola.py --titulo`: no existe en la Bandeja.
- **Por qué ahora (estrategia v11):** premisa de DINERO en segunda persona con una cifra que escala (100 € → 1.000.000 €), que es lo único que ha roto en el canal. Categoría «dinero»: no repite la del último ¿Y si…? (Q30, «sociedad»).
- **Formato:** B · mini historia con protagonista (TÚ), objetivo 61–66 s, 3D de bloques (`anim3d/`, plantilla `shots_t1.py`), voz Juanjo Viral `30jLfQdV8RTduXvosh02`, una sola generación.
- **Gancho (0–2 s):** billete gigante de 100 € flotando sobre una cabeza de bloques con un recuerdo brillando dentro. Rótulo: «100 € POR UN RECUERDO».
- **Dato real:** capacidad de la memoria humana ≈ 2,5 petabytes, *estimación* del neurocientífico Paul Reber (Scientific American, «What Is the Memory Capacity of the Human Brain?»). Se dice como estimación, porque hay quien discute la cifra.

## Guion etiquetado (voz animada; sin etiquetas de susurro)

[excited] ¡Te ofrecen cien euros por un recuerdo! Uno solo: tu primer día de colegio. ¿Lo vendes? [energetic] ¡Lo vendes! Firmas, te tocan la frente... y desaparece. Ni lo echas de menos. [amazed] Al día siguiente te ofrecen mil por tu primer beso. ¡Y diez mil por el verano en que aprendiste a nadar! [excited] Los ricos pagan fortunas por vivir recuerdos ajenos, y tu cerebro guarda, según una estimación, unos dos coma cinco petabytes. ¡Eres una mina de oro! [enthusiastic] En un mes tienes un millón. Coche, casa, viajes... [excited] ¡Y sigues vendiendo! Tu cumpleaños de los diez, tu primera bici, la voz de tu abuelo. [dramatic] Pero algo falla. Tu madre te llama llorando y no sabes por qué. Tu mejor amigo te cuenta un chiste de hace años... y no te ríes. [serious] ¡Has vendido quién eres! [dramatic] Entonces lees la letra pequeña: puedes recomprar un recuerdo... ¡al triple de precio! [excited] Y solo te llega para uno. [dramatic] ¿Cuál recompras tú?

## Planos (3D de bloques)

| # | Plano | Movimiento | Texto en pantalla |
|---|---|---|---|
| 1 | Protagonista ante un mostrador futurista; billete de 100 € gigante | empuje rápido de cámara | 100 € POR UN RECUERDO |
| 2 | Recuerdo del colegio en una burbuja que sale de la cabeza | órbita | — |
| 3 | Casco con cables; la burbuja se apaga | golpe de zoom + vibración | VENDIDO |
| 4 | Precios que suben en un panel: 1.000 € · 10.000 € | travelling lateral | contador |
| 5 | Mansión de clientes ricos «probándose» recuerdos | grúa | — |
| 6 | Cerebro de vóxeles convertido en lingote | primer plano | ≈ 2,5 PB (estimación) |
| 7 | Montaje de lujo: coche, casa, avión; burbujas (tarta, bici, abuelo) que se apagan una tras otra | cortes cada 1 s | 1.000.000 € |
| 8 | Madre llorando al teléfono; el protagonista no la reconoce | plano y contraplano | — |
| 9 | Amigo riendo; el protagonista serio | cámara lenta | — |
| 10 | Contrato con letra pequeña ampliada con lupa | zoom | RECOMPRA ×3 |
| 11 | Tres burbujas de recuerdos y monedas que solo alcanzan para una | órbita final | ¿CUÁL RECOMPRAS TÚ? |

- **Caption:** ¿Venderías tus recuerdos por 100 €? Empieza fácil… hasta que tu madre te llama 💸 ¿Cuál recomprarías tú?
- **Hashtags:** #imaginaque #quepasariasi #historias #dinero #curiosidades #ysi
- **Coste previsto:** ≈ 1.000–1.150 créditos de voz (una generación). Render ≈ 15–20 min aquí (~1 s por fotograma en 2 procesos).
