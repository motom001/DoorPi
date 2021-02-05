"""DoorPiWeb handlers for the JSON API"""
import json
import textwrap
import typing as T

import aiohttp.web

import doorpi

routes = aiohttp.web.RouteTableDef()


@routes.get("/control/trigger_event")
async def _control_trigger_event(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    try:
        ev_name = request.query["event"]
        ev_source = request.query["source"]
        ev_extra = json.loads(request.query.get("extra", "null"))
    except (json.JSONDecodeError, KeyError) as err:
        raise aiohttp.web.HTTPBadRequest() from err

    if (
        request.can_read_body
        or ev_extra is not None
        and not isinstance(ev_extra, dict)
    ):
        raise aiohttp.web.HTTPBadRequest()

    doorpi.INSTANCE.event_handler.fire_event(
        ev_name, ev_source, extra=ev_extra
    )
    return aiohttp.web.json_response(
        {"success": True, "message": "Event was fired"},
        dumps=json_encoder.encode,
    )


@routes.get("/control/config_value_get")
async def _control_config_get(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    if "key" not in request.query or request.can_read_body:
        raise aiohttp.web.HTTPBadRequest()

    try:
        value = doorpi.INSTANCE.config[request.query["key"]]
        return aiohttp.web.json_response(
            {"success": True, "message": value},
            dumps=json_encoder.encode,
        )
    except KeyError as err:
        return aiohttp.web.json_response(
            {"success": False, "message": str(err)},
            dumps=json_encoder.encode,
        )


@routes.get("/control/config_value_set")
async def _control_config_set(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    if (
        "key" not in request.query
        or "value" not in request.query
        or request.can_read_body
    ):
        raise aiohttp.web.HTTPBadRequest()

    try:
        doorpi.INSTANCE.config[request.query["key"]] = request.query["value"]
    except (IndexError, KeyError, TypeError, ValueError) as err:
        return aiohttp.web.json_response(
            {"success": False, "message": f"{type(err).__name__}: {err}"},
            dumps=json_encoder.encode,
        )
    else:
        return aiohttp.web.json_response(
            {"success": True, "message": "OK"},
            dumps=json_encoder.encode,
        )


@routes.get("/control/config_value_delete")
async def _control_config_del(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    if "key" not in request.query or request.can_read_body:
        raise aiohttp.web.HTTPBadRequest()

    try:
        del doorpi.INSTANCE.config[request.query["key"]]
    except KeyError as err:
        return aiohttp.web.json_response(
            {"success": False, "message": str(err)},
            dumps=json_encoder.encode,
        )
    else:
        return aiohttp.web.json_response(
            {"success": True, "message": "OK"},
            dumps=json_encoder.encode,
        )


@routes.get("/control/config_save")
async def _control_config_save(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    if "key" not in request.query or request.can_read_body:
        raise aiohttp.web.HTTPBadRequest()

    try:
        doorpi.INSTANCE.config.save(doorpi.INSTANCE.configfile)
    except (KeyError, TypeError) as err:
        raise aiohttp.web.HTTPBadRequest() from err
    else:
        return aiohttp.web.json_response(
            {"success": True, "message": "OK"},
            dumps=json_encoder.encode,
        )


@routes.get("/mirror")
async def _mirror(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    text = textwrap.dedent(
        """\
        CLIENT VALUES:
        client_address={client[0]}:{client[1]} ({client[0]}:{client[1]})
        command={request.method}
        path={request.path}
        real path={request.path}
        query={request.query_string}
        request_version={request.version}

        SERVER VALUES:
        server_version=unknown
        sys_version=unknown
        protocol_version={request.version}

        HEADERS RECEIVED:
        {headers}
        """
    )

    client = (
        # pylint: disable=used-before-assignment # false positive
        transport.get_extra_info("peername")
        if (transport := request.transport) is not None
        else None
    ) or ("unknown", "unknown")

    return aiohttp.web.Response(
        text=text.format(
            client=client,
            request=request,
            headers="\n".join(f"{k}={v}" for k, v in request.headers.items()),
        )
    )


@routes.get("/status")
async def _status(
    request: aiohttp.web.BaseRequest,
) -> aiohttp.web.StreamResponse:
    module: T.List[str] = request.query.getall("module", [])
    name: T.List[str] = request.query.getall("name", [])
    value: T.List[str] = request.query.getall("value", [])

    status = doorpi.INSTANCE.get_status(modules=module, name=name, value=value)

    return aiohttp.web.json_response(
        status.dictionary, dumps=json_encoder.encode
    )


class SetAsTupleJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (set, frozenset)):
            return tuple(obj)
        return super().default(obj)


json_encoder = SetAsTupleJSONEncoder()
