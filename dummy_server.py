from aiohttp import web
from multiprocessing import Process

routes = web.RouteTableDef()


@routes.get("/")
async def hello(request):
    return web.Response(text="Hello, world")


def start_server():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


def run():
    p = Process(target=start_server)
    p.start()


if __name__ == "__main__":
    run()
