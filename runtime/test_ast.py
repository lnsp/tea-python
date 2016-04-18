import unittest
from runtime import ast, env, lib
    
null_literal = ast.Literal(env.Value(env.Null))
int_literal = ast.Literal(env.Value(lib.Integer, 0))
true_literal = ast.Literal(env.Value(lib.Boolean, True))
false_literal = ast.Literal(env.Value(lib.Boolean, False))
string_literal = ast.Literal(env.Value(lib.String, "Hallo Welt!", "identifier"))

class TestAst(unittest.TestCase):
    def test_sequence_node(self):
        """Test the sequence node."""
        context = env.empty_context()
        return_node = ast.Return()
        return_node.children = [true_literal]
        # empty sequence
        empty_seq = ast.Sequence()
        self.assertEqual(empty_seq.eval(context), null_literal.value)
        
        # non-empty sequence
        non_seq = ast.Sequence()
        non_seq.children = [null_literal, true_literal]
        self.assertEqual(non_seq.eval(context), true_literal.value)
        non_seq.children = [true_literal, null_literal]
        self.assertEqual(non_seq.eval(context), null_literal.value)
        
        # sequence with return
        ret_seq = ast.Sequence()
        ret_seq.children = [return_node, null_literal]
        self.assertEqual(ret_seq.eval(context), true_literal.value)
        self.assertEqual(ret_seq.__str__(), "<Node (sequence)>")
        

    def test_conditional_node(self):
        """Test the conditional node."""
        context = env.empty_context()
        
        # Test bad conditional error
        bad_conditional = ast.Conditional()
        bad_conditional.add(null_literal) # if None:
        bad_conditional.add(null_literal) # then None
        self.assertRaises(Exception, bad_conditional.eval, context)
        
        # Test correct result
        good_conditional = ast.Conditional()
        good_conditional.add(true_literal)
        good_conditional.add(null_literal)
        self.assertEqual(good_conditional.eval(context), null_literal.value)
        self.assertEqual(good_conditional.__str__(), "<Node (conditional)>")

    def test_branch_node(self):
        """Test the branch node."""
        context = env.empty_context()
        # always evaluates
        true_cond = ast.Conditional()
        true_cond.children = [true_literal, string_literal]
        false_cond = ast.Conditional()
        false_cond.children = [false_literal, null_literal]
        # Test if branch
        if_branch = ast.Branch()
        if_branch.children = [true_cond, null_literal]
        self.assertEqual(if_branch.eval(context), string_literal.value)
        # Test if-else branch
        ifelse_branch = ast.Branch()
        ifelse_branch.children = [false_cond, string_literal]
        self.assertEqual(ifelse_branch.eval(context), string_literal.value)
        # Test if-elif-else branch
        ifelifelse_branch = ast.Branch()
        ifelifelse_branch.children = [false_cond, true_cond, null_literal]
        self.assertEqual(ifelifelse_branch.eval(context), string_literal.value)
        self.assertEqual(if_branch.__str__(), "<Node (branch)>")

    def test_loop_node(self):
        """Test the loop node."""
        break_node = ast.Break()
        return_node = ast.Return()
        return_node.children = [true_literal]
        context = env.empty_context()
        
        # check for exception
        bad_loop = ast.Loop()
        bad_loop.children = [null_literal, true_literal]
        self.assertRaises(Exception, bad_loop.eval, context)
        
        # check for break 
        break_loop = ast.Loop()
        break_loop.children = [true_literal, break_node]
        self.assertEqual(break_loop.eval(context), null_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Default)
        
        # check for return
        return_loop = ast.Loop()
        return_loop.children = [true_literal, return_node]
        self.assertEqual(return_loop.eval(context), true_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Return)
        self.assertEqual(return_loop.__str__(), "<Node (loop)>")

    def test_return_node(self):
        """Test the return node."""
        # test empty return node
        context = env.empty_context()
        empty_return = ast.Return()
        self.assertEqual(empty_return.eval(context), null_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Return)
        
        # test return with value
        context = env.empty_context()
        value_return = ast.Return()
        value_return.add(true_literal)
        self.assertEqual(value_return.eval(context), true_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Return)
        self.assertEqual(value_return.__str__(), "<Node (return)>")

    def test_break_node(self):
        """Test the break node."""
        context = env.empty_context()
        break_node = ast.Break()
        self.assertEqual(break_node.eval(context), null_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Break)
        self.assertEqual(break_node.__str__(), "<Node (break)>")

    def test_continue_node(self):
        """Test the continue node."""
        context = env.empty_context()
        continue_node = ast.Continue()
        self.assertEqual(continue_node.eval(context), null_literal.value)
        self.assertEqual(context.behaviour, ast.Behaviour.Continue)
        self.assertEqual(continue_node.__str__(), "<Node (continue)>")

    def test_call_node(self):
        """Test the function node."""
        # Create sample namespace
        class SumNode(ast.Node):
            name = "sum"
            
            def __init__(self):
                super().__init__()
            
            def eval(self, context):
                s = 0
                for c in self.children: s += c.eval(context).data
                return env.Value(lib.Integer, s)
        
        sum_function = SumNode()
        sgn1 = env.Value(lib.Integer, None, "a")
        sgn2 = env.Value(lib.Integer, None, "b")
        sum_function.children = [
            ast.Identifier("a"),
            ast.Identifier("b"),
        ]
        context = env.empty_context()
        func = env.Function([
            env.Signature([sgn1, sgn2], sum_function),
        ], "my_func")
        context.store(func)
        
        arg1 = SumNode()
        arg1.children = [
            ast.Literal(env.Value(lib.Integer, 1)),
            ast.Literal(env.Value(lib.Integer, 2)),
        ]
        arg2 = SumNode()
        arg2.children = [
            ast.Literal(env.Value(lib.Integer, 3)),
            ast.Literal(env.Value(lib.Integer, 4)),
        ]
        call_node = ast.Call("my_func")
        call_node.children = [arg1, arg2]
        
        self.assertEqual(call_node.eval(context), env.Value(lib.Integer, 10))
        bad_node = ast.Call("missing")
        self.assertRaises(Exception, bad_node.eval, context)
        

    def test_operation_node(self):
        """Test the operation node."""
        # Works completely like the call node
        # Create sample namespace
        class SumNode(ast.Node):
            name = "sum"
            
            def __init__(self):
                super().__init__()
            
            def eval(self, context):
                s = 0
                for c in self.children: s += c.eval(context).data
                return env.Value(lib.Integer, s)
        
        sum_function = SumNode()
        sgn1 = env.Value(lib.Integer, None, "a")
        sgn2 = env.Value(lib.Integer, None, "b")
        sum_function.children = [
            ast.Identifier("a"),
            ast.Identifier("b"),
        ]
        context = env.empty_context()
        func = env.Function([
            env.Signature([sgn1, sgn2], sum_function),
        ])
        op = env.Operator(func, "+")
        context.store(op)
        
        arg1 = SumNode()
        arg1.children = [
            ast.Literal(env.Value(lib.Integer, 1)),
            ast.Literal(env.Value(lib.Integer, 2)),
        ]
        arg2 = SumNode()
        arg2.children = [
            ast.Literal(env.Value(lib.Integer, 3)),
            ast.Literal(env.Value(lib.Integer, 4)),
        ]
        call_node = ast.Operation("+")
        call_node.children = [arg1, arg2]
        
        self.assertEqual(call_node.eval(context), env.Value(lib.Integer, 10))
        bad_node = ast.Operation("?")
        self.assertRaises(Exception, bad_node.eval, context)
        
    def test_cast_node(self):
        """Test the cast node."""
        context = env.empty_context()
        context.store(lib.Integer)
        cast_node = ast.Cast(lib.Integer.name)
        cast_node.children = [null_literal]
        self.assertEqual(cast_node.eval(context), int_literal.value)
        bad_node = ast.Cast("missing")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_identifier_node(self):
        """Test the identifier node."""
        context = env.empty_context()
        # Search in local ns
        context.store(string_literal.value)
        ident_node = ast.Identifier(string_literal.value.name)
        self.assertEqual(ident_node.eval(context), string_literal.value)
        
        # Search in parent ns
        context.substitute()
        self.assertEqual(ident_node.eval(context), string_literal.value)
        
        # Identifier does not exist
        bad_node = ast.Identifier("missing")
        self.assertRaises(Exception, bad_node.eval, context)

    def test_literal_node(self):
        """Test the literal node."""
        context = env.empty_context()
        self.assertEqual(null_literal.eval(context), null_literal.value)
        self.assertEqual(string_literal.eval(context), string_literal.value)
        self.assertEqual(true_literal.eval(context), true_literal.value)
        self.assertEqual(false_literal.eval(context), false_literal.value)
        
    def test_syntax_tree(self):
        """Test the syntax_tree method."""
        syntax_tree = ast.syntax_tree()
        self.assertTrue(syntax_tree is not None)
        self.assertEqual(syntax_tree.name, ast.Sequence.name)
        
    def test_run_in_substitution(self):
        """Test the run_in_substitution method."""
        class AccessNode(ast.Node):
            def __init__(self):
                super().__init__()
                
            def eval(self, context):
                context.store(string_literal.value)
                return string_literal.eval(context)
                
        context = env.empty_context()
        access_node = AccessNode()
        result = ast.run_in_substitution(access_node, context)
        self.assertEqual(result, string_literal.value)
        self.assertRaises(Exception, context.find, "id", string_literal.value.name)