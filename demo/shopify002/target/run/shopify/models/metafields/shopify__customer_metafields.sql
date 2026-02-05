
  
    
    

    create  table
      "shopify"."main"."shopify__customer_metafields__dbt_tmp"
  
    as (
      








with source_table as (
    select *
    from "shopify"."main_stg_shopify"."stg_shopify__customer"
)



select *
from source_table


    );
  
  