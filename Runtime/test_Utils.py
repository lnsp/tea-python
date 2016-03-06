"""Test package for Utils.py."""
import unittest
import Utils


class TestUtils(unittest.TestCase):
    """Test cases for the Utils."""

    def test_tree(self):
        """Test the tree method."""
        t = Utils.tree()
        t["hello"] = 3
        t["foo"]["bar"] = 42
        self.assertEqual(t["hello"], 3)
        self.assertEqual(t["foo"]["bar"], 42)

if __name__ == "__main__":
    unittest.main()
