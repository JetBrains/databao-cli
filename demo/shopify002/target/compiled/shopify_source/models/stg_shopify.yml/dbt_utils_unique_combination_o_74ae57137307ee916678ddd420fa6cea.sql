





with validation_errors as (

    select
        metafield_id, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__metafield"
    group by metafield_id, source_relation
    having count(*) > 1

)

select *
from validation_errors


