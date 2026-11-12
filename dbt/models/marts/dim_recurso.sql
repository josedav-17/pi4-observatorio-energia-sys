select
    codigo_recurso,
    recurso,
    tipo_recurso,
    empresa,
    fuente_energia,
    estado
from {{ ref('stg_xm_listado_recursos') }}
