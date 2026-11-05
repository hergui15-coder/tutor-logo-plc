# Base de conocimiento 3 — Catálogo de prácticas guiadas

Diez prácticas ordenadas por dificultad. Cada una trae enunciado, tabla de E/S, la
solución en bloques, los errores frecuentes y las preguntas socráticas que el asistente
debe usar **antes** de mostrar la solución.

> Regla para el asistente: la sección «Solución» de cada práctica es material de
> escalón 4. No se entrega hasta que el estudiante haya presentado un intento o haya
> trabajado los escalones anteriores.

---

## Práctica 1 — Arranque y paro de un motor con enclavamiento

**Nivel:** introductorio · **Bloques nuevos:** relé autoenclavador (RS)

**Enunciado.** Un motor trifásico arranca con un pulsador de marcha (NA) y se detiene con
un pulsador de paro (NC). Debe seguir funcionando aunque se suelte el pulsador de marcha.
El relé térmico detiene el motor y no permite rearranque automático.

**Tabla de E/S**

| Borne | Elemento | Tipo | Descripción |
|---|---|---|---|
| I1 | S1 | NA | Pulsador de marcha |
| I2 | S2 | NC | Pulsador de paro |
| I3 | F1 | NC | Contacto del relé térmico |
| Q1 | KM1 | — | Bobina del contactor principal |

**Preguntas antes de la solución**
1. Si el pulsador de marcha vuelve solo a su posición, ¿qué mantiene la bobina activada?
2. ¿Por qué el paro se cablea con contacto NC y no NA?
3. Si se corta el cable del pulsador de paro, ¿qué debe pasar con el motor?

**Solución**

| Bloque | Tipo | Entradas | Salida a |
|---|---|---|---|
| B001 | AND | I2, I3 | R de B002 (negado por NOT) |
| B002 | Relé autoenclavador (RS) | S = I1, R = B003 | Q1 |
| B003 | NOT | B001 | R de B002 |

Como el paro y el térmico se cablean NC, en reposo I2 e I3 están a 1. Al accionar
cualquiera de los dos, la señal cae a 0, el NOT la pone a 1 y resetea el biestable.

Alternativa más simple y equivalente, si se prefiere sin NOT: usar `NAND` con I2 e I3
directamente al Reset.

**Errores frecuentes**
- Usar un AND entre I1 y Q1 en lugar del RS: funciona, pero el estudiante debe entender
  que está reconstruyendo a mano la retención.
- Conectar el térmico al Set en vez del Reset.
- Olvidar que el paro debe tener prioridad sobre la marcha.

**Verificación en el simulador**
- Pulsar marcha y soltar: Q1 debe quedar activo.
- Pulsar paro: Q1 cae y no vuelve solo.
- Activar el térmico: Q1 cae; al desactivarlo, Q1 **no** debe volver.

---

## Práctica 2 — Inversión de giro con enclavamiento

**Nivel:** introductorio · **Bloques nuevos:** enclavamiento lógico, retardo a la conexión

**Enunciado.** Un motor gira en ambos sentidos. Dos pulsadores seleccionan el sentido y
un tercero detiene. Nunca deben activarse los dos contactores a la vez. El cambio de
sentido exige pasar por paro y esperar 2 segundos antes de arrancar en sentido contrario.

**Tabla de E/S**

| Borne | Elemento | Tipo | Descripción |
|---|---|---|---|
| I1 | S1 | NA | Marcha sentido horario |
| I2 | S2 | NA | Marcha sentido antihorario |
| I3 | S3 | NC | Paro |
| I4 | F1 | NC | Relé térmico |
| Q1 | KM1 | — | Contactor sentido horario |
| Q2 | KM2 | — | Contactor sentido antihorario |

**Advertencia de seguridad obligatoria.** El enclavamiento en el programa no basta. Los
contactos auxiliares NC de KM1 y KM2 deben cruzarse en el cableado de las bobinas. Si un
contacto de potencia se queda pegado o el LOGO! falla, el cableado es lo único que evita
el cortocircuito entre dos fases.

