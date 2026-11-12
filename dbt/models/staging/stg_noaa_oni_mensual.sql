select * from {{ source('silver', 'noaa_oni_mensual') }}
