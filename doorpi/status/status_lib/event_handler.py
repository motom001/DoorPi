import operator


def get(doorpi_obj, name, value):
    del value
    status_getters = {
        "sources": operator.attrgetter("sources"),
        "events": operator.attrgetter("events"),
        "events_by_source": lambda eh: {
            source: eh.get_events_by_source(source)
            for source in eh.sources},
        "actions": lambda eh: {
            event: list(map(str, actions))
            for event, actions in eh.actions.items()},
        "threads": lambda eh: str(eh.threads),
        "idle": operator.attrgetter("idle"),
    }

    if not name:
        name = status_getters.keys()
    return {n: status_getters[n](doorpi_obj.event_handler) for n in name}


def is_active(doorpi_object):
    return bool(doorpi_object.event_handler)
