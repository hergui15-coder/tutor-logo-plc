-- =========================================================================
-- Tutor Virtual LOGO! — creacion de tablas en Supabase
--
-- Pegue TODO este contenido en Supabase > SQL Editor > New query y pulse RUN.
-- Se ejecuta una sola vez, al preparar el estudio.
-- =========================================================================

-- Una fila por consulta del estudiante al asistente.
create table if not exists public.interacciones (
    id                    bigint generated always as identity primary key,
    creado_en             timestamptz not null default now(),
    fecha_hora            text,
    codigo_estudiante     text,
    curso                 text,
    paralelo              text,
    id_sesion             text,
    n_interaccion         integer,
    minutos_sesion        real,
    modelo                text,
    modo                  text,
    caracteres_pregunta   integer,
    caracteres_respuesta  integer,
    pregunta              text,
    respuesta             text
);

-- Una fila por consentimiento aceptado.
create table if not exists public.consentimientos (
    id                 bigint generated always as identity primary key,
    creado_en          timestamptz not null default now(),
    fecha_hora         text,
    codigo_estudiante  text,
    curso              text,
    paralelo           text,
    id_sesion          text,
    acepto             text
);

-- Consultas mas frecuentes del analisis: por estudiante y por sesion.
create index if not exists idx_interacciones_codigo
    on public.interacciones (codigo_estudiante);
create index if not exists idx_interacciones_sesion
    on public.interacciones (id_sesion);

-- -------------------------------------------------------------------------
-- Seguridad: la aplicacion solo puede INSERTAR. No puede leer, modificar ni
-- borrar. Asi, aunque la clave se filtrara, nadie podria descargar las
-- conversaciones de los estudiantes. Usted las consulta desde el panel de
-- Supabase, que entra con su propia cuenta.
-- -------------------------------------------------------------------------
alter table public.interacciones   enable row level security;
alter table public.consentimientos enable row level security;

drop policy if exists "app puede insertar interacciones"   on public.interacciones;
drop policy if exists "app puede insertar consentimientos" on public.consentimientos;

create policy "app puede insertar interacciones"
    on public.interacciones for insert to anon with check (true);

create policy "app puede insertar consentimientos"
    on public.consentimientos for insert to anon with check (true);

-- =========================================================================
-- CONSULTAS UTILES PARA EL ANALISIS (ejecutelas cuando tenga datos)
-- =========================================================================

-- Intensidad de uso por estudiante: es la variable moderadora del estudio.
-- select codigo_estudiante,
--        count(*)                        as consultas,
--        count(distinct id_sesion)       as sesiones,
--        round(max(minutos_sesion)::numeric, 1) as minutos_sesion_mas_larga,
--        min(fecha_hora)                 as primera,
--        max(fecha_hora)                 as ultima
-- from public.interacciones
-- group by codigo_estudiante
-- order by consultas desc;

-- Distribucion del uso a lo largo de las ocho semanas.
-- select date_trunc('week', creado_en)::date as semana,
--        count(*) as consultas,
--        count(distinct codigo_estudiante) as estudiantes_activos
-- from public.interacciones
-- group by 1 order by 1;
