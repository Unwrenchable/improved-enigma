# Laser Engraving File Converter

A comprehensive Python program for handling file conversions for laser engraving projects. This tool accepts multiple input file types, outputs scalable high-definition files, and suggests materials based on use cases.

## Features

- **Multi-format Input Support**
  - Vector formats: SVG, DXF, AI, EPS
  - Raster formats: PNG, JPG, BMP, TIFF
  
- **High-Quality Output**
  - Scalable vector graphics (SVG) for vector inputs
  - High-resolution PNG for raster inputs
  - Customizable DPI settings (default: 300 DPI)
  
- **Material Suggestions**
  - Intelligent material recommendations based on use cases
  - Support for decorative, functional, jewelry, signage, prototype, and detailed engraving projects
  - Comprehensive material database with descriptions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Unwrenchable/improved-enigma.git
cd improved-enigma
```

2. Make the script executable (optional):
```bash
chmod +x laser_engraver.py
```

3. For full conversion capabilities, install optional dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic File Conversion

Convert a vector file to SVG:
```bash
python laser_engraver.py -i design.dxf -o output.svg
```

Convert a raster file to high-resolution PNG:
```bash
python laser_engraver.py -i photo.jpg -o output.png --dpi 600
```

### File Information

Get information about a file:
```bash
python laser_engraver.py -i myfile.svg --info
```

### Material Suggestions

Get material recommendations for a specific use case:
```bash
python laser_engraver.py --suggest-material decorative
python laser_engraver.py --suggest-material jewelry
python laser_engraver.py --suggest-material signage
```

List all available use cases:
```bash
python laser_engraver.py --list-use-cases
```

### Advanced Options

Specify custom DPI for raster output:
```bash
python laser_engraver.py -i photo.jpg -o output.png --dpi 600
```

Set maximum dimension for raster output:
```bash
python laser_engraver.py -i large_image.tiff -o output.png --max-dimension 8192
```

## Supported Formats

### Input Formats

**Vector Formats:**
- `.svg` - Scalable Vector Graphics
- `.dxf` - AutoCAD Drawing Exchange Format
- `.ai` - Adobe Illustrator
- `.eps` - Encapsulated PostScript

**Raster Formats:**
- `.png` - Portable Network Graphics
- `.jpg` / `.jpeg` - Joint Photographic Experts Group
- `.bmp` - Bitmap
- `.tiff` / `.tif` - Tagged Image File Format

### Output Formats

- **SVG** - For vector inputs (scalable, high-definition)
- **PNG** - For raster inputs (high-resolution, configurable DPI)

## Material Suggestions

The tool includes an intelligent material suggestion system for various use cases:

1. **Decorative** - Wood, Acrylic, Leather, Cork
2. **Functional** - MDF, Plywood, Hardwood, Aluminum, Stainless Steel
3. **Jewelry** - Acrylic, Thin Wood, Leather, Anodized Aluminum
4. **Signage** - Acrylic, Wood, Aluminum Composite, HDU
5. **Prototype** - Cardboard, Foam Board, MDF, Acrylic
6. **Detailed Engraving** - Hardwood, Anodized Aluminum, Glass, Marble

## Command-Line Options

```
usage: laser_engraver.py [-h] [-i INPUT] [-o OUTPUT] [--dpi DPI]
                         [--max-dimension MAX_DIMENSION]
                         [--suggest-material SUGGEST_MATERIAL]
                         [--list-use-cases] [--info]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file path
  -o OUTPUT, --output OUTPUT
                        Output file path (default: auto-generated)
  --dpi DPI             Target DPI for raster output (default: 300)
  --max-dimension MAX_DIMENSION
                        Maximum dimension for raster output (default: 4096)
  --suggest-material SUGGEST_MATERIAL
                        Get material suggestions for a use case
  --list-use-cases      List all available use cases
  --info                Display file information only
```

## Examples

### Example 1: Convert DXF to SVG
```bash
python laser_engraver.py -i mechanical_part.dxf -o laser_ready.svg
```

### Example 2: Prepare High-Res Image for Engraving
```bash
python laser_engraver.py -i logo.jpg -o logo_hires.png --dpi 600
```

### Example 3: Get Material Suggestions for Jewelry
```bash
python laser_engraver.py --suggest-material jewelry
```

Output:
```
============================================================
Material Suggestions for: JEWELRY
============================================================

Best for jewelry items like pendants, earrings, bracelets

Recommended Materials:
  1. Acrylic
  2. Wood (Thin)
  3. Leather
  4. Anodized Aluminum

============================================================
```

### Example 4: Check File Information
```bash
python laser_engraver.py -i design.svg --info
```

Output:
```
============================================================
File Information: design.svg
============================================================
Extension: .svg
Size: 0.15 MB (157,340 bytes)
Type: Vector
Supported: Yes
============================================================
```

## Technical Notes

### Current Implementation

The current version provides a robust framework with:
- File format detection and validation
- Material suggestion system
- File information utilities
- Basic SVG and PNG handling

### Production Enhancement

For full production conversion capabilities, the code includes guidance for integrating:
- **PIL/Pillow** - Advanced raster image processing
- **ezdxf** - DXF file reading and writing
- **svgwrite** - SVG generation and manipulation
- **cairosvg** - SVG rendering and conversion
- **Inkscape CLI** - AI/EPS conversion

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License. 
