import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_multiple_attributes(self):
        node = HTMLNode(
            tag="a",
            value="Click me",
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_single_attribute(self):
        node = HTMLNode(tag="img", props={"src": "image.jpg"})
        expected = ' src="image.jpg"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_no_props(self):
        node = HTMLNode(tag="p", value="Hello, world!")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_empty_props(self):
        node = HTMLNode(tag="div", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        node = HTMLNode(tag="p", value="Test paragraph")
        result = repr(node)
        self.assertIn("tag='p'", result)
        self.assertIn("value='Test paragraph'", result)

    def test_to_html_raises_not_implemented(self):
        node = HTMLNode(tag="div")
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just raw text")
        self.assertEqual(node.to_html(), "Just raw text")

    def test_leaf_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_to_html_span(self):
        node = LeafNode("span", "Text content")
        self.assertEqual(node.to_html(), "<span>Text content</span>")

    def test_leaf_to_html_img_with_props(self):
        node = LeafNode("img", "alt text", {"src": "image.jpg", "alt": "An image"})
        self.assertEqual(node.to_html(), '<img src="image.jpg" alt="An image">alt text</img>')

    def test_leaf_repr(self):
        node = LeafNode("p", "Test")
        result = repr(node)
        self.assertIn("tag='p'", result)
        self.assertIn("value='Test'", result)
        self.assertNotIn("children", result)


class TestParentNode(unittest.TestCase):
    def test_parent_to_html_simple(self):
        node = ParentNode(
            "p",
            [
                LeafNode(None, "Hello, "),
                LeafNode("b", "world"),
                LeafNode(None, "!"),
            ],
        )
        self.assertEqual(node.to_html(), "<p>Hello, <b>world</b>!</p>")

    def test_parent_to_html_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [
                        LeafNode("b", "Bold text"),
                    ],
                ),
                LeafNode("span", "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), "<div><p><b>Bold text</b></p><span>Normal text</span></div>")

    def test_parent_to_html_with_props(self):
        node = ParentNode(
            "div",
            [
                LeafNode("p", "Paragraph"),
            ],
            {"class": "container", "id": "main"},
        )
        self.assertEqual(node.to_html(), '<div class="container" id="main"><p>Paragraph</p></div>')

    def test_parent_no_tag_raises_error(self):
        node = ParentNode(None, [LeafNode("p", "text")])
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertIn("tag", str(context.exception).lower())

    def test_parent_no_children_raises_error(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertIn("children", str(context.exception).lower())

    def test_parent_deeply_nested(self):
        node = ParentNode(
            "html",
            [
                ParentNode(
                    "body",
                    [
                        ParentNode(
                            "div",
                            [
                                LeafNode("p", "Deep content"),
                            ],
                        ),
                    ],
                ),
            ],
        )
        self.assertEqual(node.to_html(), "<html><body><div><p>Deep content</p></div></body></html>")

    def test_parent_repr(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        result = repr(node)
        self.assertIn("tag='div'", result)
        self.assertIn("children=", result)
        self.assertTrue(result.startswith("ParentNode"))


if __name__ == "__main__":
    unittest.main()
