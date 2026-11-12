select * from {{ source('silver', 'xm_precio_bolsa_horario') }}
