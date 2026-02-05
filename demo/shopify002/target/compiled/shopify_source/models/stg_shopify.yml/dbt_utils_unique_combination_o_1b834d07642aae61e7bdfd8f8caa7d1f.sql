





with validation_errors as (

    select
        inventory_item_id, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__inventory_item"
    group by inventory_item_id, source_relation
    having count(*) > 1

)

select *
from validation_errors


