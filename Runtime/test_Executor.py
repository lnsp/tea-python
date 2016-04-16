"""Test package for Executor.py."""
import unittest
from Runtime import Executor

def new_node(typename, data=None):
    return Executor.Node(Executor.TYPES[typename], data)
    
def new_literal(value):
    return new_node(Executor._LITERAL, value)

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
        sequence = new_node(Executor._SEQUENCE)
        context = Executor.default_context()
        predicted_result = Executor.store_none()
        self.assertEqual(sequence.eval(context), predicted_result)

    def test_conditional_node(self):
        """Test the conditional node."""
        none_literal = new_literal(Executor.store_none())
        true_literal = new_literal(Executor.store_value(Executor.DATA_BOOLEAN, True))
        context = Executor.default_context()
        
        # Test bad conditional error
        bad_conditional = new_node(Executor._CONDITIONAL)
        bad_conditional.add(none_literal) # if None:
        bad_conditional.add(none_literal) # then None
        self.assertRaises(Exception, bad_conditional.eval, context)
        
        # Test correct result
        good_conditional = new_node(Executor._CONDITIONAL)
        good_conditional.add(true_literal)
        good_conditional.add(none_literal)
        self.assertEqual(good_conditional.eval(context), none_literal.data)

    def test_branch_node(self):
        """Test the branch node."""
        correct_literal = new_literal(Executor.store_value(Executor.DATA_STRING, "works"))
        true_literal = new_literal(Executor.store_value(Executor.DATA_BOOLEAN, True))
        false_literal = new_literal(Executor.store_value(Executor.DATA_BOOLEAN, False))
        none_literal = new_literal(Executor.store_none())
        context = Executor.default_context()
        # always evaluates
        true_cond = new_node(Executor._CONDITIONAL)
        true_cond.add(true_literal)
        true_cond.add(correct_literal)
        false_cond = new_node(Executor._CONDITIONAL)
        false_cond.add(false_literal)
        false_cond.add(none_literal)
        # Test if branch
        if_branch = new_node(Executor._BRANCH)
        if_branch.add(true_cond)
        if_branch.add(none_literal)
        self.assertEqual(if_branch.eval(context), correct_literal.data)
        # Test if-else branch
        ifelse_branch = new_node(Executor._BRANCH)
        ifelse_branch.add(false_cond)
        ifelse_branch.add(correct_literal)
        self.assertEqual(ifelse_branch.eval(context), correct_literal.data)
        # Test if-elif-else branch
        ifelifelse_branch = new_node(Executor._BRANCH)
        ifelifelse_branch.add(false_cond)
        ifelifelse_branch.add(true_cond)
        ifelifelse_branch.add(none_literal)
        self.assertEqual(ifelifelse_branch.eval(context), correct_literal.data)

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
