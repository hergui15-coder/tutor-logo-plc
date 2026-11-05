# -*- coding: utf-8 -*-
"""
Tutor Virtual LOGO! Siemens
Instituto Superior Tecnologico "Carlos Cisneros" - Carrera de Electromecanica

Asistente conversacional para el aprendizaje de automatizacion industrial con
PLC LOGO! de Siemens, con registro persistente de interacciones para la
investigacion cuasiexperimental descrita en el archivo 05 del proyecto.

Reglas de diseno que NO deben modificarse sin recalcular la validez del estudio:
  - Las instrucciones del tutor son las validadas por juicio de expertos y viven
    en 'instrucciones_tutor.md'. Editarlas invalida esa validacion.
  - El modo pedagogico es fijo y no lo elige el estudiante.
  - El estudiante se identifica por codigo, nunca por nombre.
  - El modelo se fija a una version estable y se registra en cada interaccion.
"""

import csv
import re
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# CONFIGURACION GENERAL
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).parent
DIR_CONOCIMIENTO = RAIZ / "conocimiento"
DIR_REGISTRO = RAIZ / "registro"
ARCHIVO_INSTRUCCIONES = RAIZ / "instrucciones_tutor.md"

CSV_INTERACCIONES = DIR_REGISTRO / "interacciones.csv"
CSV_CONSENTIMIENTOS = DIR_REGISTRO / "consentimientos.csv"

# Version del modelo fijada para el periodo de aplicacion. NO usar alias del
# tipo 'gemini-flash-latest': cambiaria de modelo a mitad del estudio y el
# articulo dejaria de ser replicable.
MODELO_POR_DEFECTO = "gemini-3.6-flash"

# Hora local de Ecuador (el servidor de Streamlit Cloud trabaja en UTC).
ZONA_HORARIA = ZoneInfo("America/Guayaquil")


def ahora() -> datetime:
    """Fecha y hora actuales de Ecuador, sin zona (para restar y formatear)."""
    return datetime.now(ZONA_HORARIA).replace(tzinfo=None)


# Grupo de aplicacion del estudio y codigos de participante.
#   Estudiantes: 4A-01 ... 4A-17 (Automatizacion Industrial, TSU 4A)
#   Pruebas del docente/expertos: PRUEBA-01 ... PRUEBA-99 (se excluyen del analisis)
# La lista exacta puede fijarse en Secrets con CODIGOS_VALIDOS = "4A-01,4A-02,..."
ASIGNATURA = "Automatización Industrial"
PARALELO_ESTUDIO = "4A"
TOTAL_ESTUDIANTES = 17
PATRON_PRUEBA = r"PRUEBA-\d{2}"

# Datos del docente responsable. Aparecen en la interfaz y en el consentimiento
# informado: el participante debe saber a quien dirigirse. Los estudiantes son
# anonimos en el registro; el investigador responsable no.
DOCENTE = "Lic. Guido Hernán Cantuña Adriano, Mg."
DOCENTE_CARGO = "Docente de Automatización Industrial y PLC · Carrera de Electromecánica"
DOCENTE_CORREO = "guido.cantuna@istcarloscisneros.edu.ec"
INSTITUCION = "Instituto Superior Tecnológico «Carlos Cisneros» · Riobamba, Ecuador"

# Turnos de conversacion que se envian como contexto al modelo.
MAX_TURNOS_CONTEXTO = 20

CAMPOS_INTERACCION = [
    "fecha_hora", "codigo_estudiante", "curso", "paralelo", "id_sesion",
    "n_interaccion", "minutos_sesion", "modelo", "modo",
    "caracteres_pregunta", "caracteres_respuesta", "pregunta", "respuesta",
]
CAMPOS_CONSENTIMIENTO = [
    "fecha_hora", "codigo_estudiante", "curso", "paralelo", "id_sesion", "acepto",
]

