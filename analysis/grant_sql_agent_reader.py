from __future__ import annotations

import argparse

from load_to_sql import connect


def main() -> None:
    parser = argparse.ArgumentParser(description="Grant read-only Azure SQL access to a Foundry agent managed identity.")
    parser.add_argument("--server", default="ti-demo-ai-agents-swc-sql.database.windows.net")
    parser.add_argument("--database", default="service-portfolio-db")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--user-name", default="service-portfolio-chat-agent-vnext")
    parser.add_argument("--object-id", default="cc7494ee-7bdb-4a1f-b08a-5704ae980641")
    args = parser.parse_args()

    with connect(args.server, args.database, args.driver) as connection:
        cursor = connection.cursor()
        if not user_exists(cursor, args.user_name):
            create_user(cursor, args.user_name, args.object_id)
        cursor.execute(
            "IF IS_ROLEMEMBER(N'db_datareader', ?) <> 1 "
            "BEGIN ALTER ROLE db_datareader ADD MEMBER " + quoted_identifier(args.user_name) + " END",
            args.user_name,
        )
        connection.commit()
        cursor.execute(
            "SELECT name, type_desc FROM sys.database_principals WHERE name = ?",
            args.user_name,
        )
        row = cursor.fetchone()
        print(f"Granted db_datareader to {row.name} ({row.type_desc}).")
        cursor.close()


def user_exists(cursor, user_name: str) -> bool:
    cursor.execute("SELECT 1 FROM sys.database_principals WHERE name = ?", user_name)
    return cursor.fetchone() is not None


def create_user(cursor, user_name: str, object_id: str) -> None:
    try:
        cursor.execute(f"CREATE USER {quoted_identifier(user_name)} WITH OBJECT_ID = '{object_id}'")
    except Exception:
        cursor.execute(f"CREATE USER {quoted_identifier(user_name)} WITH SID = {object_id_to_sid(object_id)}, TYPE = E")


def quoted_identifier(value: str) -> str:
    return "[" + value.replace("]", "]]") + "]"


def object_id_to_sid(object_id: str) -> str:
    hex_value = object_id.replace("-", "")
    return "0x" + hex_value


if __name__ == "__main__":
    main()
