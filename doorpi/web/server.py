"""The server component of DoorPiWeb"""
import asyncio
import logging
import os
import socket
import typing as T

import aiohttp.web

import doorpi.metadata
import doorpi.util
import doorpi.web.api
import doorpi.web.auth
import doorpi.web.resources

SD_LISTEN_FDS_START = 3  # defined in <systemd/sd-daemon.h>

logger = logging.getLogger(__name__)

RequestHandler = T.Callable[
    [aiohttp.web.Request], T.Awaitable[aiohttp.web.StreamResponse]
]


async def run() -> None:
    """Start the web server thread"""
    cfg = doorpi.INSTANCE.config.view("web")
    shutdown = asyncio.Event()

    app = aiohttp.web.Application()
    app["doorpi_web_config"] = cfg
    doorpi.web.resources.setup(app)
    app.add_routes(doorpi.web.api.routes)
    app.add_routes(doorpi.web.resources.routes)
    doorpi.web.auth.setup(app)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()

    fds = int(os.environ.get("LISTEN_FDS", "0"))
    if fds > 0:
        logger.debug("Received %d listen FDs", fds)
        for fd in range(SD_LISTEN_FDS_START, SD_LISTEN_FDS_START + fds):
            await aiohttp.web.SockSite(
                runner,
                socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM),
            ).start()
    else:
        await aiohttp.web.TCPSite(runner, cfg["ip"], cfg["port"]).start()

    eh = doorpi.INSTANCE.event_handler
    eh.fire_event_sync("OnWebServerStart", "doorpi.web")
    eh.register_action(
        "OnShutdown",
        doorpi.actions.CallbackAction(
            asyncio.get_event_loop().call_soon_threadsafe,
            shutdown.set,
        ),
    )

    try:
        await shutdown.wait()
    finally:
        await runner.cleanup()
        eh.unregister_source("doorpi.web", force=True)
