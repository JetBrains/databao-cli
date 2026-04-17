select * from {{ source('shopify_analytics', 'orders') }}
