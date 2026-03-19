-- ============================================================
-- CONFIGURATION: Set these values before running the script
-- ============================================================

-- Name suffix: change this to create a fully independent set of all
-- Snowflake objects (database, warehouse, compute pool, integrations, etc.).
-- Leave empty for the default installation.
-- Example: SET suffix = 'V2';
SET suffix              = 'DEMO';

-- Secrets
SET openai_key          = '<YOUR_OPENAI_API_KEY>';
SET anthropic_key       = '<YOUR_ANTHROPIC_API_KEY>';
SET sf_ds_warehouse     = '<SNOWFLAKE_DATASOURCE_WAREHOUSE>';
SET sf_ds_database      = '<SNOWFLAKE_DATASOURCE_DATABASE>';

-- Git repository
SET git_repo_origin     = 'https://github.com/JetBrains/databao-cli.git';
SET git_repo_name       = 'databao-cli';
SET git_branch          = 'main';

-- Streamlit app
SET streamlit_main_file = 'examples/demo-snowflake-project/src/databao_snowflake_demo/app.py';

-- ============================================================
-- SETUP (everything below is derived from the configuration above)
-- ============================================================
USE ROLE ACCOUNTADMIN;

-- Bootstrap warehouse: Snowflake needs an active warehouse to evaluate
-- expressions in the scripting block below. This gets dropped at the end.
CREATE WAREHOUSE IF NOT EXISTS STREAMLIT_DATABAO_BOOTSTRAP_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
USE WAREHOUSE STREAMLIT_DATABAO_BOOTSTRAP_WH;

DECLARE
  _sql             VARCHAR;

  -- Configuration
  _openai_key      VARCHAR DEFAULT $openai_key;
  _anthropic_key   VARCHAR DEFAULT $anthropic_key;
  _ds_warehouse    VARCHAR DEFAULT $sf_ds_warehouse;
  _ds_database     VARCHAR DEFAULT $sf_ds_database;
  _git_origin      VARCHAR DEFAULT $git_repo_origin;
  _git_repo        VARCHAR DEFAULT $git_repo_name;
  _git_branch      VARCHAR DEFAULT $git_branch;
  _main_file       VARCHAR DEFAULT $streamlit_main_file;

  -- Derived object names (controlled by $suffix — do not modify)
  _db              VARCHAR DEFAULT 'STREAMLIT_DATABAO_DB_' || $suffix;
  _wh              VARCHAR DEFAULT 'STREAMLIT_DATABAO_WAREHOUSE_' || $suffix;
  _egress_rule     VARCHAR DEFAULT 'STREAMLIT_DATABAO_EGRESS_RULE_' || $suffix;
  _git_integration VARCHAR DEFAULT 'STREAMLIT_DATABAO_GIT_INTEGRATION_' || $suffix;
  _eai             VARCHAR DEFAULT 'STREAMLIT_DATABAO_EAI_' || $suffix;
  _secrets_access  VARCHAR DEFAULT 'STREAMLIT_DATABAO_SECRETS_ACCESS_' || $suffix;
  _compute_pool    VARCHAR DEFAULT 'STREAMLIT_DATABAO_COMPUTE_POOL_' || $suffix;
  _app_name        VARCHAR DEFAULT 'STREAMLIT_DATABAO_APP_' || $suffix;