**Preguntas antes de la solución**
1. ¿Qué pasa si el estudiante presiona los dos pulsadores de marcha simultáneamente?
2. ¿Por qué se exige un tiempo muerto entre sentidos, si eléctricamente el enclavamiento
   ya lo impide?

**Solución (esquema de bloques)**

| Bloque | Tipo | Entradas | Salida a |
|---|---|---|---|
| B001 | Relé autoenclavador | S = I1, R = B005 | B003 |
| B002 | Relé autoenclavador | S = I2, R = B005 | B004 |
| B003 | AND | B001, NOT(Q2), B007 | Q1 |
| B004 | AND | B002, NOT(Q1), B007 | Q2 |
| B005 | NAND | I3, I4 | R de B001 y B002 |
| B006 | OR | Q1, Q2 | B007 |
| B007 | Retardo a la desconexión, T = 2 s, negado | B006 | B003, B004 |

La rama B006–B007 crea el tiempo muerto: mientras alguna salida estuvo activa en los
últimos 2 segundos, ninguna puede activarse.

**Errores frecuentes**
- Enclavar solo por programa y no por hardware. Es el error grave de esta práctica.
- Tomar el enclavamiento de la marca interna en lugar de la salida real Q.
- Usar retardo a la conexión donde corresponde retardo a la desconexión.

---

## Práctica 3 — Arranque estrella-triángulo

**Nivel:** intermedio · **Bloques nuevos:** secuencia de temporizadores, tiempo de transición

**Enunciado.** Motor trifásico con arranque estrella-triángulo. Al pulsar marcha, se
cierran el contactor de línea (KM1) y el de estrella (KM3). Tras 5 segundos se abre KM3,
se espera 100 ms de tiempo muerto y se cierra el de triángulo (KM2). El paro abre todo.

**Tabla de E/S**

| Borne | Elemento | Tipo | Descripción |
|---|---|---|---|
| I1 | S1 | NA | Marcha |
| I2 | S2 | NC | Paro |
| I3 | F1 | NC | Relé térmico |
| Q1 | KM1 | — | Contactor de línea |
| Q2 | KM2 | — | Contactor de triángulo |
| Q3 | KM3 | — | Contactor de estrella |

**Preguntas antes de la solución**
1. ¿Para qué sirve el arranque estrella-triángulo? ¿Qué reduce y a costa de qué?
2. ¿Por qué hace falta un tiempo muerto de 100 ms entre estrella y triángulo?
3. ¿Qué ocurriría si KM2 y KM3 cerraran a la vez?

**Solución**

| Bloque | Tipo | Parámetros | Entradas | Salida a |
|---|---|---|---|---|
| B001 | Relé autoenclavador | Reset prioritario | S = I1, R = B002 | Q1 y B003 |
| B002 | NAND | — | I2, I3 | R de B001 |
| B003 | Retardo a la conexión | T = 5 s | B001 | B004, B006 |
| B004 | NOT | — | B003 | B005 |
| B005 | AND | — | B001, B004 | Q3 (estrella) |
| B006 | Retardo a la conexión | T = 0,1 s | B003 | B007 |
| B007 | AND | — | B006, B001, NOT(Q3) | Q2 (triángulo) |

**Errores frecuentes**
- Omitir el tiempo muerto: los dos contactores se solapan y se produce cortocircuito.
- Alimentar la estrella desde el temporizador en lugar de desde su negación.
- No cortar Q1 en el paro.

**Verificación en el simulador**
- Al pulsar marcha: Q1 y Q3 activos, Q2 en 0.
- A los 5 s: Q3 cae. A los 5,1 s: Q2 sube. Q1 permanece todo el tiempo.
- En ningún instante Q2 y Q3 deben estar simultáneamente a 1.

---

## Práctica 4 — Semáforo de cruce de dos vías

**Nivel:** intermedio · **Bloques nuevos:** cadena de temporizadores, marca de arranque M8

**Enunciado.** Cruce de dos vías. Verde de la vía A 20 s, ámbar 3 s, rojo mientras la vía
B tiene verde 20 s y ámbar 3 s. El ciclo se repite. Al energizar, el sistema debe partir
siempre en un estado conocido.

**Tabla de E/S**

