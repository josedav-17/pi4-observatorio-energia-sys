select
    d.anio,
    d.mes,
    m.municipio,
    sum(v.energia_kwh) as energia_kwh,
    sum(v.valor_cop) as valor_cop
from fact_ventas_mensual v
join dim_fecha d on d.fecha_key = v.fecha_key
join dim_municipio m on m.codigo_municipio = v.municipio_key
group by d.anio, d.mes, m.municipio
order by energia_kwh desc
limit 20
