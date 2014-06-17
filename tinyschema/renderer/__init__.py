# -*- coding:utf-8 -*-
from mako.lookup import TemplateLookup
import os.path

here = os.path.abspath(os.path.dirname(__file__))


class SchemaRenderer(object):
    def __init__(self, template_name="form.mako", directories=[here], lookup=TemplateLookup):
        self.template_name = template_name
        self.lookup = lookup(directories)
        self.template = None
        self.cache = {}

    def renderer(self, widget_name):
        try:
            return self.cache[widget_name]
        except KeyError:
            if self.template is None:
                self.template = self.lookup.get_template(self.template_name)
            renderer = self.template.get_def(widget_name)
            self.cache[widget_name] = renderer
            return renderer

    def render_schema(self, schema):
        r = []
        for field in schema:
            r.append(self.render_field(field))
        return u"".join(r)

    def render_field(self, field):
        return self.renderer(field.widget).render(field)
