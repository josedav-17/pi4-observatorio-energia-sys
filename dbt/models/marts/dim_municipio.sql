select
    codigo_municipio,
    municipio,
    municipio_key,
    codigo_departamento,
    latitud,
    longitud,
    true as es_divipola
from {{ ref('stg_divipola_municipios') }}
