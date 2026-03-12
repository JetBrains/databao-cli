-- ============================================================
-- CONFIGURATION: Set these values before running the script
-- ============================================================

-- Secrets
SET git_pat             = '<YOUR_GITHUB_PAT>';
SET git_username        = '<YOUR_GITHUB_USERNAME>';
SET openai_key          = '<YOUR_OPENAI_API_KEY>';
SET anthropic_key       = '<YOUR_ANTHROPIC_API_KEY>';
SET sf_ds_account       = '<SNOWFLAKE_DATASOURCE_ACCOUNT>';
SET sf_ds_warehouse     = '<SNOWFLAKE_DATASOURCE_WAREHOUSE>';
SET sf_ds_database      = '<SNOWFLAKE_DATASOURCE_DATABASE>';
SET sf_ds_user          = '<SNOWFLAKE_DATASOURCE_USER>';
SET sf_ds_password      = '<SNOWFLAKE_DATASOURCE_PASSWORD>';

-- Git repository
SET git_repo_origin     = 'https://github.com/JetBrains/databao-cli.git';
SET git_repo_name       = 'databao-cli';
SET git_branch          = 'main';

-- Streamlit app
SET streamlit_main_file = 'examples/demo-snowflake-project/src/databao_snowflake_demo/app.py';

-- ============================================================
-- 1. Role, Database, Schema, Warehouse
-- ============================================================
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE DATABASE STREAMLIT_DATABAO;
USE DATABASE STREAMLIT_DATABAO;
USE SCHEMA PUBLIC;

CREATE OR REPLACE WAREHOUSE STREAMLIT_DATABAO_WAREHOUSE
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
USE WAREHOUSE STREAMLIT_DATABAO_WAREHOUSE;

-- ============================================================
-- 2. Networking
-- ============================================================
CREATE OR REPLACE NETWORK RULE STREAMLIT_DATABAO.PUBLIC.STREAMLIT_DATABAO_EGRESS_RULE
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('0.0.0.0:443', '0.0.0.0:80');

-- Unset policy from our user first so CREATE OR REPLACE succeeds on re-runs
ALTER USER IF EXISTS STREAMLIT_DATABAO_USER UNSET NETWORK_POLICY;

CREATE OR REPLACE NETWORK POLICY STREAMLIT_DATABAO_NETWORK_POLICY
  ALLOWED_IP_LIST = ('0.0.0.0/0')
  COMMENT = 'Allow all network connections';

-- ============================================================
-- 3. Service User
-- ============================================================
CREATE OR REPLACE USER STREAMLIT_DATABAO_USER
  TYPE = SERVICE
  DEFAULT_ROLE = 'PUBLIC';

ALTER USER STREAMLIT_DATABAO_USER SET NETWORK_POLICY = 'STREAMLIT_DATABAO_NETWORK_POLICY';

-- ============================================================
-- 4. Git Repository + 5. Application Secrets
-- ============================================================
DECLARE
  _sql           VARCHAR;
  _git_pat       VARCHAR;
  _git_username  VARCHAR;
  _git_origin    VARCHAR;
  _git_repo      VARCHAR;
  _openai_key    VARCHAR;
  _anthropic_key VARCHAR;
  _ds_account    VARCHAR;
  _ds_warehouse  VARCHAR;
  _ds_database   VARCHAR;
  _ds_user       VARCHAR;
  _ds_password   VARCHAR;
