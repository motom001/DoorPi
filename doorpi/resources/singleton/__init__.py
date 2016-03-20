# -*- coding: utf-8 -*-

# thx @ Hrissimir Neikov
# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/#c1


def Singleton(klass):
    if not klass._instance:
        klass._instance = klass()
    return klass._instance
