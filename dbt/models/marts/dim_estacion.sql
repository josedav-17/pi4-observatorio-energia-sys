with estaciones as (
    select codigo_estacion, estacion, codigo_municipio, municipio, municipio_key, latitud, longitud
    from {{ ref('stg_ideam_precipitacion_diaria') }}
    union all
    select codigo_estacion, estacion, codigo_municipio, municipio, municipio_key, latitud, longitud
    from {{ ref('stg_ideam_temperatura_diaria') }}
)
select codigo_estacion, estacion, codigo_municipio, municipio, municipio_key, latitud, longitud
from estaciones
qualify row_number() over (partition by codigo_estacion order by estacion) = 1
