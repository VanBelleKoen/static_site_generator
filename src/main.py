import os
import shutil
from textnode import TextNode, TextType
from blockhandler import markdown_to_html_node


def extract_title(markdown):
    """
    Extract the h1 header from a markdown string.
    Returns the header text without the # and whitespace.
    Raises an exception if no h1 header is found.
    """
    lines = markdown.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            # Remove the # and strip whitespace
            return stripped[2:].strip()
    
    raise Exception("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    """
    Generate an HTML page from a markdown file using a template.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, "r") as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, "r") as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Ensure destination directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the HTML file
    with open(dest_path, "w") as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    """
    Recursively generate HTML pages from all markdown files in a directory.
    Maintains the same directory structure in the destination.
    """
    # Get all entries in the content directory
    entries = os.listdir(dir_path_content)
    
    for entry in entries:
        src_path = os.path.join(dir_path_content, entry)
        
        if os.path.isfile(src_path):
            # If it's a markdown file, generate an HTML page
            if entry.endswith(".md"):
                # Convert .md to .html for destination
                html_filename = entry[:-3] + ".html"
                dest_path = os.path.join(dest_dir_path, html_filename)
                
                # Generate the page
                generate_page(src_path, template_path, dest_path)
        else:
            # If it's a directory, create the corresponding directory in dest and recurse
            new_dest_dir = os.path.join(dest_dir_path, entry)
            if not os.path.exists(new_dest_dir):
                os.makedirs(new_dest_dir)
            
            # Recursively process the subdirectory
            generate_pages_recursive(src_path, template_path, new_dest_dir)


def copy_static_to_public(src_dir, dest_dir):
    """
    Recursively copy all contents from src_dir to dest_dir.
    First deletes all contents of dest_dir to ensure a clean copy.
    """
    if os.path.exists(dest_dir):
        print(f"Deleting {dest_dir}...")
        shutil.rmtree(dest_dir)
    
    print(f"Creating {dest_dir}...")
    os.mkdir(dest_dir)
    
    _copy_directory_contents(src_dir, dest_dir)


def _copy_directory_contents(src, dest):
    """
    Helper function to recursively copy directory contents.
    """
    items = os.listdir(src)
    
    for item in items:
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)
        
        if os.path.isfile(src_path):
            print(f"Copying file: {src_path} -> {dest_path}")
            shutil.copy(src_path, dest_path)
        else:
            print(f"Creating directory: {dest_path}")
            os.mkdir(dest_path)
            _copy_directory_contents(src_path, dest_path)


def main():
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    # Copy static files to public directory
    copy_static_to_public(static_dir, public_dir)
    
    # Generate all pages recursively
    generate_pages_recursive(content_dir, template_path, public_dir)


if __name__ == "__main__":
    main()