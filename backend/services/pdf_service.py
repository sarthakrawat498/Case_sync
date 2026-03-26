"""
PDF Generation Service
Generates formatted FIR PDF documents using ReportLab.
Supports Hindi (Devanagari) text rendering.
"""

import os
from typing import Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.config import settings


class PDFService:
    """
    PDF generation service for FIR documents.
    Supports bilingual content (Hindi and English).
    """
    
    def __init__(self):
        """Initialize PDF service and register fonts."""
        self.output_dir = settings.PDF_OUTPUT_DIR
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self._register_fonts()
    
    def _register_fonts(self):
        """
        Register fonts for PDF generation.
        Includes Hindi (Devanagari) font support.
        """
        try:
            # Try to register Noto Sans Devanagari for Hindi
            # User needs to download this font or use system font
            font_paths = [
                # Windows paths
                "C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf",
                "C:/Windows/Fonts/Mangal.ttf",
                "C:/Windows/Fonts/arial.ttf",
                # Linux paths
                "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                # Local path
                os.path.join(os.path.dirname(__file__), "fonts", "NotoSansDevanagari-Regular.ttf"),
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('DevanagariFont', font_path))
                        font_registered = True
                        print(f"Registered Hindi font: {font_path}")
                        break
                    except Exception as e:
                        print(f"Could not register font {font_path}: {e}")
                        continue
            
            if not font_registered:
                print("Warning: Hindi font not found. Hindi text may not render correctly.")
                print("Please install Noto Sans Devanagari font.")
            
        except Exception as e:
            print(f"Font registration error: {e}")
    
    def _setup_styles(self):
        """Setup custom paragraph styles for FIR documents."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='FIRTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            textColor=colors.darkblue
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='FIRBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceBefore=5,
            spaceAfter=5
        ))
        
        # Hindi text style
        self.styles.add(ParagraphStyle(
            name='HindiText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            spaceBefore=5,
            spaceAfter=5,
            fontName='DevanagariFont' if 'DevanagariFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=1,
            textColor=colors.grey
        ))
    
    def generate_pdf(
        self,
        fir_content: str,
        case_id: str,
        language: str,
        complainant_name: Optional[str] = None
    ) -> str:
        """
        Generate PDF from FIR content.
        
        Args:
            fir_content: The FIR text content
            case_id: Case identifier
            language: Language code ('hi' or 'en')
            complainant_name: Optional complainant name for filename
            
        Returns:
            str: Path to generated PDF file
        """
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_case_id = str(case_id)[:8].replace('-', '')
        filename = f"FIR_{safe_case_id}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # Build content elements
        elements = self._build_pdf_elements(fir_content, case_id, language)
        
        # Generate PDF
        doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        print(f"PDF generated: {filepath}")
        return filepath
    
    def _build_pdf_elements(self, fir_content: str, case_id: str, language: str) -> list:
        """
        Build PDF elements from FIR content.
        Parses the text-based FIR into structured PDF elements.
        """
        elements = []
        
        # Select text style based on language
        text_style = 'HindiText' if language == 'hi' else 'FIRBody'
        
        # Add title
        title = "प्रथम सूचना रिपोर्ट (FIR)" if language == 'hi' else "FIRST INFORMATION REPORT (FIR)"
        elements.append(Paragraph(title, self.styles['FIRTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add case ID box
        case_info = f"<b>Case ID:</b> {str(case_id)[:8].upper()}"
        elements.append(Paragraph(case_info, self.styles['FIRBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add horizontal line
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
        elements.append(Spacer(1, 0.2*inch))
        
        # Parse and add FIR content sections
        lines = fir_content.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Skip decorative lines
            if line.startswith('===') or line.startswith('---'):
                if current_section:
                    # Flush current section
                    section_text = '<br/>'.join(current_section)
                    try:
                        elements.append(Paragraph(section_text, self.styles[text_style]))
                    except Exception:
                        # Fallback for encoding issues
                        elements.append(Paragraph(section_text, self.styles['FIRBody']))
                    elements.append(Spacer(1, 0.1*inch))
                    current_section = []
                elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
                elements.append(Spacer(1, 0.1*inch))
                continue
            
            # Check for section headers
            if self._is_section_header(line):
                if current_section:
                    section_text = '<br/>'.join(current_section)
                    try:
                        elements.append(Paragraph(section_text, self.styles[text_style]))
                    except Exception:
                        elements.append(Paragraph(section_text, self.styles['FIRBody']))
                    elements.append(Spacer(1, 0.1*inch))
                    current_section = []
                
                elements.append(Paragraph(line, self.styles['SectionHeader']))
                continue
            
            # Escape HTML characters and add to current section
            safe_line = self._escape_html(line)
            current_section.append(safe_line)
        
        # Flush remaining content
        if current_section:
            section_text = '<br/>'.join(current_section)
            try:
                elements.append(Paragraph(section_text, self.styles[text_style]))
            except Exception:
                elements.append(Paragraph(section_text, self.styles['FIRBody']))
        
        # Add footer spacer
        elements.append(Spacer(1, 0.5*inch))
        
        # Add generation notice
        footer_text = f"Generated by CaseSync AI FIR System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(footer_text, self.styles['Footer']))
        
        return elements
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is a section header."""
        header_keywords = [
            'COMPLAINANT', 'INCIDENT', 'PROPERTY', 'WITNESS', 'DECLARATION',
            'POLICE USE', 'FOR OFFICE', 'DETAILS',
            'शिकायतकर्ता', 'घटना', 'संपत्ति', 'गवाह', 'घोषणा', 'पुलिस'
        ]
        
        line_upper = line.upper()
        return any(keyword in line_upper for keyword in header_keywords)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab."""
        replacements = [
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        return text
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.darkblue)
        canvas.drawString(1*cm, A4[1] - 0.8*cm, "CaseSync - AI-Powered FIR Generation System")
        
        # Page number footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 1*cm, 0.8*cm, f"Page {page_num}")
        
        # Confidential notice
        canvas.drawString(1*cm, 0.8*cm, "CONFIDENTIAL - For Official Use Only")
        
        canvas.restoreState()
    
    def get_pdf_path(self, case_id: str) -> Optional[str]:
        """
        Find existing PDF for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Path to PDF if exists, None otherwise
        """
        safe_case_id = str(case_id)[:8].replace('-', '')
        pattern = f"FIR_{safe_case_id}_*.pdf"
        
        # Find matching files
        for filename in os.listdir(self.output_dir):
            if filename.startswith(f"FIR_{safe_case_id}"):
                return os.path.join(self.output_dir, filename)
        
        return None
    
    def delete_pdf(self, filepath: str) -> bool:
        """
        Delete a PDF file.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting PDF: {e}")
        
        return False


# Singleton instance
pdf_service = PDFService()
