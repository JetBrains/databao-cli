





with validation_errors as (

    select
        checkout_id, index, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__abandoned_checkout_shipping_line"
    group by checkout_id, index, source_relation
    having count(*) > 1

)

select *
from validation_errors


