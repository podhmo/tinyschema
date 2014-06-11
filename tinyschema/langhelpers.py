# -*- coding:utf-8 -*-
class _Gensym(object):
    def __init__(self, i):
        self.i = i

    def __call__(self):
        self.i += 1
        return self.i

gensym = _Gensym(0)

