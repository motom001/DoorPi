def get(doorpi_obj, name, value):
    if not name: name = [""]
    if not value: value = [""]

    event_handler = doorpi_obj.event_handler

    status = {}
    for name_requested in name:
        if name_requested in "sources":
            status["sources"] = event_handler.sources
        if name_requested in "events":
            status["events"] = event_handler.events
        if name_requested in "events_by_source":
            status["events_by_source"] = {
                source: event_handler.get_events_by_source(source)
                for source in event_handler.sources
            }
        if name_requested in "actions":
            status["actions"] = {}
            for event in event_handler.actions:
                status["actions"][event] = []
                for action in event_handler.actions[event]:
                    status["actions"][event].append(str(action))
        if name_requested in "threads":
            status["threads"] = str(event_handler.threads)
        if name_requested in "idle":
            status["idle"] = event_handler.idle

    return status


def is_active(doorpi_object):
    return bool(doorpi_object.event_handler)
