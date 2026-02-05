





with validation_errors as (

    select
        customer_id, index, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__customer_tag"
    group by customer_id, index, source_relation
    having count(*) > 1

)

select *
from validation_errors


