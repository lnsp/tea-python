import unittest
from runtime import std

string_value = std.Value(std.String, "Hallo Welt!", "identifier")
missing_value = std.Value(std.Integer, 0, "missing")
example_operator = std.Operator(None, "+")
missing_operator = std.Operator(None, "?")

class TestStd(unittest.TestCase):
    def test_namespace(self):
        """Test the Namespace class."""
        ns = std.Namespace(None)
        self.assertEqual(ns.parent, None)
        self.assertRaises(Exception, ns.find, "id", "identifier")
        self.assertRaises(Exception, ns.find, "op", "operator")
        # store example operator
        ns.store(string_value)
        ns.store(example_operator)
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(ns.find("op", example_operator.symbol), example_operator)
        # test upper namspace
        sub = ns.child()
        self.assertEqual(ns.find("id", string_value.name), string_value)
        self.assertEqual(ns.find("op", example_operator.symbol), example_operator)
        # check independence
        sub.store(missing_value)
        sub.store(missing_operator)
        self.assertRaises(Exception, ns.find, "id", missing_value.name)
        self.assertRaises(Exception, ns.find, "op", missing_operator.symbol)

    def test_default_namespace(self):
        """Test the default_namespace method."""
        ns = std.default_namespace()
        self.assertEqual(ns.parent, None)
   
    def test_default_context(self):
        """Test the default_context method."""
        context = std.default_context()
        self.assertEqual(context.globalns, context.ns)