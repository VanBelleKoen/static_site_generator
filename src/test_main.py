import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from main import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_simple_h1(self):
        markdown = "# Hello"
        self.assertEqual(extract_title(markdown), "Hello")
    
    def test_h1_with_extra_whitespace(self):
        markdown = "#   Hello World   "
        self.assertEqual(extract_title(markdown), "Hello World")
    
    def test_h1_with_surrounding_content(self):
        markdown = """Some text before

# Main Title

Some text after"""
        self.assertEqual(extract_title(markdown), "Main Title")
    
    def test_h1_with_h2_after(self):
        markdown = """# Title One

## Title Two"""
        self.assertEqual(extract_title(markdown), "Title One")
    
    def test_no_h1_raises_exception(self):
        markdown = "## This is only h2\n\nSome content"
        with self.assertRaises(Exception) as context:
            extract_title(markdown)
        self.assertIn("No h1 header found", str(context.exception))
    
    def test_empty_markdown_raises_exception(self):
        markdown = ""
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_h1_at_end(self):
        markdown = """Some content

More content

# The Title"""
        self.assertEqual(extract_title(markdown), "The Title")
    
    def test_h1_with_special_characters(self):
        markdown = "# Hello **World** & Friends!"
        self.assertEqual(extract_title(markdown), "Hello **World** & Friends!")


if __name__ == "__main__":
    unittest.main()
