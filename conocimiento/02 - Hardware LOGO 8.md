# Base de conocimiento 1 — Hardware del LOGO! 8

Documento de referencia para el asistente. Datos tomados del catálogo y la
documentación de producto de Siemens.

---

## 1. Qué es el LOGO!

Módulo lógico compacto de Siemens, situado por debajo de la gama SIMATIC S7-1200. Se
usa para automatizaciones pequeñas: instalaciones de edificios, máquinas simples,
prácticas de laboratorio. Sustituye a la lógica cableada de relés, temporizadores y
contadores por una lógica programada en un solo dispositivo de carril DIN.

Frente a la lógica cableada, un cambio en la secuencia se hace modificando el programa,
no recableando el tablero. Esa es la idea que el estudiante debe entender antes que
cualquier bloque.

## 2. Módulos básicos LOGO! 8.4

Todos los módulos básicos de la generación 8 traen puerto Ethernet integrado y servidor
web. Existen en versión con pantalla (LCD de 6 líneas) y versión *Pure*, sin pantalla.

| Modelo | Referencia (con display) | Alimentación | Entradas digitales | De ellas, aptas como analógicas | Salidas |
|---|---|---|---|---|---|
| LOGO! 24 CE | 6ED1052-1CC08-0BA2 | 24 V DC | 8 | 4 | 4 transistor, 0,3 A |
| LOGO! 12/24 RCE | 6ED1052-1MD08-0BA2 | 12…24 V DC | 8 | 4 | 4 relé, 10 A |
| LOGO! 24 RCE | 6ED1052-1HB08-0BA2 | 24 V AC/DC | 8 | — | 4 relé, 10 A |
| LOGO! 230 RCE | 6ED1052-1FB08-0BA2 | 115…230 V AC/DC | 8 | — | 4 relé, 10 A |

Las versiones sin pantalla llevan referencia `6ED1052-2…`.

**Cómo leer el nombre del modelo:**

- El número indica la tensión de alimentación (24, 12/24, 230).
- `R` = salidas por relé (sin R, salidas por transistor).
- `C` = reloj integrado (temporizadores semanal y anual).
- `E` = Ethernet.
- El sufijo `0BA2` corresponde a la versión 8.4 del hardware.

**Dato que se confunde con frecuencia:** solo los modelos de 12/24 V DC y 24 V DC
admiten entradas analógicas en I1, I2, I7 e I8 (allí llamadas AI3, AI4, AI1 y AI2). Los
modelos de 24 V AC/DC y 230 V no tienen entradas analógicas integradas: necesitan un
módulo AM2.

## 3. Capacidad máxima del sistema

| Concepto | LOGO! 8 | LOGO! 9 (desde abril de 2026) |
|---|---|---|
| Bloques por programa | 400 | 800 |
| Entradas digitales | 24 | 64 |
| Salidas digitales | 20 | 60 |
| Entradas analógicas | 8 | 16 |
| Salidas analógicas | 8 | 16 |
| Pantalla del módulo base | LCD 6 líneas, monocromo | Táctil a color 320 × 240 px |
| Software | LOGO! Soft Comfort V8.x | LOGO! Soft Comfort V9 |

En los laboratorios el equipo habitual sigue siendo LOGO! 8. Al citar límites, decir
siempre a qué generación corresponden.

## 4. Módulos de ampliación

| Módulo | Función |
|---|---|
| DM8 | 4 entradas + 4 salidas digitales |
| DM16 | 8 entradas + 8 salidas digitales |
| AM2 | 2 entradas analógicas (0–10 V o 0/4–20 mA) |
| AM2 RTD | 2 entradas para sondas de temperatura Pt100 / Pt1000 |
| AM2 AQ | 2 salidas analógicas (0–10 V o 0/4–20 mA) |
| CMR 2040 / CMR 2020 | Comunicación móvil (GSM/LTE) y GPS |
| CSM | Switch Ethernet de 4 puertos |
| CMK2000 | Pasarela KNX para instalaciones de edificios |
| TDE | Display de texto externo, montaje en puerta de tablero |

Los módulos se acoplan a la derecha del módulo básico y se numeran en cascada: las
entradas del primer DM8 continúan la numeración (I9…I12) y así sucesivamente.

