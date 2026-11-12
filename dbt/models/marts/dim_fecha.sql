with calendario as (
    select cast(dia as date) as fecha
    from generate_series(
        (select date_trunc('year', min(fecha))::date from {{ ref('stg_enerandes_ventas_mensual') }}),
        (select (date_trunc('year', max(fecha)) + interval '1 year' - interval '1 day')::date
         from {{ ref('stg_enerandes_ventas_mensual') }}),
        interval 1 day
    ) as serie(dia)
)
select
    cast(strftime(c.fecha, '%Y%m%d') as integer) as fecha_key,
    c.fecha,
    extract(year from c.fecha)::integer as anio,
    extract(month from c.fecha)::integer as mes,
    strftime(c.fecha, '%B') as nombre_mes,
    extract(quarter from c.fecha)::integer as trimestre,
    extract(day from c.fecha)::integer as dia_mes,
    extract(isodow from c.fecha)::integer as dia_semana,
    strftime(c.fecha, '%A') as nombre_dia,
    coalesce(e.fase_enso, 'Sin clasificación') as fase_enso,
    e.oni
from calendario c
left join {{ ref('stg_noaa_oni_mensual') }} e
    on date_trunc('month', c.fecha) = date_trunc('month', e.fecha)
