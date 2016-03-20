# -*- coding: utf-8 -*-

from main import DOORPI

core_event_parameters = []
for doorpi_parameter in DOORPI.arguments.keys():
    core_event_parameters.append(dict(
        name=doorpi_parameter,
        type=type(DOORPI.arguments[doorpi_parameter]).__name__,
        description=_("doorpi parameter %s description" % doorpi_parameter)
    ))

DOCUMENTATION = dict(
    text_description=_("%s text_description" % __name__),
    actions=[],
    events=[
        dict(name='BeforeStartup', description=_("%s event description BeforeStartup" % __name__),
             parameter=core_event_parameters),
        dict(name='OnStartup', description=_("%s event description OnStartup" % __name__),
             parameter=core_event_parameters),
        dict(name='AfterStartup', description=_("%s event description AfterStartup" % __name__),
             parameter=core_event_parameters),
        dict(name='BeforeShutdown', description=_("%s event description BeforeShutdown" % __name__),
             parameter=core_event_parameters),
        dict(name='OnShutdown', description=_("%s event description OnShutdown" % __name__),
             parameter=core_event_parameters),
        dict(name='AfterShutdown', description=_("%s event description AfterShutdown" % __name__),
             parameter=core_event_parameters)
    ],
    configuration=[],
    libraries=dict(
        importlib=dict(),
        os=dict(),
        logging=dict(),
        re=dict(),
        json=dict(),
        time=dict(),
        math=dict(),
        wave=dict(),
        array=dict(),
        sys=dict(),
        argparse=dict(),
        datetime=dict(),
        cgi=dict(),
        resource=dict(),
        random=dict(),
        string=dict(),
        threading=dict(),
        inspect=dict()
    ),
    test=[]
)

DOCUMENTATION["test"].append(DOCUMENTATION["libraries"].keys())
for single_lib in DOCUMENTATION["libraries"].keys():
    DOCUMENTATION["libraries"][single_lib].update(dict(
        mandatory=True,
        text_warning=_("library %s text_warning" % single_lib),
        text_description=_("library %s text_description" % single_lib),
        text_installation=_("library %s text_installation" % single_lib),
        auto_install=dict(standard=True),
        text_test=_("library global text_test pre") +
                  _("<code> import %s</code>") % single_lib +
                  _("library global text_test post")),
        text_configuration=_("library %s text_configuration" % single_lib),
        configuration=[],
        text_links={
            _("docs.python.org"): _("library %s text_links %s" % (single_lib, DOORPI.CONST.USED_PYTHON_VERSION))
        }
    )
