# -*- coding:utf-8 -*-
import tinyschema as t


# definition
@t.as_schema
class Signal(object):
    color = t.column(t.TextField, widget="select")


# runtime
signal = Signal(color="red")
signal.color = signal.color.bind(t.OneOf(["red", "blue", "yellow"]))
signal.color.choices = [("red", "red"), ("blue", "blue"), ("yellow", "yellow")]

# generate html

from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=["."])

result = (lookup.get_template("render.mako").render(schema=signal))
print(result)

# <form action="#" method="POST">
#   <select>
#          <option value="red" selected="selected">red</option>
#          <option value="blue">blue</option>
#          <option value="yellow">yellow</option>
#   </select>
# </form>


# validation

signal = Signal(color="black")
signal.color = signal.color.bind(t.OneOf(["red", "blue", "yellow"]))
signal.color.choices = [("red", "red"), ("blue", "blue"), ("yellow", "yellow")]

try:
    print(signal.validate())
except t.Failure as e:
    print(e.errors["color"])
    # ['black is not in red, blue, yellow']


signal = Signal(color="blue")
signal.color = signal.color.bind(t.OneOf(["red", "blue", "yellow"]))
signal.color.choices = [("red", "red"), ("blue", "blue"), ("yellow", "yellow")]


print(signal.validate())  # => OrderedDict([('color', 'blue')])
