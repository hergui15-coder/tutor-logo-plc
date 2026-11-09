# Tutor Virtual LOGO! Siemens

Asistente conversacional para el aprendizaje de automatización industrial con el módulo
lógico LOGO! de Siemens, desarrollado para la carrera de Electromecánica del Instituto
Superior Tecnológico «Carlos Cisneros» (Riobamba, Ecuador).

Forma parte de un estudio de desarrollo y validación por juicio de expertos, con un piloto
de un solo grupo (pretest y postest) en el período octubre 2026 – febrero 2027.

**Autor:** Lic. Guido Hernán Cantuña Adriano, Mg.
guido.cantuna@istcarloscisneros.edu.ec

## Qué lo distingue

- **No entrega la solución.** Trabaja por andamiaje en cuatro escalones —comprensión,
  tabla de entradas y salidas, pistas de lógica y, solo al final, solución comentada— y no
  avanza hasta que el estudiante ha intentado.
- **Reglas de seguridad eléctrica innegociables.** El enclavamiento por programa no
  sustituye al enclavamiento por hardware entre contactores.
- **Identificación por código, nunca por nombre**, y consentimiento informado antes de la
  primera consulta.
- **Registro de cada interacción**, para medir la intensidad de uso del asistente.

## Configuración

Las claves van en `.streamlit/secrets.toml` en local, o en *Settings › Secrets* al
desplegar. Nunca dentro del código.

```toml
GEMINI_API_KEY = "..."
MODELO = "gemini-3.6-flash"
MODO_TUTOR = "guiado"
SUPABASE_URL = "https://....supabase.co"
SUPABASE_KEY = "..."   # clave publishable o anon, nunca la secreta
```

Las tablas de la base de datos se crean ejecutando `supabase_tablas.sql` en el SQL Editor
de Supabase. El detalle completo está en `LEEME - Despliegue y uso.md`.

## Aviso

Este repositorio no contiene claves ni datos de estudiantes. El archivo
`instrucciones_tutor.md` es el texto validado por juicio de expertos: modificarlo invalida
esa validación.
