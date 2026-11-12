select
    hora,
    round(avg(precio_cop_kwh), 2) as precio_promedio_cop_kwh,
    round(avg(demanda_kwh), 2) as demanda_promedio_kwh,
    count(*) as observaciones
from fact_mercado_horario
group by hora
order by hora
