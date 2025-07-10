#!/bin/bash
# Download Noto Sans CJK JP font for OGP generation

FONT_DIR="$(dirname "$0")/fonts"
FONT_URL="https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
FONT_FILE="NotoSansCJKjp-Regular.otf"

echo "Creating font directory..."
mkdir -p "$FONT_DIR"

echo "Downloading Noto Sans CJK JP Regular font..."
cd "$FONT_DIR"

if command -v wget &> /dev/null; then
    wget -O "$FONT_FILE" "$FONT_URL"
elif command -v curl &> /dev/null; then
    curl -L -o "$FONT_FILE" "$FONT_URL"
else
    echo "Error: Neither wget nor curl is installed."
    echo "Please install one of them or download the font manually from:"
    echo "$FONT_URL"
    exit 1
fi

if [ -f "$FONT_FILE" ]; then
    echo "Font downloaded successfully to: $FONT_DIR/$FONT_FILE"
else
    echo "Error: Failed to download font"
    exit 1
fi