| Borne | Elemento | Descripción |
|---|---|---|
| Q1 | Verde vía A | |
| Q2 | Ámbar vía A | |
| Q3 | Rojo vía A | |
| Q4 | Verde vía B | |
| Q5 | Ámbar vía B | |
| Q6 | Rojo vía B | |

**Preguntas antes de la solución**
1. ¿Cuántos estados distintos tiene el sistema? Dibújelos en una línea de tiempo.
2. ¿Qué luces están encendidas en cada estado? Complete la tabla antes de tocar bloques.
3. Al energizar el tablero, ¿en qué estado arranca? ¿Cómo lo garantiza?

**Enfoque de la solución.** Cadena de cuatro retardos a la conexión encadenados
(20 s → 3 s → 20 s → 3 s), con el último reiniciando al primero, y la marca M8 forzando
el arranque en el estado 1. Cada salida se activa con un AND entre el estado actual y la
negación del siguiente.

Es la primera práctica donde conviene que el estudiante llene la **tabla de estados**
antes de programar. Si no la hace, se pierde.

**Errores frecuentes**
- Programar luz por luz en lugar de por estados: el programa se vuelve inmanejable.
- Olvidar M8 y quedar con el semáforo en un estado indefinido al energizar.
- No cerrar el ciclo, con lo que el semáforo se queda en la última fase.

---

## Práctica 5 — Control de nivel de un tanque

**Nivel:** intermedio · **Bloques nuevos:** lógica con dos sensores de nivel

**Enunciado.** Un tanque tiene dos sensores tipo boya: nivel bajo (I1) y nivel alto (I2).
Cuando el nivel baja del mínimo, arranca la bomba de llenado (Q1) y se mantiene hasta que
se alcanza el nivel alto. Si la bomba trabaja más de 10 minutos seguidos, se detiene y se
enciende una alarma (Q2) por posible fuga o falla.

**Preguntas antes de la solución**
1. ¿Por qué no basta con un solo sensor? ¿Qué pasaría si la bomba conmutara en un único
   punto?
2. ¿Qué bloque le da al sistema la "memoria" de que debe seguir llenando aunque el
   sensor bajo ya no esté activo?
3. La alarma por tiempo excesivo, ¿debe poder reponerse sola o requiere intervención?

**Enfoque de la solución.** Relé autoenclavador con S = sensor bajo y R = sensor alto,
salida a Q1. En paralelo, un retardo a la conexión de 10 min alimentado por Q1: su salida
resetea el biestable y activa un segundo biestable que enciende la alarma, reponible solo
con un pulsador de rearme.

**Errores frecuentes**
- Usar un AND entre los dos sensores en lugar de un biestable: la bomba oscila.
- No prever el rearme manual de la alarma.
- Invertir la lógica de las boyas (verificar si el contacto es NA o NC en reposo).

---

## Práctica 6 — Contador de piezas en cinta transportadora

**Nivel:** intermedio · **Bloques nuevos:** contador adelante/atrás, textos de aviso

**Enunciado.** Un sensor fotoeléctrico (I1) detecta piezas sobre una cinta. Al llegar a
50 piezas, la cinta se detiene y se enciende una señal de lote completo. Un pulsador de
rearme (I2) pone el contador a cero y reanuda la marcha. El display debe mostrar la
cuenta actual.

**Enfoque de la solución.** Contador adelante/atrás con umbral de activación en 50,
entrada de conteo desde I1 y Reset desde I2. Un bloque de texto de aviso muestra el valor
actual del contador en el display del equipo.

**Errores frecuentes**
- No filtrar rebotes del sensor: el contador salta de dos en dos. Se resuelve con un
  retardo a la conexión corto o con el propio filtro del bloque.
- Confundir el umbral de activación con el de desactivación.

---

## Práctica 7 — Alumbrado de escalera con preaviso

**Nivel:** básico-intermedio · **Bloques nuevos:** interruptor de alumbrado para escalera

**Enunciado.** Pulsadores en tres pisos encienden la luz de la escalera. La luz permanece
3 minutos y, 30 segundos antes de apagarse, parpadea como aviso. Cualquier pulsación
reinicia el conteo.

