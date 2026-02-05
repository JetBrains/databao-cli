
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment_event"
    group by status

)

select *
from all_values
where value_field not in (
    'attempted_delivery','delayed','delivered','failure','in_transit','out_for_delivery','ready_for_pickup','picked_up','label_printed','label_purchased','confirmed'
)



  
  
      
    ) dbt_internal_test