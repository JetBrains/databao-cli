





with validation_errors as (

    select
        product_id, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__product"
    group by product_id, source_relation
    having count(*) > 1

)

select *
from validation_errors


