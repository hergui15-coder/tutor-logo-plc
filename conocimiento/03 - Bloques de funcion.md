# Base de conocimiento 2 — Bloques de función del LOGO!

Referencia de los bloques disponibles en LOGO! Soft Comfort, con el criterio de cuándo
usar cada uno. Nomenclatura del manual en español de Siemens.

---

## 1. Constantes y bornes (Co)

| Elemento | Uso |
|---|---|
| Entrada I | Señal física de un pulsador, final de carrera, sensor |
| Entrada analógica AI | Señal 0–10 V o 0/4–20 mA |
| Salida Q | Bobina de contactor, lámpara, electroválvula |
| Salida analógica AQ | Consigna a variador, válvula proporcional |
| Marca M | Relé interno, sin borne físico |
| Marca analógica AM | Almacena un valor analógico intermedio |
| Nivel Hi / Lo | 1 o 0 permanente. Útil para forzar entradas no usadas |
| Salida abierta X | Cierra una rama que no va a ningún borne |
| Tecla de cursor C | Botones del frente del equipo usados como entradas |
| Entradas/salidas de red NI, NQ | Comunicación entre varios LOGO! por Ethernet |

## 2. Funciones básicas (GF)

Son las compuertas lógicas. Todo programa se construye sobre ellas.

| Bloque | Salida a 1 cuando… | Equivalente en lógica cableada |
|---|---|---|
| AND | todas las entradas están a 1 | contactos en serie |
| AND con evaluación de flanco | todas a 1 **y** en el ciclo anterior no lo estaban | — |
| NAND | al menos una entrada está a 0 | contactos NC en paralelo |
| NAND con evaluación de flanco | transición de todas-a-1 a alguna-a-0 | — |
| OR | al menos una entrada está a 1 | contactos en paralelo |
| NOR | ninguna entrada está a 1 | contactos NC en serie |
| XOR | las dos entradas son distintas | conmutación de dos vías |
| NOT | la entrada está a 0 | contacto NC |

**Regla práctica:** las entradas no utilizadas de un bloque AND deben quedar a `Hi`, y
las de un bloque OR a `Lo`. LOGO! Soft Comfort lo hace por defecto, pero conviene que el
estudiante sepa por qué.

## 3. Funciones especiales de tiempo (SF)

| Bloque | Qué hace | Cuándo se usa |
|---|---|---|
| Retardo a la conexión | La salida se activa T después de que la entrada se pone a 1 | Arranque estrella-triángulo, ventilador que espera antes de arrancar |
| Retardo a la desconexión | La salida se desactiva T después de que la entrada cae a 0 | Extractor que sigue funcionando tras apagar la luz |
| Retardo a la conexión y desconexión | Combina ambos, con tiempos independientes | Filtrado de señales inestables |
| Retardo a la conexión con memoria | Basta un impulso en Trg para iniciar el conteo | Arranque por pulsador, no por interruptor |
| Relé de barrido (salida de impulsos) | La salida dura un tiempo fijo aunque la entrada siga a 1 | Impulso de arranque, avance de un paso |
| Relé de barrido activado por flancos | Impulso de duración definida ante un flanco | Sincronización de secuencias |
| Generador de impulsos asíncrono | Genera un tren de pulsos con tiempo de marcha y paro ajustables | Baliza intermitente, sirena |
| Generador aleatorio | Conmuta en un tiempo aleatorio dentro de un rango | Simulación de presencia en edificios |
| Interruptor de alumbrado para escalera | Enciende y apaga tras T, con preaviso | Iluminación de pasillos |
| Interruptor bifuncional | Pulso corto = temporizado; pulso largo = permanente | Alumbrado con dos modos |
| Temporizador semanal | Conmuta según día de la semana y hora | Horarios de iluminación, riego |
| Temporizador anual | Conmuta según fecha | Calefacción por temporada |
| Reloj astronómico | Conmuta con la salida y puesta del sol según ubicación | Alumbrado exterior |
| Cronómetro | Mide tiempo transcurrido entre dos eventos | Medición de ciclos |

Los temporizadores semanal, anual y astronómico requieren un modelo con reloj integrado
(la `C` del nombre: 12/24 **RC**E, 230 **RC**E).

## 4. Funciones especiales de conteo

| Bloque | Qué hace |
|---|---|
| Contador adelante/atrás | Cuenta impulsos en ambos sentidos, con umbrales de activación y desactivación |
| Contador de horas de servicio | Acumula horas de funcionamiento; sirve para mantenimiento preventivo |
| Interruptor de valor umbral | Cuenta impulsos por unidad de tiempo: mide frecuencia |

## 5. Funciones especiales analógicas

| Bloque | Qué hace |
|---|---|
| Comparador analógico | Compara la diferencia entre dos entradas analógicas con umbrales |
| Conmutador analógico de valor umbral | Activa la salida cuando la entrada supera un umbral, con histéresis |
| Amplificador analógico | Escala una entrada analógica (ganancia y offset) |
| Vigilancia de valor analógico | Vigila que un valor se mantenga dentro de una banda respecto a un valor memorizado |
| Interruptor analógico diferencial | Conmuta por umbral y diferencia |
| Multiplexor analógico | Selecciona entre cuatro valores predefinidos |
| Rampa | Lleva la salida de un valor a otro de forma gradual |
| Regulador PI | Control proporcional-integral de lazo cerrado |
| Modulación de ancho de pulso (PWM) | Convierte un valor analógico en una salida digital modulada |
| Instrucción aritmética | Realiza operaciones con hasta cuatro operandos |
| Filtro analógico | Suaviza señales ruidosas |
| Máx/Mín | Registra el valor máximo o mínimo alcanzado |
| Valor medio | Promedia la señal en una ventana de tiempo |

