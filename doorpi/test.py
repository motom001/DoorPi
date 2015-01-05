#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test(value):
    print str(value).lower() in ['1', 'high', 'on']

test(1)
test('1')
test('high')