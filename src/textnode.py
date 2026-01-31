from enum import Enum
from typing import Optional
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: Optional[str] = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (self.text_type, self.text, self.url) == (other.text_type, other.text, other.url)
    
    def __repr__(self):
        return f"TextNode({self.text!r}, {self.text_type!r}, {self.url!r})"


def text_node_to_html_node(text_node):
    from htmlnode import LeafNode
    
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Invalid text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        parts = old_node.text.split(delimiter)
        
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: no closing delimiter found for '{delimiter}'")
        
        for i, part in enumerate(parts):
            if part == "":
                continue
            
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes


def extract_markdown_images(text):
    """
    Extract markdown images from text.
    Returns a list of tuples: (alt_text, url)
    Pattern: ![alt text](url)
    """
    pattern = r"!\[([^\]]*)\]\(([^\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extract markdown links from text.
    Returns a list of tuples: (anchor_text, url)
    Pattern: [anchor text](url) but not ![alt text](url)
    """
    pattern = r"(?<!!)\[([^\]]*)\]\(([^\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    """
    Split nodes based on image markdown syntax.
    Converts TEXT nodes containing ![alt](url) into separate TEXT and IMAGE nodes.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        images = extract_markdown_images(old_node.text)
        
        if not images:
            new_nodes.append(old_node)
            continue
        
        remaining_text = old_node.text
        for alt_text, url in images:
            # Construct the markdown syntax
            markdown = f"![{alt_text}]({url})"
            
            # Split by this markdown (should only split once)
            parts = remaining_text.split(markdown, 1)
            
            if len(parts) != 2:
                raise ValueError(f"Image markdown not found: {markdown}")
            
            # Add text before the image (if not empty)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Continue with remaining text
            remaining_text = parts[1]
        
        # Add any remaining text after the last image
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Split nodes based on link markdown syntax.
    Converts TEXT nodes containing [text](url) into separate TEXT and LINK nodes.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        links = extract_markdown_links(old_node.text)
        
        if not links:
            new_nodes.append(old_node)
            continue
        
        remaining_text = old_node.text
        for anchor_text, url in links:
            # Construct the markdown syntax
            markdown = f"[{anchor_text}]({url})"
            
            # Split by this markdown (should only split once)
            parts = remaining_text.split(markdown, 1)
            
            if len(parts) != 2:
                raise ValueError(f"Link markdown not found: {markdown}")
            
            # Add text before the link (if not empty)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            
            # Continue with remaining text
            remaining_text = parts[1]
        
        # Add any remaining text after the last link
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    """
    Convert raw markdown text to a list of TextNode objects.
    Applies all splitting functions in sequence: bold, italic, code, images, links.
    """
    # Start with a single TEXT node containing all the text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply all the splitting functions in sequence
    # Important: Process ** before * to avoid conflicts
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes
