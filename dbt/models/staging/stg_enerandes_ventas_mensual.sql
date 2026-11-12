select * from {{ source('silver', 'enerandes_ventas_mensual') }}
