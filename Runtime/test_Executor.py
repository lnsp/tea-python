"""Test package for Executor.py."""
import unittest
from Runtime import Executor


class TestExecutor(unittest.TestCase):
    """Test cases for the Executor."""

    def test_syntax_tree(self):
        """Test the syntax_tree method."""
        syntax_tree = Executor.syntax_tree()
        self.assertTrue(syntax_tree is not None)
        self.assertEqual(syntax_tree.type, Executor.TYPES[Executor._SEQUENCE])

    def test_namespace(self):
        """Test the Namespace class."""
        ns = Executor.Namespace(None)
        self.assertEqual(ns.parent, None)
        self.assertEqual(ns.find_identifier("identifier"), None)
        self.assertEqual(ns.find_operator("operator"), None)
        # store example operator
        ns.put_identifier("a", 0)
        ns.put_operator("a", 1)
        self.assertEqual(ns.find_identifier("a"), 0)
        self.assertEqual(ns.find_operator("a"), 1)
        # test upper namspace
        sub = Executor.Namespace(ns)
        self.assertEqual(sub.find_identifier("a"), 0)
        self.assertEqual(sub.find_operator("a"), 1)
        # check independence
        sub.put_identifier("missing", -1)
        sub.put_operator("missing", -2)
        self.assertEqual(ns.find_identifier("missing"), None)
        self.assertEqual(ns.find_operator("missing"), None)

    def test_default_namespace(self):
        """Test the default_namespace method."""
        ns = Executor.default_namespace()
        self.assertEqual(ns.parent, None)
        self.assertEqual(ns.find_identifier(""), None)
        self.assertEqual(ns.find_operator(""), None)

    def test_run_in_substitution(self):
        """Test the run_in_substitution method."""
        access_node_type = {
            "name": "Test",
            "execution": lambda n, c: c["local"].put_identifier("x", 0),
        }
        context = Executor.default_context()
        access_node = Executor.Node(access_node_type, None)
        Executor.run_in_substitution(access_node, context)
        self.assertEqual(context["local"].find_identifier("x"), None)

        value_node_type = {
            "name": "Test",
            "execution": lambda n, c: Executor.store_none(),
        }
        context = Executor.default_context()
        value_node = Executor.Node(value_node_type, None)
        value_result = Executor.run_in_substitution(value_node, context)
        self.assertEqual(value_result, Executor.store_none())

    def test_default_context(self):
        """Test the default_context method."""
        context = Executor.default_context()
        self.assertEqual(context["global"], context["local"])

    def test_store_none(self):
        """Test the store_none method."""
        a = Executor.store_none()
        b = Executor.store_none()
        self.assertEqual(a["type"], Executor.DATA_NONE)
        self.assertEqual(a["value"], None)
        self.assertEqual(a, b)

    def test_store_value(self):
        """Test the store_value method."""
        i = Executor.store_value(Executor.DATA_NONE, None)
        self.assertEqual(i["type"], Executor.DATA_NONE)
        self.assertEqual(i["value"], None)
        
    def test_sequence_node(self):
        """Test the sequence node."""
        sequence = Executor.Node(Executor.TYPES[Executor._SEQUENCE], None)
        context = Executor.default_context()
        predicted_result = Executor.store_none()
        self.assertEqual(sequence.eval(context), predicted_result)

    def test_conditional_node(self):
        """Test the conditional node."""
        none_value = Executor.store_none()
        none_literal = Executor.Node(Executor.TYPES[Executor._LITERAL], none_value)
        true_value = Executor.store_value(Executor.DATA_BOOLEAN, True)
        true_literal = Executor.Node(Executor.TYPES[Executor._LITERAL], true_value)
        context = Executor.default_context()
        
        # Test bad conditional error
        bad_conditional = Executor.Node(Executor.TYPES[Executor._CONDITIONAL], None)
        bad_conditional.add(none_literal) # if None:
        bad_conditional.add(none_literal) # then None
        self.assertRaises(Exception, bad_conditional.eval, context)
        
        # Test correct result
        good_conditional = Executor.Node(Executor.TYPES[Executor._CONDITIONAL], None)
        good_conditional.add(true_literal)
        good_conditional.add(none_literal)
        self.assertEqual(good_conditional.eval(context), none_value)

    def test_branch_node(self):
        """Test the branch node."""
        pass

    def test_loop_node(self):
        """Test the loop node."""
        pass

    def test_return_node(self):
        """Test the return node."""
        pass

    def test_break_node(self):
        """Test the break node."""
        pass

    def test_continue_node(self):
        """Test the continue node."""
        pass

    def test_function_node(self):
        """Test the function node."""
        pass

    def test_operator_node(self):
        """Test the operator node."""
        pass

    def test_identifier_node(self):
        """Test the identifier node."""
        pass

    def test_literal_node(self):
        """Test the literal node."""
        pass

if __name__ == "__main__":
    unittest.main()
