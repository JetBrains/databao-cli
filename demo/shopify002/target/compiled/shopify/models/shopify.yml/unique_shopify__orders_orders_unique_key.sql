
    
    

select
    orders_unique_key as unique_field,
    count(*) as n_records

from "shopify"."main"."shopify__orders"
where orders_unique_key is not null
group by orders_unique_key
having count(*) > 1


