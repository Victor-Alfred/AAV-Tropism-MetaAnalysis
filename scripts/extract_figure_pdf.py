"""
Simple figure extraction from PDFs
Point to a folder, extract all figures, organize by paper
"""
import fitz  # PyMuPDF
import os
from pathlib import Path

def extract_figures_from_folder(pdf_folder='data/raw/pdfs', 
                                output_base='data/raw/figures',
                                min_width=100,
                                min_height=100):
    """
    Extract figures from all PDFs in a folder
    
    Args:
        pdf_folder (str): Folder containing PDF files
        output_base (str): Base folder for extracted figures
        min_width (int): Minimum image width to extract
        min_height (int): Minimum image height to extract
    """
    
    print("="*70)
    print("FIGURE EXTRACTION FROM PDFs")
    print("="*70)
    
    # Create output folder
    os.makedirs(output_base, exist_ok=True)
    
    # Find all PDFs
    pdf_files = list(Path(pdf_folder).glob('*.pdf'))
    
    if not pdf_files:
        print(f"\n✗ No PDF files found in: {pdf_folder}")
        return
    
    print(f"\nFound {len(pdf_files)} PDF files")
    print(f"Output folder: {output_base}")
    print(f"Minimum image size: {min_width}×{min_height}")
    
    # Process each PDF
    total_figures = 0
    
    for pdf_path in pdf_files:
        # Get PDF name without extension
        pdf_name = pdf_path.stem
        
        # Create folder for this paper
        paper_folder = os.path.join(output_base, pdf_name)
        os.makedirs(paper_folder, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"Processing: {pdf_path.name}")
        print(f"Output: {paper_folder}")
        
        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            print(f"  ✗ Error opening PDF: {e}")
            continue
        
        img_count = 0
        
        # Extract images from each page
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_width = base_image["width"]
                    image_height = base_image["height"]
                    
                    # Skip small images (logos, icons, etc.)
                    if image_width < min_width or image_height < min_height:
                        continue
                    
                    # Create filename: page number + image number
                    filename = f"page{page_index+1:02d}_img{img_index+1:02d}.{image_ext}"
                    filepath = os.path.join(paper_folder, filename)
                    
                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    
                    img_count += 1
                    print(f"  ✓ {filename} ({image_width}×{image_height})")
                    
                except Exception as e:
                    print(f"  ✗ Error extracting image on page {page_index+1}: {e}")
                    continue
        
        doc.close()
        
        print(f"  → Extracted {img_count} figures")
        total_figures += img_count
    
    # Summary
    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"PDFs processed: {len(pdf_files)}")
    print(f"Total figures extracted: {total_figures}")
    print(f"Output location: {output_base}")
    print(f"{'='*70}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract figures from PDFs')
    parser.add_argument('--pdf-folder', type=str, default='data/raw/pdfs',
                       help='Folder containing PDF files (default: data/raw/pdfs)')
    parser.add_argument('--output', type=str, default='data/raw/figures',
                       help='Output folder for figures (default: data/raw/figures)')
    parser.add_argument('--min-width', type=int, default=100,
                       help='Minimum image width (default: 100)')
    parser.add_argument('--min-height', type=int, default=100,
                       help='Minimum image height (default: 100)')
    
    args = parser.parse_args()
    
    extract_figures_from_folder(
        pdf_folder=args.pdf_folder,
        output_base=args.output,
        min_width=args.min_width,
        min_height=args.min_height
    )