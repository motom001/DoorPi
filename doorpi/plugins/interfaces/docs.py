# -*- coding: utf-8 -*-

from main import DOORPI

DOCUMENTATION = dict(
    fulfilled_with_one=False,
    text_description=_("%s text_description" % __name__),
    actions=[],
    events=[],
    configuration=[
        dict(section="/", key='typ', type='string', default=None, mandatory=True, description='Interface-Typ'),
    ],
    libraries=[],
    test=[]
)

DOCUMENTATION["test"].append(DOCUMENTATION["libraries"].keys())

