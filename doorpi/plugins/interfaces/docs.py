# -*- coding: utf-8 -*-

from main import DOORPI

DOCUMENTATION = dict(
    fulfilled_with_one=False,
    text_description='Basis Klasse der Interfaces',
    actions=[],
    events=[],
    configuration=[
        dict(section="/", key='typ', type='string', default=None, mandatory=True, description='Interface-Typ'),
    ],
    libraries=[]
)
