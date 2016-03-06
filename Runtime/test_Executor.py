"""Run tests on Executor."""
import unittest
import Executor


class TestExecutor(unittest.TestCase):
    """Test cases for the Executor."""

    def test_syntax_tree(self):
        """Test the syntax_tree method."""
        syntax_tree = Executor.syntax_tree()
        self.assertTrue(syntax_tree is not None)
        self.assertEqual(syntax_tree.type, Executor.TYPES[Executor._SEQUENCE])

if __name__ == "__main__":
    unittest.main()