TEXTO_CONSENTIMIENTO = f"""
**Consentimiento informado**

Usted va a utilizar un asistente virtual desarrollado como parte de un estudio
sobre el aprendizaje de automatización industrial en el {INSTITUCION.split(' · ')[0]}.

**Investigador responsable:** {DOCENTE} — {DOCENTE_CARGO}.
Para cualquier consulta sobre el estudio puede escribir a {DOCENTE_CORREO}.

- Se registrarán sus consultas al asistente, las respuestas recibidas, la fecha
  y el tiempo de uso, **identificados únicamente con el código que le asignó el
  docente**. En ningún momento se registra su nombre.
- Los datos se usan solo con fines de investigación y se reportan de forma
  agregada. Nadie fuera del equipo de investigación accede a las conversaciones
  individuales.
- **Su participación es voluntaria y no afecta su calificación.** Puede dejar de
  usar el asistente en cualquier momento sin dar explicaciones y sin
  consecuencia académica alguna.
- Todos los estudiantes del paralelo 4A de Automatización Industrial usan el
  mismo asistente, en las mismas condiciones. Al terminar el estudio, el
  asistente seguirá disponible para los estudiantes de la carrera de
  Electromecánica.

Si tiene dudas, consúltelas con el docente antes de continuar.
"""

st.set_page_config(
    page_title="Tutor Virtual LOGO! Siemens",
    page_icon="LOGO",
    layout="wide",
)


# ---------------------------------------------------------------------------
# CARGA DE INSTRUCCIONES Y BASE DE CONOCIMIENTO
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cargar_instrucciones() -> str:
    """Instrucciones del tutor: el texto validado por juicio de expertos."""
    if not ARCHIVO_INSTRUCCIONES.exists():
        return ""
    return ARCHIVO_INSTRUCCIONES.read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def cargar_conocimiento() -> tuple[str, list[str]]:
    """Concatena los archivos .md de la carpeta 'conocimiento'."""
    if not DIR_CONOCIMIENTO.exists():
        return "", []
    partes, nombres = [], []
    for archivo in sorted(DIR_CONOCIMIENTO.glob("*.md")):
        partes.append(
            f"\n\n===== INICIO DEL DOCUMENTO: {archivo.stem} =====\n"
            + archivo.read_text(encoding="utf-8")
            + f"\n===== FIN DEL DOCUMENTO: {archivo.stem} =====\n"
        )
        nombres.append(archivo.stem)
    return "".join(partes), nombres


def construir_instruccion_sistema(modo: str) -> str:
    instrucciones = cargar_instrucciones()
    conocimiento, _ = cargar_conocimiento()

    if modo == "directo":
        instrucciones += (
            "\n\nAJUSTE DE MODO (activado por el docente): responde de forma "
            "directa, con la solucion estructurada y su explicacion, sin exigir "
            "el recorrido por escalones."
        )

    if conocimiento:
        instrucciones += (
            "\n\n\nBASE DE CONOCIMIENTO\n\n"
            "Los documentos que siguen son tu fuente autorizada sobre el LOGO!. "
            "Consultalos antes de responder y da prioridad a lo que digan por "
            "encima de tu conocimiento general. No inventes datos que no esten "
            "aqui ni en el manual de Siemens.\n"
            + conocimiento
        )
    return instrucciones


# ---------------------------------------------------------------------------
# REGISTRO PERSISTENTE
#
# Orden de destinos: Supabase -> Google Sheets -> CSV local.
# El CSV local se escribe SIEMPRE como respaldo, aunque el destino principal
# haya funcionado: en un estudio, perder filas no tiene arreglo posterior.
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def config_supabase():
    """Devuelve {'url','key'} si Supabase esta configurado, o None."""
    try:
        url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
        key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
    except Exception:  # noqa: BLE001
        return None
    if not url or not key:
        return None
    return {"url": url, "key": key}


