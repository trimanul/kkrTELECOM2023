import aiohttp
from aiohttp import web
from db import budgetDAO


async def list_handler(request: aiohttp.request):
    budget = request.app["dao"]
    data = budget.get_node_list()
    return web.json_response(data)


async def node_handler(request: aiohttp.request):
    budget = request.app["dao"]
    ip = request.rel_url.query['ip']
    data = budget.get_node(ip)
    return web.json_response(data)

if __name__ == "__main__":
    app = web.Application()
    app["dao"] = budgetDAO()
    app.add_routes([
        web.get('/', list_handler),
        web.get('/node', node_handler),
    ])
    web.run_app(app, host="127.0.0.1", port=32222)