**Escalado — el punto donde más se equivocan:** el LOGO! representa internamente la
entrada analógica en el rango 0–1000 (0–10 V). Para convertir a unidades de ingeniería se
usa el amplificador analógico, o los parámetros de ganancia y offset del propio bloque:
valor real = (valor interno × ganancia) + offset.

Rangos admitidos (manual de sistema): **ganancia de −10,00 a +10,00, con dos decimales**;
offset de −10 000 a +10 000. La salida del amplificador va de −32 767 a 32 767, pero una
salida analógica física solo procesa 0–1000.

La ganancia no admite más de dos decimales, así que **no siempre se puede escalar
directamente a la unidad deseada**. Ejemplo: un sensor de nivel 0–10 V que corresponde a
0–5 metros necesitaría ganancia 0,005, que el bloque no acepta. Se trabaja en una unidad
más pequeña: ganancia 0,50 y offset 0 dan 0–500 **centímetros**. Si se quiere ver metros
en un texto de aviso, el parámetro p (número de decimales, 0 a 3) con p = 2 muestra 500
como 5.00; p solo cambia la visualización, no el valor.

Ejemplos del manual: termopar −30…+70 °C en 0–10 V → ganancia 0,1 y offset −30.
Presión 1000…5000 mbar en 0–10 V → ganancia 4 y offset 1000.

## 6. Funciones especiales varias

| Bloque | Qué hace | Cuándo se usa |
|---|---|---|
| **Relé autoenclavador (RS)** | Set/Reset con memoria | Marcha-paro con pulsadores. **Es el bloque más usado en prácticas de motores** |
| Relé de impulsos | Cambia de estado con cada impulso (biestable) | Un solo pulsador que enciende y apaga |
| Textos de aviso | Muestra mensajes en el display | Indicar estado o valores al operario |
| Interruptor de software | Interruptor virtual accionable desde el display o el servidor web | Modo manual/automático |
| Registro de desplazamiento | Desplaza bits en cada impulso | Secuenciadores, control de cintas en cascada |
| Detección de errores de instrucción aritmética | Señala división por cero o desbordamiento | Protección de cálculos |

### Sobre la prioridad Set/Reset

En el **relé autoenclavador** el **Reset tiene siempre prioridad**: si S = 1 y R = 1, la
salida se desactiva. No es configurable. Su único parámetro es la **remanencia** (`/` sin
remanencia, `R` remanente: tras un corte de alimentación recupera el estado anterior).

Para circuitos de motores esto importa: si el estudiante pulsa marcha y paro a la vez, el
motor debe quedar parado, y con el relé autoenclavador queda parado sin configurar nada.
Es una pregunta de examen habitual y una decisión de seguridad, no un detalle.

Sobre la remanencia en motores: con `R` activada, tras volver la energía el motor podría
arrancar solo. En circuitos de motores se deja **sin remanencia** salvo que haya una razón
justificada y se evalúe el riesgo.

No confundir con el **relé de impulsos**: ese sí tiene un parámetro de selección,
**RS** (la entrada R tiene prioridad) o **SR** (la entrada S tiene prioridad).

## 7. Correspondencia con la lógica cableada

Tabla útil para el estudiante que viene de esquemas de mando:

| Elemento del esquema eléctrico | Equivalente en el programa |
|---|---|
| Pulsador de marcha NA | Entrada I → Set del RS |
| Pulsador de paro NC | Entrada I → Reset del RS (negada si se cablea NC) |
| Contacto de retención (autoalimentación) | Lo hace el propio bloque RS |
| Bobina de contactor | Salida Q |
| Contacto auxiliar NA de un contactor | La misma salida Q usada como entrada del bloque |
| Enclavamiento entre contactores | AND con la salida contraria negada, **más** el enclavamiento por hardware |
| Temporizador neumático o electrónico | Retardo a la conexión |
| Relé térmico | Entrada I con contacto NC → Reset del RS |

## 8. Límites que conviene tener presentes

- LOGO! 8: máximo **400 bloques** por programa. Un programa de laboratorio típico usa
  entre 5 y 30, así que el límite rara vez se alcanza; pero conviene mencionarlo cuando
  el estudiante encadena bloques sin criterio.
- La profundidad de anidamiento y el número de entradas por bloque están limitados: si
  LOGO! Soft Comfort rechaza una conexión, casi siempre es por eso y se resuelve
  insertando una marca M intermedia.
- Los tiempos de los temporizadores admiten base de segundos, minutos u horas; el rango
  máximo depende de la base seleccionada.

## Fuentes

- Siemens, manual de sistema LOGO! y ayuda en pantalla de LOGO! Soft Comfort (edición en
  español). Escalado y relé autoenclavador verificados contra el *Manual de sistema LOGO!*,
  edición 7/2022, A5E33039720-AK: apartados 4.3.6, 4.4.22, 4.4.23 y 4.4.24.
- Siemens, catálogo de producto LOGO! 8.4.
