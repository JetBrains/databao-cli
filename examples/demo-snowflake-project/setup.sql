-- ============================================================
-- CONFIGURATION: Set these values before running the script
-- ============================================================

-- Name suffix: change this to create a fully independent set of all
-- Snowflake objects (database, warehouse, compute pool, integrations, etc.).
-- Leave empty for the default installation.
-- Example: SET suffix = 'V2';
SET suffix                  = 'DEMO';

-- Secrets
SET openai_api_key          = '<YOUR_OPENAI_API_KEY>';
SET anthropic_api_key           = '<YOUR_ANTHROPIC_API_KEY>';
SET snowflake_ds_warehouse  = '<SNOWFLAKE_DATASOURCE_WAREHOUSE>';
SET snowflake_ds_database   = '<SNOWFLAKE_DATASOURCE_DATABASE>';

-- Git repository
SET git_repo_origin         = 'https://github.com/JetBrains/databao-cli.git';
SET git_repo_name           = '"databao-cli"';
SET git_branch              = '"main"';

-- Streamlit app
SET streamlit_main_file     = 'examples/demo-snowflake-project/src/databao_snowflake_demo/app.py';

-- Derived object names (controlled by $suffix — do not modify)
SET database_name           = 'STREAMLIT_DATABAO_DB_' || $suffix;
SET egress_rule             = 'STREAMLIT_DATABAO_EGRESS_RULE_' || $suffix;
SET git_integration         = 'STREAMLIT_DATABAO_GIT_INTEGRATION_' || $suffix;
SET app_name                = 'STREAMLIT_DATABAO_APP_' || $suffix;
SET app_warehouse           = 'STREAMLIT_DATABAO_WAREHOUSE_' || $suffix;
SET app_eai                 = 'STREAMLIT_DATABAO_EAI_' || $suffix;
SET secrets_access          = 'STREAMLIT_DATABAO_SECRETS_ACCESS_' || $suffix;

SET app_compute_pool        = 'SYSTEM_COMPUTE_POOL_CPU';

-- OPTIONAL: Uncomment to create a dedicated compute pool for the app
-- SET app_compute_pool        = 'STREAMLIT_DATABAO_COMPUTE_POOL_' || $suffix;
--
-- DROP COMPUTE POOL IF EXISTS IDENTIFIER($app_compute_pool);
-- CREATE COMPUTE POOL IDENTIFIER($app_compute_pool)
--     MIN_NODES = 1
--     MAX_NODES = 1
--     INSTANCE_FAMILY = CPU_X64_M
--     AUTO_RESUME = TRUE
--     AUTO_SUSPEND_SECS = 300;

CREATE OR REPLACE DATABASE IDENTIFIER($database_name);

USE DATABASE IDENTIFIER($database_name);
USE SCHEMA PUBLIC;

CREATE OR REPLACE WAREHOUSE IDENTIFIER($app_warehouse)
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

USE WAREHOUSE IDENTIFIER($app_warehouse);

CREATE OR REPLACE SECRET openai_api_key
    TYPE = GENERIC_STRING
    SECRET_STRING = $openai_api_key;

CREATE OR REPLACE SECRET anthropic_api_key
    TYPE = GENERIC_STRING
    SECRET_STRING = $anthropic_api_key;

CREATE OR REPLACE SECRET snowflake_ds_warehouse
    TYPE = GENERIC_STRING
    SECRET_STRING = $snowflake_ds_warehouse;

CREATE OR REPLACE SECRET snowflake_ds_database
    TYPE = GENERIC_STRING
    SECRET_STRING = $snowflake_ds_database;

CREATE OR REPLACE NETWORK RULE IDENTIFIER($egress_rule)
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('0.0.0.0:443', '0.0.0.0:80');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION IDENTIFIER($app_eai)
    ALLOWED_NETWORK_RULES = ($egress_rule)
    ENABLED = TRUE;

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION IDENTIFIER($secrets_access)
    ALLOWED_NETWORK_RULES = ($egress_rule)
    ALLOWED_AUTHENTICATION_SECRETS = (
        openai_api_key,
        anthropic_api_key,
        snowflake_ds_warehouse,
        snowflake_ds_database
    ) ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION IDENTIFIER($git_integration)
    API_PROVIDER = git_https_api
    API_ALLOWED_PREFIXES = ($git_repo_origin)
    ALLOWED_AUTHENTICATION_SECRETS = ()
    ENABLED = TRUE;

CREATE OR REPLACE GIT REPOSITORY IDENTIFIER($git_repo_name)
    ORIGIN = $git_repo_origin
    API_INTEGRATION = $git_integration;

ALTER GIT REPOSITORY IDENTIFIER($git_repo_name) FETCH;

DECLARE
    _sql                    VARCHAR;
    _streamlit_stage_path   VARCHAR;
BEGIN
    _streamlit_stage_path := '@' || $database_name || '."PUBLIC".' || $git_repo_name || '/branches/' || $git_branch || '/';

    _sql := 'CREATE OR REPLACE STREAMLIT "' || $app_name || '"'
    || ' FROM ''' || :_streamlit_stage_path || ''''
    || ' MAIN_FILE = ''' || $streamlit_main_file || ''''
    || ' QUERY_WAREHOUSE = ''' || $app_warehouse || ''''
    || ' COMPUTE_POOL = ''' || $app_compute_pool || ''''
    || ' RUNTIME_NAME = ''SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'''
    || ' EXTERNAL_ACCESS_INTEGRATIONS = (' || $app_eai || ')'
    || ' COMMENT = ''Databao Snowflake Connection Test UI''';
  EXECUTE IMMEDIATE :_sql;
END;

DECLARE
    _sql        VARCHAR;
BEGIN
    _sql := 'CREATE OR REPLACE FUNCTION get_secret(secret_name STRING)'
        || ' RETURNS STRING'
        || ' LANGUAGE PYTHON'
        || ' RUNTIME_VERSION = 3.11'
        || ' HANDLER = ''get_secret'''
        || ' EXTERNAL_ACCESS_INTEGRATIONS = (' || $secrets_access || ')'
        || ' SECRETS = ('
        || '  ''openai_api_key'' = openai_api_key,'
        || '  ''anthropic_api_key'' = anthropic_api_key,'
        || '  ''snowflake_ds_warehouse'' = snowflake_ds_warehouse,'
        || '  ''snowflake_ds_database'' = snowflake_ds_database'
        || ') AS '
        || '$$' || CHR(10)
        || 'import _snowflake' || CHR(10)
        || CHR(10)
        || 'def get_secret(secret_name):' || CHR(10)
        || '    return _snowflake.get_generic_secret_string(secret_name)' || CHR(10)
        || '$$';

    EXECUTE IMMEDIATE :_sql;
END;
