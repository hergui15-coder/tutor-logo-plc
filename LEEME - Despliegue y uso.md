# Tutor Virtual LOGO! — despliegue y uso

Aplicación del estudio *Desarrollo e implementación de un asistente virtual para el
aprendizaje de automatización industrial utilizando PLC LOGO! Siemens*.
IST «Carlos Cisneros» · Carrera de Electromecánica.

---

## Antes que nada: revoque la clave anterior

La versión previa de `app.py` tenía la clave de la API escrita dentro del código, y existe
un archivo `clave API.txt` en la carpeta del proyecto. **Esa clave debe considerarse
comprometida.**

1. Entre a <https://aistudio.google.com/apikey>, elimine la clave anterior y genere una nueva.
2. Ponga la nueva clave únicamente en `secrets.toml` (ver más abajo). Nunca dentro de `app.py`.
3. Borre `clave API.txt`.

---

## Qué cambió respecto de la versión anterior

| Antes | Ahora | Por qué |
|---|---|---|
| Clave dentro de `app.py` | Solo en `secrets.toml`, y la app se detiene si falta | Evita exponerla al desplegar |
| El estudiante elegía «Guiado» o «Directo» | Modo fijo, lo decide el docente en `secrets.toml` | Si el estudiante puede pedir la solución, el estudio deja de medir lo que declara el diseño |
| Prompt de tres líneas, sin base de conocimiento | Instrucciones completas de `instrucciones_tutor.md` + los tres archivos de `conocimiento/` | Es el asistente que se valida con los expertos; el anterior era otro |
| Identificación por nombre | Código de estudiante, con formato validado | La anonimización es una exigencia ética del diseño |
| Sin consentimiento | Pantalla de consentimiento informado antes del chat | Exigencia ética y editorial |
| El registro se perdía al cerrar la pestaña | Se escribe fila a fila en hoja de cálculo o en CSV local | Es la variable «intensidad de uso» del estudio |
| `requirements.txt.txt` vacío | `requirements.txt` con las dependencias | Sin esto no despliega |

---

## Estructura de la carpeta

```
tutor_logo_plc/
├─ app.py                          la aplicación
├─ instrucciones_tutor.md          instrucciones del tutor (las validadas)
├─ conocimiento/                   base de conocimiento (.md)
│   ├─ 02 - Hardware LOGO 8.md
│   ├─ 03 - Bloques de funcion.md
│   └─ 04 - Practicas guiadas.md
├─ registro/                       CSV de respaldo (se crea solo)
├─ requirements.txt
├─ .gitignore
└─ .streamlit/
    └─ secrets.toml.ejemplo        copiar como secrets.toml y completar
```

**No edite `instrucciones_tutor.md` una vez que los expertos hayan validado el asistente.**
Cualquier cambio posterior invalida esa validación y debe repetirse.

---

## Uso local (una máquina del laboratorio)

```bash
cd tutor_logo_plc
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .streamlit\secrets.toml.ejemplo .streamlit\secrets.toml
notepad .streamlit\secrets.toml   # pegue la clave nueva
streamlit run app.py
```

Se abre en <http://localhost:8501>. El registro queda en `registro/interacciones.csv`,
que abre directamente en Excel.

Limitación: solo sirve si todos los estudiantes usan esa máquina. Para uso desde la casa,
despliegue en la nube.

---

## Despliegue en Streamlit Community Cloud (gratuito)

1. Cree un repositorio en GitHub con esta carpeta. **Verifique que `.gitignore` esté
   incluido**, para que no se suban `secrets.toml` ni la carpeta `registro/`.
2. Entre a <https://share.streamlit.io>, conecte el repositorio y elija `app.py`.
3. En **Settings › Secrets**, pegue el contenido de su `secrets.toml`.
4. Despliegue y comparta el enlace con los estudiantes del grupo experimental.

En la nube el sistema de archivos es efímero: **el CSV local se borra en cada reinicio**.
Para desplegar en la nube hay que configurar Supabase (o la hoja de cálculo): sin eso, los
datos del estudio se pierden.

Secretos que se pegan en *Settings › Secrets* (formato TOML, uno por línea):

```toml
GEMINI_API_KEY = "la clave nueva de Google AI Studio"
MODELO = "gemini-3.6-flash"
MODO_TUTOR = "guiado"
SUPABASE_URL = "https://xxxxxxxx.supabase.co"
SUPABASE_KEY = "la clave publishable o anon"
```

Los códigos válidos son `4A-01` a `4A-17` (estudiantes) y `PRUEBA-01` a `PRUEBA-99`
(docente y expertos, se excluyen del análisis). Si hace falta otra lista, se añade
`CODIGOS_VALIDOS = "4A-01,4A-02,..."`.

### Dos avisos del plan gratuito

- **Supabase pausa los proyectos gratuitos después de unos días sin actividad.** Si se
  pausa, las consultas de los estudiantes no se guardan (en la nube el respaldo CSV se
  pierde). Entre en el panel de Supabase al menos una vez por semana y revise que el
  proyecto esté activo, sobre todo en vacaciones de fin de año. La app avisa al estudiante
  si el registro falla.
