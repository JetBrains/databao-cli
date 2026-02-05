
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment"
    group by status

)

select *
from all_values
where value_field not in (
    'pending','open','success','cancelled','error','failure'
)


