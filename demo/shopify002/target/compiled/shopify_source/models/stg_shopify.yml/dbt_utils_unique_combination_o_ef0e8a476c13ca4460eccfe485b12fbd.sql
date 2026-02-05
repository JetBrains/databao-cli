





with validation_errors as (

    select
        fulfillment_event_id, source_relation
    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment_event"
    group by fulfillment_event_id, source_relation
    having count(*) > 1

)

select *
from validation_errors


