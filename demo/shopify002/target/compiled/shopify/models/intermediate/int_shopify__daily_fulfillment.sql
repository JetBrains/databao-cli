

with fulfillment_event as (

    select *
    from "shopify"."main_stg_shopify"."stg_shopify__fulfillment_event"
),

fulfillment_aggregates as (

    select 
        source_relation,
        cast(date_trunc('day', happened_at) as date) as date_day

        
        , count(distinct case when lower(status) = 'attempted_delivery' then fulfillment_id end) as count_fulfillment_attempted_delivery
        
        , count(distinct case when lower(status) = 'delayed' then fulfillment_id end) as count_fulfillment_delayed
        
        , count(distinct case when lower(status) = 'delivered' then fulfillment_id end) as count_fulfillment_delivered
        
        , count(distinct case when lower(status) = 'failure' then fulfillment_id end) as count_fulfillment_failure
        
        , count(distinct case when lower(status) = 'in_transit' then fulfillment_id end) as count_fulfillment_in_transit
        
        , count(distinct case when lower(status) = 'out_for_delivery' then fulfillment_id end) as count_fulfillment_out_for_delivery
        
        , count(distinct case when lower(status) = 'ready_for_pickup' then fulfillment_id end) as count_fulfillment_ready_for_pickup
        
        , count(distinct case when lower(status) = 'picked_up' then fulfillment_id end) as count_fulfillment_picked_up
        
        , count(distinct case when lower(status) = 'label_printed' then fulfillment_id end) as count_fulfillment_label_printed
        
        , count(distinct case when lower(status) = 'label_purchased' then fulfillment_id end) as count_fulfillment_label_purchased
        
        , count(distinct case when lower(status) = 'confirmed' then fulfillment_id end) as count_fulfillment_confirmed
        
    
    from fulfillment_event
    group by 1,2

)

select *
from fulfillment_aggregates