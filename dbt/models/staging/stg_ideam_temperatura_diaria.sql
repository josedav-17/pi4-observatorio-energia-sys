select * from {{ source('silver', 'ideam_temperatura_diaria') }}
