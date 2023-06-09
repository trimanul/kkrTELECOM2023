import asyncio
import json
import pprint
import redis
from datetime import datetime, date
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

async def on_connect(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    timer = 0
    addr = writer.get_extra_info('peername')
    print(f"{addr[0]}:{addr[1]} connected")
    redis_con = redis.from_url("redis://localhost", decode_responses=True)
    data = ""
    while True:
        try:
            data = await reader.readline()
        except ConnectionResetError:
            print(f"{addr[0]}:{addr[1]} suddenly disconnected.")
            return
        if not data:
            timer += 1
            await asyncio.sleep(1)
            if timer > 5:
                print(f"{addr[0]}:{addr[1]} timed out")
                writer.close()
                await writer.wait_closed()
                return
            continue
        message = data.decode()
        stats = json.loads(message)
        stats["node_online"] = True
        stats["node_ip"] = addr[0]
        print(f"Received data from {addr[0]}:{addr[1]}: ")
        pprint.pprint(stats)
        redis_con.set(addr[0], json.dumps(stats, default=json_serial))
        await asyncio.sleep(1)


async def main():
    server = await asyncio.start_server(
        on_connect, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
