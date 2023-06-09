from psutil import virtual_memory, cpu_percent
from platform import platform
import aiopg
from psycopg2 import extras
import docker
class SpecsMonitor:

    def __init__(self):
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

    def get_docker_data(self):
        data = {}
        client = docker.from_env()
        for container in client.containers.list():
            stats = container.stats(stream=False)
            data[stats["id"]] = {}
            data[stats["id"]]["name"] = stats["name"]
            data[stats["id"]]["status"] = container.status
            data[stats["id"]]["cpu"] = stats["cpu_stats"]["cpu_usage"]["total_usage"]
            data[stats["id"]]["ram"] = stats["memory_stats"]["usage"]

        self._specs["docker"] = data

    async def get_specs(self):
        await self.get_postgres_data()
        self.get_os_data()
        self.get_loads()
        self.get_docker_data()
        return self._specs