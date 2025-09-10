import argparse
import os
import sqlalchemy
from langchain_aws import ChatBedrock
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP
from scalapay.databot import database
from scalapay.databot.tools import snowflake
from snowflake.sqlalchemy import URL
from sqlalchemy.dialects import registry
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from scalapay.utils import chamber

chamber.provision_environment_with_path('databot-dev')

DATABOT_AGENT_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
DIALECT_NAME = "MultiSchema"

registry.register(DIALECT_NAME.lower(), "scalapay.databot.dialect", DIALECT_NAME)


class LocalToolkit(snowflake.Toolkit):
    """A local toolkit for Snowflake that uses environment variables passed as arguments."""

    @classmethod
    def with_connection(cls, snowflake_conn: dict[str, any]) -> "LocalToolkit":
        """Create a toolkit instance with the provided connection parameters."""
        snowflake_url = URL(
            account=snowflake_conn["snowflake_account"],
            user=snowflake_conn["snowflake_user"],
            warehouse=snowflake_conn["snowflake_warehouse"],
            role=snowflake_conn["snowflake_role"],
            database=snowflake_conn["snowflake_database"],
            schemas=snowflake_conn["snowflake_schema"],
            authenticator="externalbrowser",
        )

        snowflake_url = snowflake_url.replace("snowflake", DIALECT_NAME.lower())

        engine = sqlalchemy.create_engine(snowflake_url)

        db = database.CustomSQLDatabase(
            engine,
            view_support=True,
            lazy_table_reflection=True,
        )

        llm = ChatBedrock(model_id=DATABOT_AGENT_MODEL, streaming=True, model_kwargs={"temperature": 0})

        return cls(db=db, llm=llm)
    
    @classmethod
    def with_ssm_credentials(cls, snowflake_conn: dict[str, any]) -> "LocalToolkit":
        """Create a toolkit instance with the provided connection parameters."""
        private_key_pem = os.environ["DATABOT_SNOWFLAKE_PRIVATE_KEY"].encode()
        passphrase = os.environ["DATABOT_SNOWFLAKE_PASSPHRASE"].encode()

        p_key = serialization.load_pem_private_key(private_key_pem, password=passphrase, backend=default_backend())

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        snowflake_url = URL(
            account=snowflake_conn["snowflake_account"],
            user=snowflake_conn["snowflake_user"],
            warehouse=snowflake_conn["snowflake_warehouse"],
            role=snowflake_conn["snowflake_role"],
            database=snowflake_conn["snowflake_database"],
            schemas=snowflake_conn["snowflake_schema"],
        )

        snowflake_url = snowflake_url.replace("snowflake", DIALECT_NAME.lower())

        engine = sqlalchemy.create_engine(
            snowflake_url,
            connect_args={
                "private_key": pkb,
            },
        )

        db = database.CustomSQLDatabase(
            engine,
            view_support=True,
            lazy_table_reflection=True,
        )

        llm = ChatBedrock(model_id=DATABOT_AGENT_MODEL, streaming=True, model_kwargs={"temperature": 0})

        return cls(db=db, llm=llm)


def main():
    parser = argparse.ArgumentParser(
        description="Connect to Snowflake using environment variables passed as arguments."
    )
    parser.add_argument("--account", type=str, default="tz45198.eu-central-1", help="The Snowflake account ID")
    parser.add_argument("--user", type=str, default="PRD_DATABOT", help="The Snowflake user.")
    parser.add_argument("--warehouse", type=str, default="PRD_DATABOT", help="The Snowflake warehouse.")
    parser.add_argument("--role", type=str, default="PRD_DATABOT", help="The Snowflake role")
    parser.add_argument("--database", type=str, default="PRD_ANALYTICS", help="The Snowflake database.")
    parser.add_argument(
        "--schema",
        type=str,
        default="COMMON,COMMON_MART,INTERCOM,COMPETITOR_ANALYSIS,IDV",
        help="The Snowflake schemas, as a string of comma seperated values",
    )

    args = parser.parse_args()
    connection = {
        "snowflake_account": args.account,
        "snowflake_user": args.user,
        "snowflake_warehouse": args.warehouse,
        "snowflake_role": args.role,
        "snowflake_database": args.database,
        "snowflake_schema": args.schema,
    }

    fastmcp_tools = [to_fastmcp(tool) for tool in LocalToolkit.with_ssm_credentials(connection).get_tools()]

    mcp = FastMCP("Snowflake", tools=fastmcp_tools)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()