def guardar_supabase(tabla: str, fila: dict) -> bool:
    """Inserta una fila via API REST de Supabase (PostgREST)."""
    cfg = config_supabase()
    if cfg is None:
        return False
    try:
        import requests

        respuesta = requests.post(
            f"{cfg['url']}/rest/v1/{tabla}",
            headers={
                "apikey": cfg["key"],
                "Authorization": f"Bearer {cfg['key']}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json=fila,
            timeout=15,
        )
        if respuesta.status_code >= 300:
            st.session_state["error_supabase"] = (
                f"HTTP {respuesta.status_code}: {respuesta.text[:300]}"
            )
            return False
        return True
    except Exception as e:  # noqa: BLE001
        st.session_state["error_supabase"] = str(e)
        return False


@st.cache_resource(show_spinner=False)
def conectar_hoja():
    """Devuelve (hoja_interacciones, hoja_consentimientos) o (None, None)."""
    try:
        if "gcp_service_account" not in st.secrets or "SHEET_ID" not in st.secrets:
            return None, None
        import gspread

        cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        libro = cliente.open_by_key(st.secrets["SHEET_ID"])

        def _hoja(nombre, cabecera):
            try:
                h = libro.worksheet(nombre)
            except Exception:
                h = libro.add_worksheet(title=nombre, rows=2000, cols=len(cabecera))
            if not h.row_values(1):
                h.append_row(cabecera)
            return h

        return _hoja("interacciones", CAMPOS_INTERACCION), _hoja(
            "consentimientos", CAMPOS_CONSENTIMIENTO
        )
    except Exception as e:  # noqa: BLE001
        st.session_state["error_hoja"] = str(e)
        return None, None


def _guardar_csv(ruta: Path, campos: list[str], fila: dict) -> None:
    DIR_REGISTRO.mkdir(exist_ok=True)
    nuevo = not ruta.exists()
    with ruta.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


def registrar(tipo: str, fila: dict) -> str:
    """Escribe una fila. Devuelve el destino principal usado:
    'supabase', 'sheets', 'csv' o 'error'."""
    campos = CAMPOS_INTERACCION if tipo == "interaccion" else CAMPOS_CONSENTIMIENTO
    ruta = CSV_INTERACCIONES if tipo == "interaccion" else CSV_CONSENTIMIENTOS
    tabla = "interacciones" if tipo == "interaccion" else "consentimientos"

    destino = ""

    # 1. Destino principal: Supabase
    if guardar_supabase(tabla, fila):
        destino = "supabase"

    # 2. Alternativa: Google Sheets
    if not destino:
        hoja_i, hoja_c = conectar_hoja()
        hoja = hoja_i if tipo == "interaccion" else hoja_c
        if hoja is not None:
            try:
                hoja.append_row([str(fila.get(c, "")) for c in campos],
                                value_input_option="RAW")
                destino = "sheets"
            except Exception as e:  # noqa: BLE001
                st.session_state["error_hoja"] = str(e)

    # 3. CSV local: siempre, como respaldo y como ultimo recurso
    try:
        _guardar_csv(ruta, campos, fila)
        if not destino:
            destino = "csv"
    except Exception as e:  # noqa: BLE001
        st.session_state["error_registro"] = str(e)
        if not destino:
            destino = "error"

    return destino


# ---------------------------------------------------------------------------
# CLIENTE DEL MODELO
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def cliente_gemini(clave: str):
    return genai.Client(api_key=clave)


# Errores transitorios del servidor de Google: el modelo saturado (503),
# la cuota momentaneamente excedida (429) o un fallo interno (500/502/504).
# No son errores de la aplicacion y se resuelven reintentando.
SENALES_TRANSITORIAS = (
    "503", "500", "502", "504", "429",
    "UNAVAILABLE", "RESOURCE_EXHAUSTED", "INTERNAL", "DEADLINE_EXCEEDED",
    "overloaded", "high demand", "try again later",
)
ESPERAS = (1.5, 4.0, 9.0)  # segundos entre reintentos


class ModeloSaturado(Exception):
    """El servidor de Google no respondio tras varios reintentos."""


def _es_transitorio(e: Exception) -> bool:
    texto = str(e)
    return any(s.lower() in texto.lower() for s in SENALES_TRANSITORIAS)


def responder(clave: str, modelo: str, instruccion: str, historial: list[dict],
              pregunta: str) -> str:
    cliente = cliente_gemini(clave)
    contenidos = []
    for m in historial[-MAX_TURNOS_CONTEXTO:]:
        contenidos.append(
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])],
            )
        )
    contenidos.append(
        types.Content(role="user", parts=[types.Part.from_text(text=pregunta)])
    )
    config = types.GenerateContentConfig(system_instruction=instruccion)

    # El modelo NO cambia entre reintentos: el estudio exige que todas las
    # respuestas provengan de la misma version. Solo se reintenta.
    ultimo_error = None
    for intento in range(len(ESPERAS) + 1):
        try:
            respuesta = cliente.models.generate_content(
                model=modelo, contents=contenidos, config=config
            )
            texto = (respuesta.text or "").strip()
            return texto or "(El modelo no devolvió texto. Intente reformular la consulta.)"
        except Exception as e:  # noqa: BLE001
            ultimo_error = e
            if not _es_transitorio(e) or intento == len(ESPERAS):
                break
            time.sleep(ESPERAS[intento])

    if ultimo_error is not None and _es_transitorio(ultimo_error):
        raise ModeloSaturado(str(ultimo_error)) from ultimo_error
    raise ultimo_error  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ESTADO DE SESION