- **Gemini API en el nivel gratuito:** Google puede usar el contenido de las consultas para
  mejorar sus productos, y los límites de consultas por minuto y por día son bajos para un
  curso entero. Con la facturación activada en Google AI Studio (nivel de pago), el
  contenido no se usa para entrenar y los límites suben; el costo con 17 estudiantes es
  bajo. Decida antes del 23 de noviembre y declárelo en el artículo.

---

## Registro en Supabase (destino principal, recomendado)

Supabase es una base de datos PostgreSQL gratuita en la nube, con panel web. Es lo que
conviene para el estudio: no tiene límite práctico de filas, los datos salen como tabla
real y se exportan a CSV para Excel, SPSS o R.

1. Cree una cuenta en <https://supabase.com> y un proyecto nuevo (plan gratuito).
   Guarde la contraseña de la base que le pide al crearlo.
2. Abra **SQL Editor › New query**, pegue todo el contenido de `supabase_tablas.sql`
   y pulse **Run**. Eso crea las dos tablas y las reglas de seguridad.
3. Copie dos datos:
   - el **Project URL** (en *Project Settings › Data API*) → `SUPABASE_URL`
   - la clave pública (en *Project Settings › API Keys*): la **publishable**
     (`sb_publishable_…`) o, en proyectos antiguos, la **anon** (`eyJ…`) → `SUPABASE_KEY`.
     La app acepta las dos y rechaza las claves secretas.
4. Péguelas en `.streamlit/secrets.toml` (o en *Settings › Secrets* de Streamlit Cloud),
   sin el `#` del inicio de la línea.

**Use la clave publishable o `anon`, nunca la secreta (`sb_secret_…` o `service_role`).** Con las políticas del archivo SQL, la
aplicación solo puede *insertar* filas: no puede leer, modificar ni borrar. Así, aunque la
clave se filtrara, nadie podría descargar las conversaciones de los estudiantes. Usted las
consulta desde el panel de Supabase, que entra con su propia cuenta.

Para ver los datos: **Table Editor › interacciones**. Para exportar: el botón *Export* de
esa misma pantalla. Al final de `supabase_tablas.sql` hay dos consultas ya escritas —una
calcula la intensidad de uso por estudiante, que es la variable moderadora del estudio, y
otra la distribución del uso por semana—; se pegan en el SQL Editor cuando tenga datos.

---

## Registro en Google Sheets (alternativa)

1. Cree una hoja nueva en Google Sheets. El `SHEET_ID` es la parte larga de la URL:
   `docs.google.com/spreadsheets/d/`**`ESTE_TROZO`**`/edit`.
2. En <https://console.cloud.google.com>: cree un proyecto, habilite **Google Sheets API**
   y **Google Drive API**, y cree una **cuenta de servicio** con una clave en formato JSON.
3. Comparta la hoja con el `client_email` de esa cuenta de servicio, con permiso de
   **Editor**.
4. Pegue el contenido del JSON en `secrets.toml` bajo `[gcp_service_account]`, y añada
   `SHEET_ID`.

La app crea sola dos pestañas: `interacciones` y `consentimientos`.

---

## Los datos que quedan registrados

Hoja `interacciones`, una fila por consulta:

`fecha_hora · codigo_estudiante · curso · paralelo · id_sesion · n_interaccion ·
minutos_sesion · modelo · modo · caracteres_pregunta · caracteres_respuesta ·
pregunta · respuesta`

Con eso se calcula directamente la variable **intensidad de uso** del diseño metodológico:
número de consultas por estudiante, número de sesiones distintas (`id_sesion`), tiempo
acumulado y distribución a lo largo de las ocho semanas. Y el texto de las consultas da
material cualitativo para la discusión: qué temas generaron más dudas.

Esto convierte una limitación declarada del estudio —autorreporte de la intensidad de
uso— en un registro objetivo. Conviene decirlo explícitamente en el apartado de
materiales y métodos: es una ventaja frente a los estudios que usan un chatbot comercial
compartido.

---

## Antes de aplicar con estudiantes

- [ ] Clave anterior revocada y `clave API.txt` borrado
- [ ] Registro probado: hacer dos consultas y comprobar que aparecen las filas
- [ ] Prueba del andamiaje: pedir «quiero programar un arranque estrella-triángulo» y
      verificar que **no** entrega el programa, sino que pregunta. Si lo entrega, revise
      que `instrucciones_tutor.md` se esté cargando y que `MODO_TUTOR` sea `guiado`
- [ ] Códigos de estudiante asignados y entregados (`4A-01` a `4A-17`), con la lista
      código↔nombre guardada aparte y solo en poder del docente
- [ ] Modelo y fechas anotados para el apartado de materiales y métodos:
      modelo `gemini-3.6-flash`, período del 23 / 11 / 2026 al 14 / 01 / 2027
- [ ] Prueba desde un celular con datos móviles (no con la red del instituto)
- [ ] Respuestas del banco de 40 consultas generadas y guardadas **antes** del 23 de
      noviembre; la calificación de los expertos puede llegar después (ver el plan `09`)
- [ ] Filas de prueba borradas de Supabase antes del primer uso real, o identificadas por el
      código `PRUEBA-xx`
