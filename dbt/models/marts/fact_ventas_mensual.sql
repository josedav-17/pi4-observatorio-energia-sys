select
    cast(strftime(v.fecha, '%Y%m%d') as integer) as fecha_key,
    v.codigo_municipio as municipio_key,
    v.segmento,
    v.tipo_compra,
    sum(v.energia_kwh) as energia_kwh,
    sum(v.valor_cop) as valor_cop,
    sum(v.clientes) as clientes
from {{ ref('stg_enerandes_ventas_mensual') }} v
join {{ ref('dim_municipio') }} m on m.codigo_municipio = v.codigo_municipio
group by 1, 2, 3, 4