# ---------------------------------------------------------------------------

for clave_estado, valor in {
    "id_sesion": uuid.uuid4().hex[:12],
    "inicio_sesion": ahora(),
    "mensajes": [],
    "registro_sesion": [],
    "consentimiento": False,
    "identificado": False,
    "codigo": "",
    "curso": "",
    "paralelo": "",
    "destino_registro": "",
}.items():
    st.session_state.setdefault(clave_estado, valor)


# ---------------------------------------------------------------------------
# LECTURA DE CONFIGURACION
# ---------------------------------------------------------------------------

def leer_secreto(nombre: str, por_defecto=None):
    try:
        return st.secrets.get(nombre, por_defecto)
    except Exception:  # noqa: BLE001
        return por_defecto


API_KEY = leer_secreto("GEMINI_API_KEY", "")
MODELO = leer_secreto("MODELO", MODELO_POR_DEFECTO)
MODO = str(leer_secreto("MODO_TUTOR", "guiado")).strip().lower()
if MODO not in ("guiado", "directo"):
    MODO = "guiado"


# ---------------------------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------------------------

IMAGEN_ENCABEZADO = RAIZ / "recursos" / "encabezado_istcc.jpg"

ESTILOS = """
<style>
:root { --azul:#1E2A6E; --azul2:#2B4BA8; --verde:#3FD12A; --naranja:#F59E0B; --cian:#06B6D4; }
.block-container { padding-top: 1.2rem; }
.hero { background: linear-gradient(120deg, #1E2A6E 0%, #2B4BA8 55%, #0EA5A4 100%);
        border-radius: 18px; padding: 26px 28px; color: #fff; display:flex;
        align-items:center; gap: 22px; flex-wrap: wrap; margin: 6px 0 18px 0;
        box-shadow: 0 8px 24px rgba(30,42,110,.25); }
.hero-texto { flex: 1 1 320px; min-width: 260px; }
.hero h1 { color:#fff !important; font-size: 2.1rem; line-height:1.15; margin:0 0 6px 0; padding:0; }
.hero .chip { display:inline-block; background: rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.35);
        padding: 3px 12px; border-radius: 999px; font-size:.8rem; margin-bottom:10px; letter-spacing:.3px; }
.hero p { color: #E6ECFF; font-size: 1.02rem; margin: 6px 0 0 0; }
.hero-img { flex: 0 1 300px; max-width: 320px; width:100%; }
.tarjetas { display:grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 14px; margin: 4px 0 18px 0; }
.tarjeta { border-radius: 14px; padding: 16px 16px 14px 16px; color:#1f2937; border:1px solid rgba(0,0,0,.05); }
.tarjeta .ico { font-size: 1.7rem; }
.tarjeta b { display:block; font-size: 1.02rem; margin: 4px 0 4px 0; }
.tarjeta span { font-size: .9rem; color:#374151; }
.t1 { background:#E8FBE4; border-left: 6px solid #3FD12A; }
.t2 { background:#FFF4DB; border-left: 6px solid #F59E0B; }
.t3 { background:#E0F2FE; border-left: 6px solid #0EA5E9; }
.t4 { background:#F3E8FF; border-left: 6px solid #8B5CF6; }
.pasos { display:flex; gap:10px; flex-wrap:wrap; margin: 0 0 16px 0; }
.paso { flex: 1 1 180px; background:#fff; border:2px dashed #CBD5E1; border-radius: 12px; padding: 10px 12px; font-size:.92rem; color:#1f2937; }
.paso .n { display:inline-flex; width:26px; height:26px; border-radius:50%; background:#1E2A6E; color:#fff;
        align-items:center; justify-content:center; font-weight:700; margin-right:6px; }
.mini { background: linear-gradient(90deg,#1E2A6E,#2B4BA8); color:#fff; border-radius: 12px;
        padding: 10px 16px; margin-bottom: 10px; font-weight:600; }
.mini small { font-weight:400; color:#DCE4FF; }
@media (max-width: 640px) { .hero { padding: 18px; } .hero h1 { font-size: 1.6rem; } }
</style>
"""

