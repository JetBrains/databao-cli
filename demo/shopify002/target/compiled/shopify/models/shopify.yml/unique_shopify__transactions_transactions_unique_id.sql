
    
    

select
    transactions_unique_id as unique_field,
    count(*) as n_records

from "shopify"."main"."shopify__transactions"
where transactions_unique_id is not null
group by transactions_unique_id
having count(*) > 1


