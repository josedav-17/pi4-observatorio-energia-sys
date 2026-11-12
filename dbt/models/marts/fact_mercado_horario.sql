with mercado as (
    select
        p.fecha,
        p.hora,
        p.precio_cop_kwh,
        d.demanda_kwh
    from {{ ref('stg_xm_precio_bolsa_horario') }} p
    inner join {{ ref('stg_xm_demanda_horaria') }} d
        on p.fecha = d.fecha and p.hora = d.hora
)
select
    cast(strftime(m.fecha, '%Y%m%d') as integer) as fecha_key,
    m.hora,
    m.precio_cop_kwh,
    m.demanda_kwh,
    e.volumen_util_pct,
    a.aportes_mwh,
    n.oni,
    n.fase_enso
from mercado m
left join {{ ref('stg_xm_embalses_diario') }} e on m.fecha = e.fecha
left join {{ ref('stg_xm_aportes_hidricos_diario') }} a on m.fecha = a.fecha
left join {{ ref('stg_noaa_oni_mensual') }} n
    on date_trunc('month', m.fecha) = date_trunc('month', n.fecha)
