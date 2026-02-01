# Laser Engraving File Converter

A comprehensive Python tool for converting multiple file formats to scalable, high-definition files suitable for laser engraving, with intelligent material suggestions based on use cases.

## Features

- **Multiple Input Formats**: Supports both vector (SVG, DXF, AI, EPS) and raster (PNG, JPG, BMP, TIFF) files
- **High-Quality Output**: Converts to SVG for precise vector work or high-resolution PNG (300+ DPI) for photo engraving
- **Material Suggestions**: Provides research-backed material recommendations based on your use case
- **Batch Processing**: Process multiple files at once
- **Best Practices Guide**: Built-in guidelines for successful laser engraving

## Installation

### Prerequisites

1. **Python 3.7+**: Make sure Python is installed on your system
2. **ImageMagick** (optional): Required for AI/EPS file conversion
   - Ubuntu/Debian: `sudo apt-get install imagemagick`
   - macOS: `brew install imagemagick`
   - Windows: Download from [imagemagick.org](https://imagemagick.org/script/download.php)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

Convert a JPG to SVG for vector engraving:
```bash
python laser_converter.py photo.jpg --output-type svg --use-case photos
```

Convert a DXF design to high-resolution PNG:
```bash
python laser_converter.py design.dxf --output-type png --dpi 600
```

Process multiple files for signage:
```bash
python laser_converter.py logo.png design.svg --output-type svg --use-case signage
```

### Command-Line Options

```
positional arguments:
  input_files           Input file path(s) - supports SVG, DXF, AI, EPS, PNG, JPG, BMP, TIFF

optional arguments:
  -h, --help            Show help message and exit
  --output-type {svg,png}
                        Output format: svg (vector) or png (raster) - default: svg
  --use-case USE_CASE   Use case for material suggestions - default: general
  --dpi DPI             DPI for PNG output (minimum 300 recommended) - default: 300
  --threshold THRESHOLD
                        Threshold for raster-to-vector tracing (0-255) - default: 128
  --best-practices      Show best practices for laser engraving
```

### Use Cases

The program provides material suggestions for these use cases:
- `signage` - Signs, displays, wayfinding
- `jewelry` - Earrings, pendants, accessories
- `personalization` - Custom gifts, names, dates
- `photos` - Photo engraving, portraits
- `general` - All-purpose engraving
- `industrial` - Part marking, labels
- `arts` - Artistic projects, decorative items

## Output Formats

### SVG (Vector)
- **Best for**: Precise lines, cuts, and shapes
- **Advantages**: Infinitely scalable, small file size, clean cuts
- **Recommended for**: Logos, text, geometric designs
- **Materials**: Wood, acrylic, leather, anodized aluminum

### PNG (Raster)
- **Best for**: Photo engraving, shading, gradients
- **Advantages**: Supports grayscale, detailed images
- **Recommended for**: Photographs, complex artwork with shading
- **Materials**: Wood, slate, ceramic, leather

## Material Recommendations

The program provides intelligent material suggestions based on your output format and use case. Examples:

| Use Case | SVG Output | PNG Output |
|----------|------------|------------|
| Signage | Acrylic or plywood | Wood or MDF |
| Photos | Not ideal (use PNG) | Wood, slate, or ceramic |
| Jewelry | Anodized aluminum | Not recommended (use SVG) |
| Personalization | Leather or wood | Slate or leather |

## Best Practices

Run with `--best-practices` flag to see complete guidelines. Key points:

1. **Resolution**: Use 300+ DPI for raster images (600 DPI for fine detail)
2. **Scale**: Work at 1:1 scale in your design
3. **Testing**: ALWAYS test on scrap material first
4. **Safety**: Never use PVC (releases toxic chlorine gas when cut)
5. **Vectors**: Remove overlapping paths to prevent double-cutting
6. **Materials**: Start with basswood - forgiving and affordable

## Technical Details

### File Conversions

- **DXF → SVG**: Converts lines, circles, and arcs using ezdxf
- **AI/EPS → SVG**: Uses ImageMagick via Wand library
- **Raster → SVG**: Simple threshold-based tracing (consider Potrace for production)
- **SVG → PNG**: High-DPI rasterization using cairosvg
- **Raster → PNG**: DPI optimization and format standardization

### Dependencies

- **Pillow**: Image processing and raster handling
- **svgwrite**: SVG creation and editing
- **cairosvg**: SVG to PNG conversion
- **ezdxf**: DXF file parsing and conversion
- **Wand**: AI/EPS handling (requires ImageMagick)

## Limitations & Notes

1. **Raster-to-Vector Tracing**: The built-in tracing is basic. For production work, use dedicated tools like:
   - Potrace: Command-line bitmap tracing
   - Inkscape: GUI with trace bitmap feature
   - Adobe Illustrator: Image Trace feature

2. **AI/EPS Files**: Require ImageMagick installed separately

3. **Large Files**: Very large raster images may create huge SVG files when traced

4. **Complex Vectors**: DXF conversion supports basic entities (lines, circles, arcs). Complex curves may need manual review.

## Workflow Integration

This tool prepares files for laser engraving software:
1. Convert and optimize files with this tool
2. Import results into laser control software:
   - **LightBurn** (recommended)
   - **Inkscape** (free, open source)
   - **LaserGRBL** (for GRBL-based systems)
3. Adjust laser settings (power, speed, passes)
4. Test on scrap material
5. Engrave final piece

## Research & References

Material and technique recommendations are based on:
- Industry best practices from laser engraving professionals
- Material safety guidelines (xometry.com)
- Resolution and scaling requirements (heatsign.com)
- Community tutorials and case studies (YouTube laser engraving channels)

## License

MIT License - Feel free to use and modify for your projects

## Contributing

Contributions welcome! Areas for improvement:
- Advanced vectorization algorithms (integrate Potrace)
- Support for additional file formats
- GUI interface using Tkinter or web-based with Flask
- Preset profiles for common laser engravers
- Material database expansion

## Support

For issues, questions, or suggestions, please open an issue on GitHub. 