# Ilustracion propia: modulo logico generico con un circuito de marcha-paro.
ILUSTRACION_SVG = """
<svg class="hero-img" viewBox="0 0 320 210" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Ilustración de un módulo lógico programable con entradas, salidas y un circuito de marcha y paro">
  <rect x="8" y="14" width="304" height="10" rx="3" fill="#94A3B8"/>
  <rect x="40" y="30" width="170" height="150" rx="12" fill="#F8FAFC"/>
  <rect x="40" y="30" width="170" height="28" rx="12" fill="#CBD5E1"/>
  <rect x="40" y="46" width="170" height="12" fill="#CBD5E1"/>
  <g fill="#1E2A6E">
    <circle cx="58" cy="44" r="4"/><circle cx="76" cy="44" r="4"/><circle cx="94" cy="44" r="4"/><circle cx="112" cy="44" r="4"/>
    <circle cx="130" cy="44" r="4"/><circle cx="148" cy="44" r="4"/><circle cx="166" cy="44" r="4"/><circle cx="184" cy="44" r="4"/>
  </g>
  <text x="125" y="72" font-family="Arial, sans-serif" font-size="9" fill="#475569" text-anchor="middle">I1  I2  I3  I4  I5  I6  I7  I8</text>
  <rect x="56" y="80" width="98" height="58" rx="6" fill="#0F172A"/>
  <rect x="62" y="86" width="86" height="46" rx="3" fill="#22D3EE" opacity=".9"/>
  <text x="105" y="104" font-family="Courier New, monospace" font-size="11" fill="#0F172A" text-anchor="middle" font-weight="bold">Q1 = ON</text>
  <text x="105" y="121" font-family="Courier New, monospace" font-size="10" fill="#0F172A" text-anchor="middle">T001 05.0s</text>
  <g fill="#E2E8F0" stroke="#94A3B8">
    <rect x="164" y="84" width="16" height="12" rx="3"/><rect x="184" y="84" width="16" height="12" rx="3"/>
    <rect x="164" y="102" width="16" height="12" rx="3"/><rect x="184" y="102" width="16" height="12" rx="3"/>
  </g>
  <circle cx="172" cy="128" r="5" fill="#3FD12A"/><circle cx="192" cy="128" r="5" fill="#F59E0B"/>
  <rect x="40" y="148" width="170" height="32" fill="#CBD5E1"/>
  <rect x="40" y="168" width="170" height="12" rx="12" fill="#CBD5E1"/>
  <g fill="#1E2A6E"><circle cx="66" cy="164" r="4"/><circle cx="102" cy="164" r="4"/><circle cx="138" cy="164" r="4"/><circle cx="174" cy="164" r="4"/></g>
  <text x="122" y="158" font-family="Arial, sans-serif" font-size="9" fill="#475569" text-anchor="middle">Q1       Q2       Q3       Q4</text>
  <path d="M66 180 V196 H250 V150" stroke="#3FD12A" stroke-width="3" fill="none"/>
  <circle cx="250" cy="136" r="14" fill="#3FD12A"/>
  <circle cx="250" cy="136" r="22" fill="#3FD12A" opacity=".25"/>
  <text x="250" y="140" font-family="Arial, sans-serif" font-size="11" fill="#0F172A" text-anchor="middle" font-weight="bold">M1</text>
  <g transform="translate(232,46)">
    <rect width="64" height="44" rx="8" fill="#FFFFFF" opacity=".95"/>
    <circle cx="20" cy="22" r="11" fill="#16A34A"/><text x="20" y="26" font-size="9" fill="#fff" text-anchor="middle" font-family="Arial">I</text>
    <circle cx="45" cy="22" r="11" fill="#DC2626"/><text x="45" y="26" font-size="9" fill="#fff" text-anchor="middle" font-family="Arial">O</text>
  </g>
  <path d="M232 68 H212" stroke="#F8FAFC" stroke-width="2" stroke-dasharray="4 3"/>
</svg>
"""


