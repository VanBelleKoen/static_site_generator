from enum import Enum
from textnode import text_to_textnodes, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    """
    Split a markdown document into blocks.
    Blocks are separated by double newlines.
    Leading/trailing whitespace is stripped from each block.
    Empty blocks are removed.
    """
    blocks = markdown.split("\n\n")
    
    result = []
    for block in blocks:
        stripped = block.strip()
        if stripped:
            result.append(stripped)
    
    return result


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    Assumes leading/trailing whitespace has been stripped.
    """
    lines = block.split("\n")
    
    if block.startswith("#"):
        hash_count = 0
        for char in block:
            if char == "#":
                hash_count += 1
            else:
                break
        
        if 1 <= hash_count <= 6 and len(block) > hash_count and block[hash_count] == " ":
            return BlockType.HEADING
    
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    is_ordered = True
    for i, line in enumerate(lines):
        expected_num = i + 1
        expected_prefix = f"{expected_num}. "
        if not line.startswith(expected_prefix):
            is_ordered = False
            break
    
    if is_ordered and len(lines) > 0:
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Convert text with inline markdown to a list of HTMLNode children.
    """
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def _paragraph_to_html(block):
    """Convert a paragraph block to HTML."""
    from htmlnode import ParentNode
    normalized_text = block.replace("\n", " ")
    children = text_to_children(normalized_text)
    return ParentNode("p", children)


def _heading_to_html(block):
    """Convert a heading block to HTML."""
    from htmlnode import ParentNode
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    heading_text = block[level + 1:]
    children = text_to_children(heading_text)
    return ParentNode(f"h{level}", children)


def _code_to_html(block):
    """Convert a code block to HTML."""
    from htmlnode import ParentNode, LeafNode
    code_text = block[3:-3]
    if code_text.startswith("\n"):
        code_text = code_text[1:]
    code_node = LeafNode("code", code_text)
    return ParentNode("pre", [code_node])


def _quote_to_html(block):
    """Convert a quote block to HTML."""
    from htmlnode import ParentNode
    lines = block.split("\n")
    quote_lines = []
    for line in lines:
        if line.startswith("> "):
            quote_lines.append(line[2:])
        else:
            quote_lines.append(line[1:])
    quote_text = "\n".join(quote_lines)
    children = text_to_children(quote_text)
    return ParentNode("blockquote", children)


def _unordered_list_to_html(block):
    """Convert an unordered list block to HTML."""
    from htmlnode import ParentNode
    lines = block.split("\n")
    list_items = []
    for line in lines:
        item_text = line[2:]
        children = text_to_children(item_text)
        list_items.append(ParentNode("li", children))
    return ParentNode("ul", list_items)


def _ordered_list_to_html(block):
    """Convert an ordered list block to HTML."""
    from htmlnode import ParentNode
    lines = block.split("\n")
    list_items = []
    for i, line in enumerate(lines):
        prefix_length = len(f"{i + 1}. ")
        item_text = line[prefix_length:]
        children = text_to_children(item_text)
        list_items.append(ParentNode("li", children))
    return ParentNode("ol", list_items)


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document to a single parent HTMLNode.
    Returns a div containing all the block-level elements.
    """
    from htmlnode import ParentNode
    
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        match block_type:
            case BlockType.PARAGRAPH:
                block_nodes.append(_paragraph_to_html(block))
            case BlockType.HEADING:
                block_nodes.append(_heading_to_html(block))
            case BlockType.CODE:
                block_nodes.append(_code_to_html(block))
            case BlockType.QUOTE:
                block_nodes.append(_quote_to_html(block))
            case BlockType.UNORDERED_LIST:
                block_nodes.append(_unordered_list_to_html(block))
            case BlockType.ORDERED_LIST:
                block_nodes.append(_ordered_list_to_html(block))
    
    return ParentNode("div", block_nodes)
