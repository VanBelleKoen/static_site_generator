# Static Site Generator

A Python-based static site generator that converts Markdown files into a complete static website. This project was built as part of the [Boot.dev](https://boot.dev) Static Site Generator course.

## 🌐 Live Site

The site is deployed at: [https://testteachlead.be](https://testteachlead.be)

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Core Components](#core-components)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Build & Deployment](#build--deployment)
- [Custom Domain Configuration](#custom-domain-configuration)
- [Development](#development)
- [Technical Details](#technical-details)

## Overview

This static site generator takes Markdown content files and transforms them into a fully-functional HTML website. It features:

- **Markdown to HTML conversion** with support for all common Markdown syntax
- **Recursive directory processing** to maintain content structure
- **Template-based page generation** for consistent styling
- **Configurable base paths** for flexible deployment (local development or GitHub Pages)
- **Static asset management** (CSS, images)
- **Custom domain support** via GitHub Pages

## Project Structure

```
static_site_generator/
├── src/                      # Source code
│   ├── main.py              # Main orchestration & page generation
│   ├── htmlnode.py          # HTML node classes (HTMLNode, LeafNode, ParentNode)
│   ├── textnode.py          # Inline markdown parsing (TextNode, TextType)
│   ├── blockhandler.py      # Block-level markdown parsing (BlockType)
│   ├── test_htmlnode.py     # Tests for HTML nodes
│   ├── test_textnode.py     # Tests for text nodes
│   ├── test_blockhandler.py # Tests for block handlers
│   └── test_main.py         # Tests for main functions
├── content/                  # Markdown content files
│   ├── index.md             # Homepage content
│   ├── contact/             # Contact page
│   │   └── index.md
│   └── blog/                # Blog posts
│       ├── glorfindel/
│       ├── tom/
│       └── majesty/
├── static/                   # Static assets (CSS, images, CNAME)
│   ├── index.css
│   ├── CNAME               # Custom domain configuration
│   └── images/
├── docs/                     # Generated output (served by GitHub Pages)
├── template.html            # HTML template with placeholders
├── main.sh                  # Local development script
├── build.sh                 # Production build script
└── test.sh                  # Test runner script
```

## How It Works

### High-Level Flow

1. **Static Asset Copying**: All files from `static/` are recursively copied to `docs/`
2. **Markdown Processing**: All `.md` files in `content/` are discovered recursively
3. **HTML Generation**: Each markdown file is converted to HTML and placed in `docs/` maintaining the directory structure
4. **Template Application**: The HTML content is injected into the template with title extraction
5. **Path Resolution**: All internal links and asset references are adjusted based on the configured basepath

### Detailed Processing Pipeline

```
Markdown File (content/blog/post/index.md)
    ↓
1. Read markdown content
    ↓
2. Split into blocks (markdown_to_blocks)
    ↓
3. Identify block types (heading, paragraph, list, code, quote)
    ↓
4. For each block:
    a. Parse inline markdown (bold, italic, code, links, images)
    b. Create TextNode objects
    c. Convert TextNodes to HTMLNode objects
    d. Build block-specific HTML structure
    ↓
5. Combine all blocks into single HTMLNode tree
    ↓
6. Convert HTMLNode tree to HTML string
    ↓
7. Extract h1 title from markdown
    ↓
8. Inject HTML and title into template
    ↓
9. Replace path prefixes (href="/, src="/) with basepath
    ↓
10. Write to docs/blog/post/index.html
```

## Core Components

### 1. HTML Node System (`htmlnode.py`)

The foundation for building HTML structures programmatically.

**Classes:**
- `HTMLNode`: Base class for all HTML nodes
  - Properties: `tag`, `value`, `children`, `props`
  - Methods: `props_to_html()`, `__repr__()`

- `LeafNode(HTMLNode)`: Represents HTML elements with no children (text, images, links)
  - Examples: `<p>text</p>`, `<a href="...">link</a>`, `<img src="..." />`
  - Method: `to_html()` - renders the element as HTML string

- `ParentNode(HTMLNode)`: Represents HTML elements with children (divs, lists, etc.)
  - Examples: `<div>...</div>`, `<ul><li>...</li></ul>`
  - Method: `to_html()` - recursively renders children

**Example:**
```python
node = ParentNode("div", [
    LeafNode("p", "Hello"),
    LeafNode("a", "Click me", {"href": "/page"})
])
html = node.to_html()
# Output: <div><p>Hello</p><a href="/page">Click me</a></div>
```

### 2. Text Node System (`textnode.py`)

Handles inline markdown parsing (within a single line or paragraph).

**Key Components:**
- `TextType` enum: TEXT, BOLD, ITALIC, CODE, LINK, IMAGE
- `TextNode` class: Represents a chunk of text with a specific type
  - Properties: `text`, `text_type`, `url` (for links/images)

**Functions:**
- `split_nodes_delimiter()`: Splits text on delimiters like `**`, `*`, `` ` ``
- `extract_markdown_images()`: Finds image syntax `![alt](url)` using regex
- `extract_markdown_links()`: Finds link syntax `[text](url)` using regex
- `split_nodes_image()`: Splits TextNodes on image markers
- `split_nodes_link()`: Splits TextNodes on link markers
- `text_to_textnodes()`: Main function that processes all inline markdown in sequence
- `text_node_to_html_node()`: Converts TextNode to HTMLNode (LeafNode)

**Processing Order:**
1. Bold text (`**text**`)
2. Italic text (`*text*`)
3. Code (`\`code\``)
4. Images (`![alt](url)`)
5. Links (`[text](url)`)

### 3. Block Handler System (`blockhandler.py`)

Handles block-level markdown parsing (paragraphs, headings, lists, etc.).

**Key Components:**
- `BlockType` enum: PARAGRAPH, HEADING, CODE, QUOTE, UNORDERED_LIST, ORDERED_LIST

**Functions:**
- `markdown_to_blocks()`: Splits markdown into blocks on `\n\n`
- `block_to_block_type()`: Identifies what type each block is
- `text_to_children()`: Converts inline markdown to list of HTMLNodes
- `markdown_to_html_node()`: Main converter using match/case for block types

**Block Handlers:**
- `_paragraph_to_html()`: Wraps inline content in `<p>` tag
- `_heading_to_html()`: Creates `<h1>` through `<h6>` based on `#` count
- `_code_to_html()`: Wraps code in `<pre><code>` tags
- `_quote_to_html()`: Creates `<blockquote>` from lines starting with `>`
- `_unordered_list_to_html()`: Creates `<ul><li>` from lines starting with `*` or `-`
- `_ordered_list_to_html()`: Creates `<ol><li>` from numbered lines `1. 2. 3.`

### 4. Main Generator (`main.py`)

Orchestrates the entire site generation process.

**Functions:**

- `extract_title(markdown)`: 
  - Extracts the first h1 header (`# Title`) from markdown
  - Raises exception if no h1 found
  - Returns the title text without the `#`

- `generate_page(from_path, template_path, dest_path, basepath="/")`:
  - Reads markdown file
  - Converts markdown to HTML using `markdown_to_html_node()`
  - Extracts title using `extract_title()`
  - Reads template file
  - Replaces `{{ Title }}` and `{{ Content }}` placeholders
  - Replaces `href="/` and `src="/` with configured basepath
  - Creates destination directory if needed
  - Writes final HTML file

- `generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/")`:
  - Lists all entries in content directory
  - For each markdown file: calls `generate_page()`
  - For each subdirectory: creates corresponding directory in dest and recurses
  - Maintains exact directory structure from content to docs

- `copy_static_to_public(src_dir, dest_dir)`:
  - Deletes existing destination directory
  - Recreates empty destination directory
  - Calls `_copy_directory_contents()` to recursively copy all files

- `_copy_directory_contents(src, dest)`:
  - Lists all items in source directory
  - For files: copies using `shutil.copy()`
  - For directories: creates directory and recurses

- `main()`:
  - Reads basepath from `sys.argv[1]` (defaults to `"/"`)
  - Sets up directory paths
  - Copies static assets
  - Generates all pages recursively

## Installation & Setup

### Prerequisites
- Python 3.10+ (requires match/case syntax)
- Git

### Clone Repository
```bash
git clone https://github.com/VanBelleKoen/static_site_generator.git
cd static_site_generator
```

### No Dependencies Required
This project uses only Python standard library modules:
- `os` - file and directory operations
- `shutil` - file copying
- `sys` - command-line arguments
- `re` - regular expressions
- `enum` - enumerations
- `unittest` - testing

## Usage

### Local Development

Generate the site for local testing (uses `/` basepath):
```bash
python3 src/main.py
```

Generate and serve locally:
```bash
sh main.sh
```
Then visit: `http://localhost:8888`

### Run Tests

Run all tests (119 tests across 4 test files):
```bash
sh test.sh
```

Or run specific test files:
```bash
python3 -m unittest src/test_htmlnode.py     # 20 tests
python3 -m unittest src/test_textnode.py     # 54 tests
python3 -m unittest src/test_blockhandler.py # 37 tests
python3 -m unittest src/test_main.py         # 8 tests
```

## Build & Deployment

### Production Build

Build for GitHub Pages (uses `/static_site_generator/` basepath):
```bash
sh build.sh
```

This generates the site into `docs/` with paths configured for GitHub Pages.

### Deploy to GitHub Pages

1. Commit the changes:
```bash
git add .
git commit -m "Update site content"
git push
```

2. GitHub Pages automatically serves from the `docs/` directory on the main branch.

### Basepath Configuration

The generator supports configurable basepaths for different deployment scenarios:

**Local Development:**
```bash
python3 src/main.py
# Uses default basepath: "/"
# Links: href="/blog/post", src="/images/photo.png"
```

**GitHub Pages (subdirectory):**
```bash
python3 src/main.py "/static_site_generator/"
# Links: href="/static_site_generator/blog/post"
```

**Custom Domain:**
```bash
python3 src/main.py "/"
# Custom domains serve from root, so use "/"
```

## Custom Domain Configuration

### 1. Create CNAME File

The CNAME file is already set up in `static/CNAME`:
```
testteachlead.be
```

This file gets copied to `docs/CNAME` during the build process.

### 2. Configure DNS

At your domain registrar, add these DNS records:

**A Records (for apex domain):**
| Type | Name/Host | Value           |
| ---- | --------- | --------------- |
| A    | @         | 185.199.108.153 |
| A    | @         | 185.199.109.153 |
| A    | @         | 185.199.110.153 |
| A    | @         | 185.199.111.153 |

**CNAME Record (for www subdomain - optional):**
| Type  | Name/Host | Value                  |
| ----- | --------- | ---------------------- |
| CNAME | www       | VanBelleKoen.github.io |

### 3. Configure GitHub Pages

1. Go to repository Settings → Pages
2. Under "Custom domain", enter your domain
3. Wait for DNS check to pass (can take up to 48 hours)
4. Enable "Enforce HTTPS"

### 4. Update Build Script for Custom Domain

When using a custom domain, update `build.sh` to use `/` basepath:
```bash
#!/bin/bash
python3 src/main.py "/"
```

## Development

### Adding New Content

1. Create a new markdown file in `content/`:
```bash
mkdir -p content/blog/new-post
nano content/blog/new-post/index.md
```

2. Add markdown content with required h1 header:
```markdown
# My New Post Title

Content goes here with **bold** and *italic* text.

## Subheading

More content...
```

3. Rebuild the site:
```bash
sh main.sh  # For local testing
# or
sh build.sh # For production
```

### Adding Static Assets

1. Add files to `static/` directory:
```bash
cp my-image.png static/images/
```

2. Reference in markdown:
```markdown
![Alt text](/images/my-image.png)
```

3. Rebuild - assets are automatically copied to `docs/`

### Modifying the Template

Edit `template.html` to change the site layout:
```html
<!doctype html>
<html>
  <head>
    <title>{{ Title }}</title>
    <link href="/index.css" rel="stylesheet" />
  </head>
  <body>
    <article>{{ Content }}</article>
  </body>
</html>
```

Placeholders:
- `{{ Title }}` - Replaced with h1 from markdown
- `{{ Content }}` - Replaced with converted HTML

## Technical Details

### Markdown Support

**Inline Elements:**
- Bold: `**text**` → `<b>text</b>`
- Italic: `*text*` → `<i>text</i>`
- Code: `` `code` `` → `<code>code</code>`
- Links: `[text](url)` → `<a href="url">text</a>`
- Images: `![alt](url)` → `<img src="url" alt="alt" />`

**Block Elements:**
- Headings: `# H1` through `###### H6` → `<h1>` through `<h6>`
- Paragraphs: Plain text → `<p>text</p>`
- Code blocks: Triple backticks → `<pre><code>...</code></pre>`
- Quotes: `> text` → `<blockquote>text</blockquote>`
- Unordered lists: `* item` or `- item` → `<ul><li>item</li></ul>`
- Ordered lists: `1. item` → `<ol><li>item</li></ol>`

### Recursive Processing

The generator processes nested directories automatically:

```
content/
├── index.md
├── about/
│   └── index.md
└── blog/
    ├── post1/
    │   └── index.md
    └── post2/
        └── index.md

↓ Generates ↓

docs/
├── index.html
├── about/
│   └── index.html
└── blog/
    ├── post1/
    │   └── index.html
    └── post2/
        └── index.html
```

### HTMLNode Tree Rendering

Example rendering process:

```python
# Creating the tree
parent = ParentNode("div", [
    ParentNode("ul", [
        LeafNode("li", "Item 1"),
        LeafNode("li", "Item 2")
    ])
])

# Rendering (recursive)
parent.to_html()
# → calls children[0].to_html() (the ul)
#   → calls children[0].to_html() (first li)
#     → returns "<li>Item 1</li>"
#   → calls children[1].to_html() (second li)
#     → returns "<li>Item 2</li>"
#   → returns "<ul><li>Item 1</li><li>Item 2</li></ul>"
# → returns "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>"
```

### Test Coverage

The project includes comprehensive test coverage:

- **HTMLNode Tests** (20 tests): Node creation, HTML rendering, prop handling
- **TextNode Tests** (54 tests): Inline markdown parsing, delimiter splitting, regex extraction
- **BlockHandler Tests** (37 tests): Block identification, list parsing, heading levels
- **Main Tests** (8 tests): Title extraction with various edge cases

Run with:
```bash
sh test.sh
```

### Performance Considerations

- **Incremental Building**: Not supported - full rebuild on each run
- **Caching**: No caching - all files regenerated
- **Large Sites**: Scales linearly with number of markdown files
- **Static Assets**: Simple copy operation, no minification or optimization

### Limitations

- No hot reloading in development
- No markdown plugins or extensions
- No image optimization
- No syntax highlighting in code blocks (could be added with CSS)
- No RSS feed generation
- No sitemap generation
- No search functionality

### Future Enhancements

Possible improvements:
- [ ] Incremental builds (only rebuild changed files)
- [ ] Watch mode for development
- [ ] Markdown front matter support (YAML metadata)
- [ ] Syntax highlighting for code blocks
- [ ] RSS feed generation
- [ ] Sitemap.xml generation
- [ ] Tag/category system for blog posts
- [ ] Image optimization and thumbnails
- [ ] Multiple template support
- [ ] Partial/component system
- [ ] Live reload during development

## License

This project was created as part of the Boot.dev curriculum.

## Author

Koen Van Belle

## Acknowledgments

- [Boot.dev](https://boot.dev) for the excellent course material
- J.R.R. Tolkien for inspiration on the sample content