BEGIN
  SELECT $git_pat, $git_username, $git_repo_origin, $git_repo_name,
         $openai_key, $anthropic_key, $sf_ds_account, $sf_ds_warehouse, $sf_ds_database,
         $sf_ds_user, $sf_ds_password
    INTO :_git_pat, :_git_username, :_git_origin, :_git_repo,
         :_openai_key, :_anthropic_key, :_ds_account, :_ds_warehouse, :_ds_database,
         :_ds_user, :_ds_password;

  -- Git PAT secret
  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.git_pat_secret'
    || ' TYPE = PASSWORD'
    || ' USERNAME = ''' || :_git_username || ''''
    || ' PASSWORD = ''' || :_git_pat      || '''';
  EXECUTE IMMEDIATE :_sql;

  -- API integration for Git
  _sql := 'CREATE OR REPLACE API INTEGRATION STREAMLIT_DATABAO_GIT_INTEGRATION'
    || ' API_PROVIDER = git_https_api'
    || ' API_ALLOWED_PREFIXES = (''' || :_git_origin || ''')'
    || ' ALLOWED_AUTHENTICATION_SECRETS = (STREAMLIT_DATABAO.PUBLIC.git_pat_secret)'
    || ' ENABLED = TRUE';
  EXECUTE IMMEDIATE :_sql;

  -- Git repository
  _sql := 'CREATE OR REPLACE GIT REPOSITORY STREAMLIT_DATABAO.PUBLIC."'
    || :_git_repo || '"'
    || ' ORIGIN = ''' || :_git_origin || ''''
    || ' API_INTEGRATION = STREAMLIT_DATABAO_GIT_INTEGRATION'
    || ' GIT_CREDENTIALS = STREAMLIT_DATABAO.PUBLIC.git_pat_secret';
  EXECUTE IMMEDIATE :_sql;

  -- Fetch latest
  _sql := 'ALTER GIT REPOSITORY STREAMLIT_DATABAO.PUBLIC."'
    || :_git_repo || '" FETCH';
  EXECUTE IMMEDIATE :_sql;

  -- Application secrets
  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.openai_api_key'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_openai_key || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.anthropic_api_key'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_anthropic_key || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.snowflake_ds_account'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_account || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.snowflake_ds_warehouse'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_warehouse || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.snowflake_ds_database'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_database || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.snowflake_ds_user'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_user || '''';
  EXECUTE IMMEDIATE :_sql;

  _sql := 'CREATE OR REPLACE SECRET STREAMLIT_DATABAO.PUBLIC.snowflake_ds_password'
    || ' TYPE = GENERIC_STRING'
    || ' SECRET_STRING = ''' || :_ds_password || '''';
  EXECUTE IMMEDIATE :_sql;
END;

-- ============================================================
-- 6. External Access Integrations
-- ============================================================
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION STREAMLIT_DATABAO_EAI
  ALLOWED_NETWORK_RULES = (STREAMLIT_DATABAO.PUBLIC.STREAMLIT_DATABAO_EGRESS_RULE)
  ENABLED = TRUE;

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION STREAMLIT_DATABAO_SECRETS_ACCESS
  ALLOWED_NETWORK_RULES = (STREAMLIT_DATABAO.PUBLIC.STREAMLIT_DATABAO_EGRESS_RULE)
  ALLOWED_AUTHENTICATION_SECRETS = (
    STREAMLIT_DATABAO.PUBLIC.openai_api_key,
    STREAMLIT_DATABAO.PUBLIC.anthropic_api_key,
    STREAMLIT_DATABAO.PUBLIC.snowflake_ds_account,
    STREAMLIT_DATABAO.PUBLIC.snowflake_ds_warehouse,
    STREAMLIT_DATABAO.PUBLIC.snowflake_ds_database,
    STREAMLIT_DATABAO.PUBLIC.snowflake_ds_user,
    STREAMLIT_DATABAO.PUBLIC.snowflake_ds_password
  )
  ENABLED = TRUE;

-- ============================================================
-- 7. Compute Pool
-- ============================================================
DROP COMPUTE POOL IF EXISTS STREAMLIT_DATABAO_COMPUTE_POOL;
CREATE COMPUTE POOL STREAMLIT_DATABAO_COMPUTE_POOL
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_M
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 300;

-- ============================================================
-- 8. UDF + Streamlit App
-- ============================================================
CREATE OR REPLACE FUNCTION STREAMLIT_DATABAO.PUBLIC.get_secret(secret_name STRING)
  RETURNS STRING
  LANGUAGE PYTHON
  RUNTIME_VERSION = 3.11
  HANDLER = 'get_secret'
  EXTERNAL_ACCESS_INTEGRATIONS = (STREAMLIT_DATABAO_SECRETS_ACCESS)
  SECRETS = (
    'openai_api_key' = STREAMLIT_DATABAO.PUBLIC.openai_api_key,
    'anthropic_api_key' = STREAMLIT_DATABAO.PUBLIC.anthropic_api_key,
    'snowflake_ds_account' = STREAMLIT_DATABAO.PUBLIC.snowflake_ds_account,
    'snowflake_ds_warehouse' = STREAMLIT_DATABAO.PUBLIC.snowflake_ds_warehouse,
    'snowflake_ds_database' = STREAMLIT_DATABAO.PUBLIC.snowflake_ds_database,
    'snowflake_ds_user' = STREAMLIT_DATABAO.PUBLIC.snowflake_ds_user,
    'snowflake_ds_password' = STREAMLIT_DATABAO.PUBLIC.snowflake_ds_password
  )
  AS
$$
import _snowflake

def get_secret(secret_name):
    return _snowflake.get_generic_secret_string(secret_name)
$$;

DECLARE
  _sql        VARCHAR;
  _git_repo   VARCHAR;
  _git_branch VARCHAR;
  _main_file  VARCHAR;
BEGIN
  SELECT $git_repo_name, $git_branch, $streamlit_main_file
    INTO :_git_repo, :_git_branch, :_main_file;

  _sql := 'CREATE OR REPLACE STREAMLIT STREAMLIT_DATABAO.PUBLIC.STREAMLIT_DATABAO_DEMO_SNOWFLAKE'
    || ' FROM ''@"STREAMLIT_DATABAO"."PUBLIC"."' || :_git_repo || '"/branches/"' || :_git_branch || '"/'''
    || ' MAIN_FILE = ''' || :_main_file || ''''
    || ' QUERY_WAREHOUSE = ''STREAMLIT_DATABAO_WAREHOUSE'''
    || ' COMPUTE_POOL = ''STREAMLIT_DATABAO_COMPUTE_POOL'''
    || ' RUNTIME_NAME = ''SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'''
    || ' EXTERNAL_ACCESS_INTEGRATIONS = (STREAMLIT_DATABAO_EAI)'
    || ' COMMENT = ''Databao Snowflake Demo UI''';
  EXECUTE IMMEDIATE :_sql;
END;