## 5. Direccionamiento

| Identificador | Qué representa | Rango en LOGO! 8 |
|---|---|---|
| I | Entrada digital | I1 … I24 |
| AI | Entrada analógica | AI1 … AI8 |
| Q | Salida digital | Q1 … Q20 |
| AQ | Salida analógica | AQ1 … AQ8 |
| M | Marca (relé interno) | M1 … M64 |
| AM | Marca analógica | AM1 … AM64 |
| NI / NQ | Entradas y salidas de red (Ethernet) | NI1…NI64 / NQ1…NQ64 |
| X | Salida abierta (no conectada) | X1 … X64 |
| Lo / Hi | Nivel lógico fijo 0 / 1 | — |

**Marcas con función especial:**

- **M8 — marca de arranque.** Está a 1 únicamente durante el primer ciclo tras el
  arranque del LOGO!. Se usa para inicializar estados. Es la respuesta a "¿cómo hago
  que algo se ponga en una posición conocida al encender?".
- **M25 / M26** — retroiluminación del display (blanca / del TDE).
- **M27** — juego de caracteres del mensaje.
- **M28 / M29 / M30 / M31** — retroiluminación en ámbar y rojo.

## 6. Software: LOGO! Soft Comfort

Entorno de programación para PC. La versión correspondiente al hardware 8.4 es
**LOGO! Soft Comfort V8.4** (referencia 6ED1058-0BA08-0YA1). Existe versión de
demostración con funcionalidad limitada de descarga al equipo.

Ofrece dos lenguajes de programación:

- **FUP (FBD)** — diagrama de funciones. Bloques lógicos conectados por líneas. Es el
  lenguaje nativo del LOGO! y el más usado en su programación.
- **KOP (LAD)** — esquema de contactos. Se parece al esquema eléctrico de mando
  tradicional, por lo que a un estudiante que viene de lógica cableada le resulta más
  intuitivo al principio.

Adicionalmente permite crear **UDF** (bloques definidos por el usuario): un conjunto de
bloques encapsulado y reutilizable, útil cuando la misma lógica se repite.

Incluye **simulación** integrada: permite accionar entradas virtuales y ver el estado de
salidas y temporizadores sin conectar el equipo. Es donde el estudiante debe probar todo
antes de descargar al hardware.

## 7. Programación desde el propio equipo

En los modelos con display se puede programar directamente con los seis botones del
frente, navegando por el menú. Es lento y solo se justifica para modificaciones puntuales
en campo. Para aprendizaje se usa siempre LOGO! Soft Comfort.

Secuencia de menú habitual: `► Programa` → `Editar` → `Editar programa`. Para poner en
marcha: `► Start`.

## 8. Errores frecuentes de los estudiantes con el hardware

1. **Confundir el borne de entrada con el común.** Las entradas del LOGO! DC comparten
   el borne común; conectar la señal al común deja la entrada permanentemente a 1.
2. **Alimentar un LOGO! 230 RCE con 24 V** (no enciende) o un 12/24 RCE con 230 V
   (lo destruye). La tensión está impresa en el frente; verificarla es el primer paso.
3. **Cablear un motor trifásico directo a la salida de relé.** La salida conmuta la
   bobina del contactor, no la carga de potencia.
4. **Usar un pulsador NA para el paro.** El paro y el térmico se cablean NC, de modo que
   una rotura de conductor detenga el sistema en lugar de dejarlo funcionando.
5. **Suponer que el enclavamiento del programa basta.** El enclavamiento por contactos
   auxiliares NC entre contactores es obligatorio y adicional.
6. **Olvidar el común de las salidas de relé.** Las salidas están agrupadas por bornes
   comunes independientes; cada grupo necesita su alimentación.

## Fuentes

- Siemens, *LOGO! — Logic Modules for Everyday Automation* y *LOGO! Basic Modules*.
- Siemens, folleto *Everything about the LOGO! world* (LOGO! 8.4, referencias MLFB).
- Siemens, nota de prensa de presentación de LOGO! 9 (9 de marzo de 2026;
  disponibilidad 1 de abril de 2026).