**Enfoque de la solución.** OR de los tres pulsadores al bloque de alumbrado para
escalera, con tiempo 3 min y preaviso 30 s. Es la práctica que muestra el valor de las
funciones especiales: lo que en lógica cableada exige varios temporizadores, aquí es un
solo bloque parametrizado.

---

## Práctica 8 — Puerta de garaje automática

**Nivel:** intermedio-avanzado · **Bloques nuevos:** relé de impulsos, finales de carrera

**Enunciado.** Un pulsador único (I1) abre y cierra la puerta alternadamente. Finales de
carrera de puerta abierta (I2) y cerrada (I3) detienen el motor. Una barrera fotoeléctrica
(I4) invierte el movimiento si detecta un obstáculo durante el cierre. Q1 abre, Q2 cierra.

**Preguntas antes de la solución**
1. ¿Qué bloque permite que un mismo pulsador haga dos cosas distintas según el estado?
2. Si la barrera se activa mientras la puerta abre, ¿debe hacer algo?
3. ¿Qué pasa si se pulsa el botón con la puerta a media carrera?

**Errores frecuentes**
- No enclavar Q1 y Q2 (misma advertencia de seguridad que en la práctica 2).
- Que la barrera invierta también durante la apertura, lo que bloquea la puerta.

---

## Práctica 9 — Control de temperatura con sonda Pt100

**Nivel:** avanzado · **Bloques nuevos:** módulo AM2 RTD, conmutador analógico de umbral, escalado

**Enunciado.** Una sonda Pt100 conectada a un módulo AM2 RTD mide la temperatura de un
horno. La resistencia calefactora (Q1) se activa por debajo de 60 °C y se desactiva a
65 °C. Por encima de 80 °C se dispara una alarma (Q2) y se corta la calefacción.

**Enfoque de la solución.** Conmutador analógico de valor umbral sobre AI1 con umbral de
conexión 60 °C y de desconexión 65 °C (histéresis). Un segundo conmutador con umbral
80 °C activa la alarma y, negado, entra en el AND de la calefacción.

**Punto de enseñanza.** Aquí se explica la **histéresis**: si se usara un solo umbral, la
resistencia conmutaría continuamente alrededor del punto de consigna, con desgaste del
contactor. La diferencia entre umbral de conexión y desconexión es el concepto central.

**Errores frecuentes**
- Programar un único umbral sin histéresis.
- Confundir el valor interno (0–1000) con la unidad de ingeniería: hay que revisar el
  escalado del bloque.
- Suponer que el AM2 RTD acepta cualquier sonda; es específico para Pt100/Pt1000.

---

## Práctica 10 — Secuencia de tres cintas transportadoras

**Nivel:** avanzado · **Bloques nuevos:** secuenciación, retardo a la desconexión en cascada

**Enunciado.** Tres cintas en serie (C1 alimenta a C2, y C2 a C3). Al arrancar, la última
cinta parte primero y las anteriores se incorporan cada 3 segundos hacia atrás, para que
ninguna reciba material sin estar en marcha. Al parar, se detienen en orden inverso, con
5 segundos entre cada una, para vaciar el material en tránsito.

**Preguntas antes de la solución**
1. ¿Por qué arrancan de la última a la primera y paran de la primera a la última?
2. ¿Qué bloque mantiene una cinta funcionando después de que se ordenó el paro?

**Enfoque de la solución.** Para el arranque, cadena de retardos a la conexión. Para el
paro, cadena de retardos a la desconexión. Es la práctica que integra todo lo anterior y
suele funcionar bien como evaluación final del módulo.

---

## Cómo debe usar el asistente este catálogo

1. Si el estudiante nombra una práctica, empieza por las preguntas, no por la tabla.
2. Si el estudiante presenta un enunciado nuevo, lo compara con la práctica más parecida
   de este catálogo y reutiliza el enfoque, sin copiar la solución.
3. Si el estudiante pide "una práctica para repasar temporizadores", propone la 3 o la 7
   según el nivel que haya mostrado.
4. Los errores frecuentes de cada práctica son la fuente de las preguntas de diagnóstico
   cuando un programa no funciona.
