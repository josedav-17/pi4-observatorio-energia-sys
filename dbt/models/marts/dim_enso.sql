select
    cast(strftime(fecha, '%Y%m') as integer) as enso_key,
    fecha as mes,
    oni,
    fase_enso
from {{ ref('stg_noaa_oni_mensual') }}
