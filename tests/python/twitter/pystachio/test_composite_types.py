import pytest
import unittest
from twitter.pystachio import (
  Empty,
  String,
  Integer,
  Float,
  Map,
  List,
  Composite,
  Default,
  Required)

def test_basic_types():
  class Resources(Composite):
    cpu = Float
    ram = Integer
  assert Resources().check().ok()
  assert Resources(cpu = 1.0).check().ok()
  assert Resources(cpu = 1.0, ram = 100).check().ok()
  assert Resources(cpu = 1, ram = 100).check().ok()
  assert Resources(cpu = '1.0', ram = 100).check().ok()


def test_nested_composites():
  class Resources(Composite):
    cpu = Float
    ram = Integer
  class Process(Composite):
    name = String
    resources = Resources
  assert Process().check().ok()
  assert Process(name = "hello_world").check().ok()
  assert Process(resources = Resources()).check().ok()
  assert Process(resources = Resources(cpu = 1.0)).check().ok()
  assert Process(resources = Resources(cpu = 1)).check().ok()
  assert Process(name = 15)(resources = Resources(cpu = 1.0)).check().ok()

def test_defaults():
  class Resources(Composite):
    cpu = Default(Float, 1.0)
    ram = Integer
  assert Resources() == Resources(cpu = 1.0)
  assert Resources(cpu = 2.0)._schema_data['cpu'] == Float(2.0)

  class Process(Composite):
    name = String
    resources = Default(Resources, Resources(ram = 10))

  assert Process().check().ok()
  assert Process() == Process(resources = Resources(cpu = 1.0, ram = 10))
  assert Process() != Process(resources = Resources())
  assert Process()(resources = Empty).check().ok()

def test_composite_interpolation():
  class Resources(Composite):
    cpu = Required(Float)
    ram = Integer
    disk = Integer

  class Process(Composite):
    name = Required(String)
    resources = Map(String, Resources)

  p = Process(name = "hello")
  assert p(resources = {'foo': Resources()}) == \
         p(resources = {'{{whee}}': Resources()}).bind(whee='foo')
  assert p(resources = {'{{whee}}': Resources(cpu='{{whee}}')}).bind(whee=1.0) == \
         p(resources = {'1.0': Resources(cpu=1.0)})
