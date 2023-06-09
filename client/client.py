import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from psutil import virtual_memory, cpu_percent
from platform import platform
import json
import aiopg
from psycopg2 import extras
from datetime import datetime, date

class SpecsMonitor:

    def __init__(self, db_name="postgres", user="postgres", password="postgres"):
        self._specs = {}

    def get_loads(self):
        ram_load = str(virtual_memory().available * 100 / virtual_memory().total)
        cpu_load = cpu_percent()
        self._specs["ram"] = ram_load
        self._specs["cpu"] = cpu_load

    def get_os_data(self):
        self._specs["os"] = platform()

    async def get_postgres_data(self):
        async with aiopg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1') as conn:
            if not conn.closed:
                async with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    await cur.execute("SELECT * from pg_stat_user_tables;")
                    data = await cur.fetchall()
                    postgres_vals = {}
                    for row in data:
                        postgres_vals[row["relname"]] = dict(row)

                    self._specs["postgres_stats"] = postgres_vals
                    self._specs["postgres_online"] = True
                    return

            else:
                self._specs["postgres_online"] = False

    async def get_specs(self):
        await self.get_postgres_data()
        self.get_os_data()
        self.get_loads()
        return self._specs


async def main():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    specs = SpecsMonitor()

    try:
        while True:
            vals = await specs.get_specs()
            vals["online"] = True
            print(f"Sending {vals}")
            data = (json.dumps(vals, default=json_serial) + " \n").encode()
            writer.write(data)
            await asyncio.sleep(5)
    except KeyboardInterrupt:

        writer.close()
        await writer.wait_closed()
        print("Closing connection")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

if __name__ == '__main__':
    asyncio.run(main())
    