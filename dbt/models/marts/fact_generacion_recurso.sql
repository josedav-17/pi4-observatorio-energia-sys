select
    cast(strftime(g.fecha, '%Y%m%d') as integer) as fecha_key,
    g.hora,
    g.codigo_recurso as recurso_key,
    g.generacion_kwh
from {{ ref('stg_xm_generacion_recurso_horario') }} g
inner join {{ ref('dim_recurso') }} r on r.codigo_recurso = g.codigo_recurso
