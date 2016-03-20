# -*- coding: utf-8 -*-

from main import DOORPI

DOCUMENTATION = dict(
    fulfilled_with_one=False,
    text_description=_("%s text_description" % __name__),
    actions=[],
    events=[],
    configuration=[],
    libraries=dict(
        importlib=DOORPI.libraries['importlib'].copy(),
        json=DOORPI.libraries['json'].copy(),
        os=DOORPI.libraries['os'].copy()
    )
)
