from __future__ import annotations

import argparse

from load_to_sql import connect


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or replace an Azure SQL external user by object/client ID.")
    parser.add_argument("--server", default="ti-demo-ai-agents-swc-sql.database.windows.net")
    parser.add_argument("--database", default="service-portfolio-db")
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--user-name", required=True)
    parser.add_argument("--object-id")
    parser.add_argument("--from-external-provider", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    with connect(args.server, args.database, args.driver) as connection:
        cursor = connection.cursor()
        if args.replace and user_exists(cursor, args.user_name):
            cursor.execute(f"DROP USER {quoted_identifier(args.user_name)}")
        if not user_exists(cursor, args.user_name):
            if args.from_external_provider:
                cursor.execute(f"CREATE USER {quoted_identifier(args.user_name)} FROM EXTERNAL PROVIDER")
            elif args.object_id:
                cursor.execute(f"CREATE USER {quoted_identifier(args.user_name)} WITH OBJECT_ID = '{args.object_id}'")
            else:
                raise ValueError("Specify --object-id or --from-external-provider.")
        cursor.execute(
            "IF IS_ROLEMEMBER(N'db_datareader', ?) <> 1 "
            "BEGIN ALTER ROLE db_datareader ADD MEMBER " + quoted_identifier(args.user_name) + " END",
            args.user_name,
        )
        connection.commit()
        cursor.execute(
            "SELECT name, type_desc, CONVERT(varchar(100), sid, 2) AS sid_hex FROM sys.database_principals WHERE name = ?",
            args.user_name,
        )
        row = cursor.fetchone()
        print(f"{row.name} {row.type_desc} {row.sid_hex}")
        cursor.close()


def user_exists(cursor, user_name: str) -> bool:
    cursor.execute("SELECT 1 FROM sys.database_principals WHERE name = ?", user_name)
    return cursor.fetchone() is not None


def quoted_identifier(value: str) -> str:
    return "[" + value.replace("]", "]]") + "]"


if __name__ == "__main__":
    main()
