with municipios as (
    select
        codigo_municipio,
        municipio,
        municipio_key,
        codigo_departamento,
        latitud,
        longitud,
        true as es_divipola
    from {{ ref('stg_divipola_municipios') }}
), ventas_sin_match as (
    select distinct
        'NO-DANE-' || v.municipio_key as codigo_municipio,
        v.municipio,
        v.municipio_key,
        'NA' as codigo_departamento,
        cast(null as double) as latitud,
        cast(null as double) as longitud,
        false as es_divipola
    from {{ ref('stg_enerandes_ventas_mensual') }} v
    where not exists (
        select 1 from municipios m where m.municipio_key = v.municipio_key
    )
)
select * from municipios
union all
select * from ventas_sin_match
