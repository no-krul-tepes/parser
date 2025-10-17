import argparse
import asyncio
import sys
from importlib import import_module
from pathlib import Path

if __package__ is None or __package__ == "":
    package_dir = Path(__file__).resolve().parent
    parent_dir = package_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    package_name = package_dir.name
    config_module = import_module(f"{package_name}.config")
    parser_module = import_module(f"{package_name}.parser")
    utils_module = import_module(f"{package_name}.utils")
    db_module = import_module(f"{package_name}.db")

    get_config = config_module.get_config
    parse_group = parser_module.parse_group
    configure_logging = utils_module.configure_logging
    get_database = db_module.get_database
else:
    from .config import get_config
    from .parser import parse_group
    from .utils import configure_logging
    from .db import get_database

async def main(group_id: int) -> None:
    config = get_config()
    configure_logging(config.log_level)

    result = await parse_group(group_id)
    status = "SUCCESS" if result.status else "FAILURE"

    print(f"[{status}] Group {result.group_id}: {result.details}")
    if result.status:
        print(
            f"Added: {result.lessons_added}, Updated: {result.lessons_updated}, "
            f"Deleted: {result.lessons_deleted}"
        )
    elif result.errors:
        print(f"Error: {result.errors}")

    db = await get_database()
    await db.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run single schedule parsing.")
    parser.add_argument("group_id", type=int, help="Target group identifier")
    args = parser.parse_args()

    asyncio.run(main(args.group_id))