BEGIN
  -- ==========================================================
  -- 1. Database, Schema, Warehouse
  -- ==========================================================
  EXECUTE IMMEDIATE 'CREATE OR REPLACE DATABASE ' || :_db;
  EXECUTE IMMEDIATE 'USE DATABASE ' || :_db;
  EXECUTE IMMEDIATE 'USE SCHEMA PUBLIC';

  _sql := 'CREATE OR REPLACE WAREHOUSE ' || :_wh
    || ' WAREHOUSE_SIZE = ''XSMALL'''
    || ' AUTO_SUSPEND = 60'
    || ' AUTO_RESUME = TRUE';
  EXECUTE IMMEDIATE :_sql;
  EXECUTE IMMEDIATE 'USE WAREHOUSE ' || :_wh;

  -- ==========================================================
  -- 2. Networking
  -- ==========================================================
  _sql := 'CREATE OR REPLACE NETWORK RULE ' || :_db || '.PUBLIC.' || :_egress_rule
    || ' MODE = EGRESS'
    || ' TYPE = HOST_PORT'
    || ' VALUE_LIST = (''0.0.0.0:443'', ''0.0.0.0:80'')';
  EXECUTE IMMEDIATE :_sql;

  -- ==========================================================
  -- 3. Git Repository
  -- ==========================================================
  _sql := 'CREATE OR REPLACE API INTEGRATION ' || :_git_integration
    || ' API_PROVIDER = git_https_api'
    || ' API_ALLOWED_PREFIXES = (''' || :_git_origin || ''')'
    || ' ALLOWED_AUTHENTICATION_SECRETS = ()'
    || ' ENABLED = TRUE';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE GIT REPOSITORY ' || :_db || '.PUBLIC."' || :_git_repo || '"'
    || ' ORIGIN = ''' || :_git_origin || ''''
    || ' API_INTEGRATION = ' || :_git_integration;
  EXECUTE IMMEDIATE :_sql;

  _sql := 'ALTER GIT REPOSITORY ' || :_db || '.PUBLIC."' || :_git_repo || '" FETCH';
  EXECUTE IMMEDIATE :_sql;

  -- ==========================================================
  -- 4. Application Secrets
  -- ==========================================================
  _sql := 'CREATE OR REPLACE SECRET ' || :_db || '.PUBLIC.openai_api_key'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_openai_key || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET ' || :_db || '.PUBLIC.anthropic_api_key'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_anthropic_key || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET ' || :_db || '.PUBLIC.snowflake_ds_warehouse'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_warehouse || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET ' || :_db || '.PUBLIC.snowflake_ds_database'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_database || '''';
  EXECUTE IMMEDIATE :_sql;

  -- ==========================================================
  -- 5. External Access Integrations
  -- ==========================================================
  _sql := 'CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ' || :_eai
    || ' ALLOWED_NETWORK_RULES = (' || :_db || '.PUBLIC.' || :_egress_rule || ')'
    || ' ENABLED = TRUE';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ' || :_secrets_access
    || ' ALLOWED_NETWORK_RULES = (' || :_db || '.PUBLIC.' || :_egress_rule || ')'
    || ' ALLOWED_AUTHENTICATION_SECRETS = ('
    || :_db || '.PUBLIC.openai_api_key, '
    || :_db || '.PUBLIC.anthropic_api_key, '
    || :_db || '.PUBLIC.snowflake_ds_warehouse, '
    || :_db || '.PUBLIC.snowflake_ds_database'
    || ') ENABLED = TRUE';
  EXECUTE IMMEDIATE :_sql;

  -- ==========================================================
  -- 6. Compute Pool
  -- ==========================================================
  EXECUTE IMMEDIATE 'DROP COMPUTE POOL IF EXISTS ' || :_compute_pool;
  _sql := 'CREATE COMPUTE POOL ' || :_compute_pool
    || ' MIN_NODES = 1'
    || ' MAX_NODES = 1'
    || ' INSTANCE_FAMILY = CPU_X64_M'
    || ' AUTO_RESUME = TRUE'
    || ' AUTO_SUSPEND_SECS = 300';
  EXECUTE IMMEDIATE :_sql;

  -- ==========================================================
  -- 7. UDF + Streamlit App
  -- ==========================================================
  _sql := 'CREATE OR REPLACE FUNCTION ' || :_db || '.PUBLIC.get_secret(secret_name STRING)'
    || ' RETURNS STRING'
    || ' LANGUAGE PYTHON'
    || ' RUNTIME_VERSION = 3.11'
    || ' HANDLER = ''get_secret'''
    || ' EXTERNAL_ACCESS_INTEGRATIONS = (' || :_secrets_access || ')'
    || ' SECRETS = ('
    || '  ''openai_api_key'' = ' || :_db || '.PUBLIC.openai_api_key,'
    || '  ''anthropic_api_key'' = ' || :_db || '.PUBLIC.anthropic_api_key,'
    || '  ''snowflake_ds_warehouse'' = ' || :_db || '.PUBLIC.snowflake_ds_warehouse,'
    || '  ''snowflake_ds_database'' = ' || :_db || '.PUBLIC.snowflake_ds_database'
    || ') AS '
    || '$$' || CHR(10)
    || 'import _snowflake' || CHR(10)
    || CHR(10)
    || 'def get_secret(secret_name):' || CHR(10)
    || '    return _snowflake.get_generic_secret_string(secret_name)' || CHR(10)
    || '$$';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE STREAMLIT ' || :_db || '.PUBLIC."' || :_app_name || '"'
    || ' FROM ''@"' || :_db || '"."PUBLIC"."' || :_git_repo || '"/branches/"' || :_git_branch || '"/'''
    || ' MAIN_FILE = ''' || :_main_file || ''''
    || ' QUERY_WAREHOUSE = ''' || :_wh || ''''
    || ' COMPUTE_POOL = ''' || :_compute_pool || ''''
    || ' RUNTIME_NAME = ''SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'''
    || ' EXTERNAL_ACCESS_INTEGRATIONS = (' || :_eai || ')'
    || ' COMMENT = ''Databao Snowflake Demo UI''';
  EXECUTE IMMEDIATE :_sql;
END;

-- Clean up the bootstrap warehouse
DROP WAREHOUSE IF EXISTS STREAMLIT_DATABAO_BOOTSTRAP_WH;

SELECT 'Streamlit app STREAMLIT_DATABAO_APP_' || $suffix || ' created successfully.' AS STATUS;
