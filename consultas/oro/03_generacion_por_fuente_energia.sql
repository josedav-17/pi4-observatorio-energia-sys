select
    r.fuente_energia,
    d.anio,
    sum(g.generacion_kwh) as generacion_kwh
from fact_generacion_recurso g
join dim_recurso r on r.codigo_recurso = g.recurso_key
join dim_fecha d on d.fecha_key = g.fecha_key
group by r.fuente_energia, d.anio
order by d.anio, generacion_kwh desc
