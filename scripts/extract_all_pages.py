"""
Ultra-simple: Convert ALL pages to images
No figure detection, just extract everything
"""
import fitz
import os
from pathlib import Path

def extract_all_pages(pdf_folder='data/raw/pdfs',
                     output_folder='data/raw/figures',
                     dpi=300):
    """
    Convert every page of every PDF to an image
    
    Args:
        pdf_folder (str): Folder with PDFs
        output_folder (str): Where to save images
        dpi (int): Resolution
    """
    
    print("="*70)
    print("EXTRACT ALL PAGES AS IMAGES")
    print("="*70)
    
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = list(Path(pdf_folder).glob('*.pdf'))
    print(f"\nFound {len(pdf_files)} PDF files")
    print(f"Resolution: {dpi} DPI\n")
    
    total_pages = 0
    
    for pdf_path in pdf_files:
        pdf_name = pdf_path.stem
        paper_folder = os.path.join(output_folder, pdf_name)
        os.makedirs(paper_folder, exist_ok=True)
        
        print(f"Processing: {pdf_path.name}")
        
        doc = fitz.open(str(pdf_path))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Convert page to image
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save
            filename = f"page{page_num+1:02d}.png"
            filepath = os.path.join(paper_folder, filename)
            pix.save(filepath)
            
            print(f"  ✓ {filename} ({pix.width}×{pix.height})")
            total_pages += 1
        
        doc.close()
    
    print(f"\n✓ Extracted {total_pages} pages total")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract all pages as images')
    parser.add_argument('--pdf-folder', type=str, default='data/raw/pdfs')
    parser.add_argument('--output', type=str, default='data/raw/figures')
    parser.add_argument('--dpi', type=int, default=300)
    
    args = parser.parse_args()
    
    extract_all_pages(args.pdf_folder, args.output, args.dpi)