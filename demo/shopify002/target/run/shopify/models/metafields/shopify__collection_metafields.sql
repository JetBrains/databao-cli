
  
    
    

    create  table
      "shopify"."main"."shopify__collection_metafields__dbt_tmp"
  
    as (
      








with source_table as (
    select *
    from "shopify"."main_stg_shopify"."stg_shopify__collection"
)



select *
from source_table


    );
  
  