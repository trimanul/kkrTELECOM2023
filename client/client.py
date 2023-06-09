import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import json

from datetime import datetime, date
from monitor import SpecsMonitor


async def main():
    try:
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)
    except Exception:
        print("failed to connect to the server")
        raise ConnectionError

    specs = SpecsMonitor()

    while True:
        try:
            vals = await specs.get_specs()
            vals["online"] = True
            print(f"Sending {vals}")
            data = (json.dumps(vals, default=json_serial) + " \n").encode()
            writer.write(data)
            await asyncio.sleep(5)

        except Exception:
            print("Lost connection with a server")
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
