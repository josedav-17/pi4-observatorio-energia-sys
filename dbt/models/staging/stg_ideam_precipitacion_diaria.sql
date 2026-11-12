select * from {{ source('silver', 'ideam_precipitacion_diaria') }}
