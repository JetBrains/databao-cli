
  
    
    

    create  table
      "shopify"."main"."metricflow_time_spine__dbt_tmp"
  
    as (
      

select
    cast(range as date) as date_day
from generate_series(
    cast('2020-01-01' as date),
    cast('2030-01-01' as date),
    interval '1 day'
) as t(range)
    );
  
  