#!/usr/bin/env python3
"""
OGP Image Generator for Hatena Blog
Generates Open Graph Protocol images from blog post titles with Japanese text support.
"""

import os
import sys
import argparse
import yaml
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

# Constants
OGP_WIDTH = 1200
OGP_HEIGHT = 630
BACKGROUND_COLOR = (70, 130, 180)  # Steel blue similar to Dashscope logo
TEXT_AREA_COLOR = (255, 255, 255)  # White
TEXT_COLOR = (70, 130, 180)  # Same as background for contrast
BLOG_TITLE_COLOR = (255, 255, 255)  # White for blog title
PADDING = 40
TEXT_AREA_MARGIN = 60

# Font settings
FONT_DIR = Path(__file__).parent / "fonts"
FONT_FILE = "NotoSansCJKjp-Regular.otf"
BLOG_TITLE_FONT_SIZE = 48
POST_TITLE_FONT_SIZE = 56


class OGPGenerator:
    def __init__(self, font_path: Path):
        """Initialize OGP generator with font path."""
        self.font_path = font_path
        self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts for blog title and post title."""
        try:
            self.blog_title_font = ImageFont.truetype(
                str(self.font_path), BLOG_TITLE_FONT_SIZE
            )
            self.post_title_font = ImageFont.truetype(
                str(self.font_path), POST_TITLE_FONT_SIZE
            )
        except IOError as e:
            print(f"Error loading font: {e}")
            print(f"Please ensure {FONT_FILE} is in the {FONT_DIR} directory")
            sys.exit(1)
    
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> list:
        """Wrap text to fit within max_width. Handles Japanese text without spaces."""
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        lines = []
        current_line = ""
        
        # For Japanese text, we need to handle character by character
        i = 0
        while i < len(text):
            char = text[i]
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line += char
                i += 1
            else:
                if current_line:
                    # Check if we can break at a better position
                    # Avoid breaking before certain characters
                    no_break_before = "、。！？」』）］｝】〉》"
                    if i < len(text) and text[i] in no_break_before:
                        # Move the punctuation to current line if it fits
                        test_with_punct = current_line + text[i]
                        bbox = draw.textbbox((0, 0), test_with_punct, font=font)
                        if bbox[2] - bbox[0] <= max_width * 1.1:  # Allow slight overflow for punctuation
                            current_line = test_with_punct
                            i += 1
                    
                    lines.append(current_line)
                    current_line = ""
                else:
                    # Single character is too wide (shouldn't happen with normal text)
                    lines.append(char)
                    i += 1
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def generate_ogp_image(self, post_title: str, output_path: Path):
        """Generate OGP image with given post title."""
        # Create base image
        img = Image.new('RGB', (OGP_WIDTH, OGP_HEIGHT), color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Draw white text area
        text_area_top = TEXT_AREA_MARGIN * 2
        text_area_height = OGP_HEIGHT - TEXT_AREA_MARGIN * 3
        text_area_rect = [
            TEXT_AREA_MARGIN,
            text_area_top,
            OGP_WIDTH - TEXT_AREA_MARGIN,
            text_area_top + text_area_height
        ]
        draw.rectangle(text_area_rect, fill=TEXT_AREA_COLOR)
        
        # Draw blog title at the top
        blog_title = "iwashi.co"
        bbox = draw.textbbox((0, 0), blog_title, font=self.blog_title_font)
        blog_title_width = bbox[2] - bbox[0]
        blog_title_x = (OGP_WIDTH - blog_title_width) // 2
        blog_title_y = TEXT_AREA_MARGIN // 2
        draw.text(
            (blog_title_x, blog_title_y),
            blog_title,
            font=self.blog_title_font,
            fill=BLOG_TITLE_COLOR
        )
        
        # Draw post title in the center of text area
        max_text_width = text_area_rect[2] - text_area_rect[0] - PADDING * 2
        wrapped_lines = self._wrap_text(post_title, self.post_title_font, max_text_width)
        
        # Calculate vertical position for centered text
        line_height = POST_TITLE_FONT_SIZE * 1.2
        total_text_height = len(wrapped_lines) * line_height
        text_y = text_area_rect[1] + (text_area_height - total_text_height) // 2
        
        # Draw each line
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=self.post_title_font)
            line_width = bbox[2] - bbox[0]
            line_x = (OGP_WIDTH - line_width) // 2
            draw.text(
                (line_x, text_y),
                line,
                font=self.post_title_font,
                fill=TEXT_COLOR
            )
            text_y += line_height
        
        # Save image
        img.save(output_path, 'PNG', optimize=True)
        print(f"Generated: {output_path}")
    
    def process_markdown_file(self, md_path: Path, output_dir: Path):
        """Process a single markdown file and generate OGP image."""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML front matter
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                print(f"Warning: No front matter found in {md_path}")
                return
            
            # Parse YAML
            front_matter = yaml.safe_load(match.group(1))
            title = front_matter.get('title', '')
            
            if not title:
                print(f"Warning: No title found in {md_path}")
                return
            
            # Generate output filename
            output_filename = md_path.stem + '_ogp.png'
            output_path = output_dir / output_filename
            
            # Generate OGP image
            self.generate_ogp_image(title, output_path)
            
        except Exception as e:
            print(f"Error processing {md_path}: {e}")


def download_font_instructions():
    """Print instructions for downloading the required font."""
    print("\nFont Setup Instructions:")
    print("1. Download Noto Sans CJK JP from: https://github.com/notofonts/noto-cjk/releases")
    print("2. Look for 'NotoSansCJKjp-Regular.otf' in the OTF folder")
    print("3. Create a 'fonts' directory in _tools/")
    print("4. Place the font file in _tools/fonts/")
    print("\nAlternatively, you can download directly:")
    print("wget https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf")


def main():
    parser = argparse.ArgumentParser(
        description='Generate OGP images for blog posts'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Path to markdown file or directory (default: _posts/)'
    )
    parser.add_argument(
        '-o', '--output',
        default='assets/images/ogp',
        help='Output directory for OGP images (default: assets/images/ogp)'
    )
    parser.add_argument(
        '--setup-font',
        action='store_true',
        help='Show font setup instructions'
    )
    
    args = parser.parse_args()
    
    if args.setup_font:
        download_font_instructions()
        return
    
    # Check font file
    font_path = FONT_DIR / FONT_FILE
    if not font_path.exists():
        print(f"Error: Font file not found at {font_path}")
        download_font_instructions()
        sys.exit(1)
    
    # Initialize generator
    generator = OGPGenerator(font_path)
    
    # Setup paths
    if args.input:
        input_path = Path(args.input)
    else:
        # Get the blog root directory
        script_dir = Path(__file__).parent
        blog_root = script_dir.parent
        input_path = blog_root / '_posts'
    
    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = Path(__file__).parent.parent / output_dir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process files
    if input_path.is_file() and input_path.suffix == '.md':
        generator.process_markdown_file(input_path, output_dir)
    elif input_path.is_dir():
        md_files = list(input_path.glob('*.md'))
        print(f"Found {len(md_files)} markdown files")
        for md_file in md_files:
            generator.process_markdown_file(md_file, output_dir)
    else:
        print(f"Error: {input_path} is not a valid markdown file or directory")
        sys.exit(1)


if __name__ == '__main__':
    main()