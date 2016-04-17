"""Test package for Executor.py."""
import unittest
from Runtime import Executor
from Runtime.Executor import Value, Node, store_null, TYPES, NODES, Identifier, Operator, Function



def new_node(typename, data=None):
    return Node(NODES[typename], data)
    
def new_literal(value):
    return new_node(Executor._LITERAL, value)
    
null_literal = new_literal(store_null())
int_literal = new_literal(Value(TYPES["int"], 0))
true_literal = new_literal(Value(TYPES["bool"], True))
false_literal = new_literal(Value(TYPES["bool"], False))
string_literal = new_literal(Value(TYPES["string"], "works"))
        

class TestExecutor(unittest.TestCase):
    """Test cases for the Executor."""

    def test_syntax_tree(self):
        """Test the syntax_tree method."""
        syntax_tree = Executor.syntax_tree()
        self.assertTrue(syntax_tree is not None)
        self.assertEqual(syntax_tree.type, NODES[Executor._SEQUENCE])

    def test_namespace(self):
        """Test the Namespace class."""
        ns = Executor.Namespace(None)
        self.assertEqual(ns.parent, None)
        self.assertEqual(ns.find_identifier("identifier"), None)
        self.assertEqual(ns.find_operator("operator"), None)
        # store example operator
        ns.put_identifier(Identifier(string_literal.data, "str"))
        ns.put_operator(Operator(None, "+"))
        self.assertEqual(ns.find_identifier("str"), string_literal.data)
        self.assertEqual(ns.find_operator("+").symbol, "+")
        # test upper namspace
        sub = Executor.Namespace(ns)
        self.assertEqual(ns.find_identifier("str"), string_literal.data)
        self.assertEqual(ns.find_operator("+").symbol, "+")
        # check independence
        sub.put_identifier(Identifier(true_literal.data, "missing"))
        sub.put_operator(Operator(None, "-"))
        self.assertEqual(ns.find_identifier("missing"), None)
        self.assertEqual(ns.find_operator("-"), None)

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
            "execution": lambda n, c: c.ns.put_identifier(Identifier(int_literal.data, "x")),
        }
        context = Executor.default_context()
        access_node = Executor.Node(access_node_type, None)
        Executor.run_in_substitution(access_node, context)
        self.assertEqual(context.ns.find_identifier("x"), None)

        value_node_type = {
            "name": "Test",
            "execution": lambda n, c: Executor.store_null(),
        }
        context = Executor.default_context()
        value_node = Executor.Node(value_node_type, None)
        value_result = Executor.run_in_substitution(value_node, context)
        self.assertEqual(value_result, Executor.store_null())

    def test_default_context(self):
        """Test the default_context method."""
        context = Executor.default_context()
        self.assertEqual(context.globalns, context.ns)

    def test_store_null(self):
        """Test the store_null method."""
        a = Executor.store_null()
        b = Executor.store_null()
        self.assertEqual(a.datatype, TYPES["null"])
        self.assertEqual(a.data, None)
        self.assertEqual(a, b)
        
    def test_sequence_node(self):
        """Test the sequence node."""
        context = Executor.default_context()
        return_node = new_node(Executor._RETURN, None)
        return_node.children = [true_literal]
        # empty sequence
        empty_seq = new_node(Executor._SEQUENCE)
        self.assertEqual(empty_seq.eval(context), null_literal.data)
        
        # non-empty sequence
        non_seq = new_node(Executor._SEQUENCE)
        non_seq.children = [null_literal, true_literal]
        self.assertEqual(non_seq.eval(context), true_literal.data)
        non_seq.children = [true_literal, null_literal]
        self.assertEqual(non_seq.eval(context), null_literal.data)
        
        # sequence with return
        ret_seq = new_node(Executor._SEQUENCE)
        ret_seq.children = [return_node, null_literal]
        self.assertEqual(ret_seq.eval(context), true_literal.data)
        

    def test_conditional_node(self):
        """Test the conditional node."""
        context = Executor.default_context()
        
        # Test bad conditional error
        bad_conditional = new_node(Executor._CONDITIONAL)
        bad_conditional.add(null_literal) # if None:
        bad_conditional.add(null_literal) # then None
        self.assertRaises(Exception, bad_conditional.eval, context)
        
        # Test correct result
        good_conditional = new_node(Executor._CONDITIONAL)
        good_conditional.add(true_literal)
        good_conditional.add(null_literal)
        self.assertEqual(good_conditional.eval(context), null_literal.data)

    def test_branch_node(self):
        """Test the branch node."""
        context = Executor.default_context()
        # always evaluates
        true_cond = new_node(Executor._CONDITIONAL)
        true_cond.children = [true_literal, string_literal]
        false_cond = new_node(Executor._CONDITIONAL)
        false_cond.children = [false_literal, null_literal]
        # Test if branch
        if_branch = new_node(Executor._BRANCH)
        if_branch.children = [true_cond, null_literal]
        self.assertEqual(if_branch.eval(context), string_literal.data)
        # Test if-else branch
        ifelse_branch = new_node(Executor._BRANCH)
        ifelse_branch.children = [false_cond, string_literal]
        self.assertEqual(ifelse_branch.eval(context), string_literal.data)
        # Test if-elif-else branch
        ifelifelse_branch = new_node(Executor._BRANCH)
        ifelifelse_branch.children = [false_cond, true_cond, null_literal]
        self.assertEqual(ifelifelse_branch.eval(context), string_literal.data)

    def test_loop_node(self):
        """Test the loop node."""
        break_node = new_node(Executor._BREAK)
        return_node = new_node(Executor._RETURN)
        return_node.children = [true_literal]
        context = Executor.default_context()
        
        # check for exception
        bad_loop = new_node(Executor._LOOP)
        bad_loop.children = [null_literal, true_literal]
        self.assertRaises(Exception, bad_loop.eval, context)
        
        # check for break 
        break_loop = new_node(Executor._LOOP)
        break_loop.children = [true_literal, break_node]
        self.assertEqual(break_loop.eval(context), null_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_DEFAULT)
        
        # check for return
        return_loop = new_node(Executor._LOOP)
        return_loop.children = [true_literal, return_node]
        self.assertEqual(return_loop.eval(context), true_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_RETURN)

    def test_return_node(self):
        """Test the return node."""
        # test empty return node
        context = Executor.default_context()
        empty_return = new_node(Executor._RETURN)
        self.assertEqual(empty_return.eval(context), null_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_RETURN)
        
        # test return with value
        context = Executor.default_context()
        value_return = new_node(Executor._RETURN)
        value_return.add(true_literal)
        self.assertEqual(value_return.eval(context), true_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_RETURN)

    def test_break_node(self):
        """Test the break node."""
        context = Executor.default_context()
        break_node = new_node(Executor._BREAK)
        self.assertEqual(break_node.eval(context), null_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_BREAK)

    def test_continue_node(self):
        """Test the continue node."""
        context = Executor.default_context()
        continue_node = new_node(Executor._CONTINUE)
        self.assertEqual(continue_node.eval(context), null_literal.data)
        self.assertEqual(context.behaviour, Executor.BEHAVIOUR_CONTINUE)

    def test_function_node(self):
        """Test the function node."""
        pass

    def test_operator_node(self):
        """Test the operator node."""
        pass

    def test_identifier_node(self):
        """Test the identifier node."""
        context = Executor.default_context()
        # Search in local ns
        context.ns.put_identifier(Identifier(string_literal.data, "i"))
        ident_node = new_node(Executor._IDENTIFIER, "i")
        self.assertEqual(ident_node.eval(context).data, string_literal.data.data)
        
        # Search in parent ns
        context.ns = Executor.Namespace(context.ns)
        self.assertEqual(ident_node.eval(context).data, string_literal.data.data)
        
        # Identifier does not exist
        bad_node = new_node(Executor._IDENTIFIER, "nope")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_literal_node(self):
        """Test the literal node."""
        context = Executor.default_context()
        self.assertEqual(null_literal.eval(context), null_literal.data)
        self.assertEqual(string_literal.eval(context), string_literal.data)
        self.assertEqual(true_literal.eval(context), true_literal.data)
        self.assertEqual(false_literal.eval(context), false_literal.data)

if __name__ == "__main__":
    unittest.main()