def mostrar_encabezado_institucional() -> None:
    if IMAGEN_ENCABEZADO.exists():
        st.image(str(IMAGEN_ENCABEZADO), use_container_width=True)


st.markdown(ESTILOS, unsafe_allow_html=True)
mostrar_encabezado_institucional()

if not API_KEY:
    st.error(
        "**Falta configurar la clave de la API.** Agregue `GEMINI_API_KEY` en "
        "`.streamlit/secrets.toml` (uso local) o en *Settings > Secrets* de "
        "Streamlit Cloud. La clave nunca debe escribirse dentro del código."
    )
    st.stop()

if not cargar_instrucciones().strip():
    st.error(
        "**Falta el archivo `instrucciones_tutor.md`.** Sin él, el asistente no "
        "es el que se validó con los expertos y el estudio no sería válido."
    )
    st.stop()

# --- Barra lateral -----------------------------------------------------------
with st.sidebar:
    st.header("Identificación")

    if st.session_state.identificado:
        st.success(f"Código: **{st.session_state.codigo}**")
        st.caption(f"{st.session_state.curso} - Paralelo {st.session_state.paralelo}")
    else:
        st.text_input(
            "Código de estudiante",
            key="entrada_codigo",
            placeholder="Ej. 4A-07",
            help="Es el código que le entregó el docente. No escriba su nombre.",
        )
        st.caption(f"{ASIGNATURA} · Paralelo {PARALELO_ESTUDIO}")

    st.divider()
    st.header("Evidencia")

    cabecera = (
        "REGISTRO DE TUTORÍA VIRTUAL LOGO!\n"
        f"{INSTITUCION}\n"
        f"Docente responsable: {DOCENTE} ({DOCENTE_CORREO})\n"
        f"Código de estudiante: {st.session_state.codigo or '(sin registrar)'}\n"
        f"Curso: {st.session_state.curso} | Paralelo: {st.session_state.paralelo}\n"
        f"Sesion: {st.session_state.id_sesion}\n"
        f"Modelo: {MODELO} | Modo: {MODO}\n"
        f"Fecha: {ahora().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Interacciones en esta sesión: {len(st.session_state.registro_sesion)}\n"
        + "=" * 60 + "\n\n"
    )
    cuerpo = "".join(
        f"[{r['fecha_hora']}] ESTUDIANTE:\n{r['pregunta']}\n\n"
        f"[{r['fecha_hora']}] TUTOR:\n{r['respuesta']}\n\n" + "-" * 60 + "\n\n"
        for r in st.session_state.registro_sesion
    ) or "(Sin interacciones en esta sesión)"

    st.download_button(
        "Descargar registro de la sesión (.txt)",
        data=cabecera + cuerpo,
        file_name=(
            f"tutoria_{st.session_state.codigo or 'sin_codigo'}_"
            f"{ahora().strftime('%Y%m%d_%H%M')}.txt"
        ),
        mime="text/plain",
        use_container_width=True,
    )

    if st.button("Terminar sesión y limpiar", use_container_width=True):
        for k in ("mensajes", "registro_sesion", "identificado", "consentimiento",
                  "codigo", "curso", "paralelo"):
            st.session_state[k] = [] if k in ("mensajes", "registro_sesion") else (
                False if k in ("identificado", "consentimiento") else ""
            )
        st.session_state.id_sesion = uuid.uuid4().hex[:12]
        st.session_state.inicio_sesion = ahora()
        st.rerun()

    st.divider()
    st.markdown(
        f"**Docente responsable**  \n{DOCENTE}  \n"
        f"{DOCENTE_CARGO}  \n[{DOCENTE_CORREO}](mailto:{DOCENTE_CORREO})"
    )

    st.divider()
    st.caption(f"Modelo: `{MODELO}`")
    destinos = {
        "supabase": "Registro: base de datos Supabase (+ respaldo local)",
        "sheets": "Registro: hoja de cálculo en línea (+ respaldo local)",
        "csv": "Registro: archivo local `registro/interacciones.csv`",
        "error": "Registro: **no se pudo guardar**. Avise al docente.",
    }
    if st.session_state.destino_registro in destinos:
        st.caption(destinos[st.session_state.destino_registro])
    if st.session_state.get("error_supabase"):
        st.caption(f"Aviso Supabase: {st.session_state['error_supabase'][:120]}")

