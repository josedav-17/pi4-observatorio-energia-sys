select * from {{ source('silver', 'xm_aportes_hidricos_diario') }}