def codigo_valido(codigo: str) -> bool:
    """Acepta solo los codigos del grupo de estudio (lista en Secrets o 4A-01..4A-17)."""
    lista = str(leer_secreto("CODIGOS_VALIDOS", "") or "")
    if lista.strip():
        validos = {c.strip().upper() for c in lista.split(",") if c.strip()}
        return codigo in validos
    m = re.fullmatch(rf"{PARALELO_ESTUDIO}-(\d{{2}})", codigo)
    return bool(m) and 1 <= int(m.group(1)) <= TOTAL_ESTUDIANTES


# --- Paso 1: identificacion y consentimiento --------------------------------
if not st.session_state.identificado:
    st.markdown(f"""
<div class="hero">
  <div class="hero-texto">
    <span class="chip">⚡ {ASIGNATURA} · Paralelo {PARALELO_ESTUDIO}</span>
    <h1>¡Bienvenido a tu Tutor Virtual LOGO!</h1>
    <p>Aprende a programar el módulo lógico LOGO! paso a paso: el tutor no te da la
    respuesta de inmediato, te hace pensar como un técnico en automatización.</p>
  </div>
  {ILUSTRACION_SVG}
</div>
<div class="tarjetas">
  <div class="tarjeta t1"><div class="ico">🧠</div><b>Te guía, no te copia</b><span>Pistas y preguntas hasta que tú mismo armes el programa.</span></div>
  <div class="tarjeta t2"><div class="ico">⚠️</div><b>Seguridad primero</b><span>Te recuerda las reglas de seguridad eléctrica antes de energizar.</span></div>
  <div class="tarjeta t3"><div class="ico">🔧</div><b>Prácticas guiadas</b><span>Marcha-paro, temporizadores, contadores, estrella-triángulo y más.</span></div>
  <div class="tarjeta t4"><div class="ico">📱</div><b>Desde cualquier lugar</b><span>Funciona en el celular y en la computadora, en clase o en casa.</span></div>
</div>
<div class="pasos">
  <div class="paso"><span class="n">1</span>Escribe tu <b>código</b> en la barra lateral (ej. 4A-07). En el celular, ábrela con <b>&gt;</b> arriba a la izquierda.</div>
  <div class="paso"><span class="n">2</span>Lee el <b>consentimiento</b> y marca la casilla.</div>
  <div class="paso"><span class="n">3</span>Pulsa <b>Comenzar la tutoría</b> y escribe tu primera duda.</div>
</div>
""", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(TEXTO_CONSENTIMIENTO)
    acepto = st.checkbox(
        "He leído lo anterior, entiendo que mi participación es voluntaria y "
        "acepto que se registren mis consultas de forma anónima."
    )

    if st.button("Comenzar la tutoría", type="primary"):
        codigo = st.session_state.get("entrada_codigo", "").strip().upper()
        codigo = codigo.replace(" ", "")
        es_prueba = bool(re.fullmatch(PATRON_PRUEBA, codigo))
        curso = ASIGNATURA
        paralelo = "PRUEBA" if es_prueba else PARALELO_ESTUDIO

        if not (es_prueba or codigo_valido(codigo)):
            st.warning(
                "Ese código no está registrado. Escriba exactamente el código que "
                "le entregó el docente (por ejemplo 4A-07). No use su nombre."
            )
        elif not acepto:
            st.warning("Debe aceptar el consentimiento informado para continuar.")
        else:
            st.session_state.update(
                codigo=codigo, curso=curso, paralelo=paralelo,
                identificado=True, consentimiento=True,
                inicio_sesion=ahora(),
            )
            registrar("consentimiento", {
                "fecha_hora": ahora().strftime("%Y-%m-%d %H:%M:%S"),
                "codigo_estudiante": codigo,
                "curso": curso,
                "paralelo": paralelo,
                "id_sesion": st.session_state.id_sesion,
                "acepto": "si",
            })
            st.rerun()
    st.stop()

# --- Paso 2: chat ------------------------------------------------------------
minutos = round((ahora() - st.session_state.inicio_sesion).total_seconds() / 60, 1)
st.caption(
    f"Sesión `{st.session_state.id_sesion}` · tiempo activo: **{minutos} min** · "
    f"consultas: **{len(st.session_state.registro_sesion)}**"
)

st.markdown(
    f'<div class="mini">🤖 Tutor Virtual LOGO! &nbsp;<small>· {ASIGNATURA} · '
    f'Paralelo {st.session_state.paralelo} · Código {st.session_state.codigo}</small></div>',
    unsafe_allow_html=True,
)

if not st.session_state.mensajes:
    st.info(
        "Este tutor no le va a entregar el programa resuelto de entrada: le hará "
        "preguntas para que usted lo razone. Puede empezar por ejemplo con "
        "*\"quiero programar un arranque estrella-triangulo en LOGO! 8\"* o "
        "*\"explíqueme la diferencia entre logica cableada y logica programada\"*."
    )

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if pregunta := st.chat_input("Escriba su duda sobre LOGO!..."):
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("El tutor está pensando..."):
            try:
                texto = responder(
                    API_KEY, MODELO, construir_instruccion_sistema(MODO),
                    st.session_state.mensajes[:-1], pregunta,
                )
            except ModeloSaturado as e:
                texto = None
                st.warning(
                    "**El servidor está saturado en este momento.** No es un "
                    "problema de su consulta ni de su equipo: suele durar unos "
                    "minutos. Vuelva a enviar la misma pregunta en un momento; "
                    "su conversación no se ha perdido."
                )
                st.caption(f"Detalle técnico para el docente: {str(e)[:180]}")
            except Exception as e:  # noqa: BLE001
                texto = None
                st.error(
                    "**No se pudo conectar con el asistente.** Avise al docente "
                    "e intente de nuevo en unos minutos."
                )
                st.caption(f"Detalle técnico para el docente: {str(e)[:180]}")

        if texto:
            st.markdown(texto)
            st.session_state.mensajes.append({"role": "assistant", "content": texto})

            momento = ahora()
            fila = {
                "fecha_hora": momento.strftime("%Y-%m-%d %H:%M:%S"),
                "codigo_estudiante": st.session_state.codigo,
                "curso": st.session_state.curso,
                "paralelo": st.session_state.paralelo,
                "id_sesion": st.session_state.id_sesion,
                "n_interaccion": len(st.session_state.registro_sesion) + 1,
                "minutos_sesion": round(
                    (momento - st.session_state.inicio_sesion).total_seconds() / 60, 1
                ),
                "modelo": MODELO,
                "modo": MODO,
                "caracteres_pregunta": len(pregunta),
                "caracteres_respuesta": len(texto),
                "pregunta": pregunta,
                "respuesta": texto,
            }
            st.session_state.registro_sesion.append(fila)
            st.session_state.destino_registro = registrar("interaccion", fila)

            if st.session_state.destino_registro == "error":
                st.warning(
                    "La consulta se respondió, pero no se pudo guardar en el "
                    "registro. Avise al docente y descargue el registro de la "
                    "sesión antes de cerrar."
                )
