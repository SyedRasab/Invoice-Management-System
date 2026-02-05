"""
PDF Invoice Generator using ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import config


def generate_invoice_pdf(invoice_data, output_path):
    """
    Generate professional invoice PDF
    
    Args:
        invoice_data: Dictionary containing invoice information
        output_path: Path where PDF should be saved
    
    Returns:
        Path to generated PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555')
    )
    
    # Company Header
    company_name = Paragraph(f"<b>{config.COMPANY_INFO['name']}</b>", title_style)
    elements.append(company_name)
    
    company_details = Paragraph(
        f"{config.COMPANY_INFO['address']}<br/>"
        f"Phone: {config.COMPANY_INFO['phone']} | Email: {config.COMPANY_INFO['email']}",
        ParagraphStyle('CompanyDetails', parent=normal_style, alignment=TA_CENTER)
    )
    elements.append(company_details)
    elements.append(Spacer(1, 0.3*inch))
    
    # Invoice Title
    invoice_title = Paragraph(f"<b>INVOICE</b>", heading_style)
    elements.append(invoice_title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice Info Table
    invoice_info_data = [
        ['Invoice Number:', invoice_data['invoice_number'], 'Date:', invoice_data['date']],
    ]
    
    invoice_info_table = Table(invoice_info_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
    invoice_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ]))
    elements.append(invoice_info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Customer Information
    customer_heading = Paragraph("<b>Bill To:</b>", heading_style)
    elements.append(customer_heading)
    
    customer_data = [
        ['Customer Name:', invoice_data['customer_name']],
        ['Contact:', invoice_data['customer_contact']],
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 5.5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Invoice Details
    details_heading = Paragraph("<b>Invoice Details:</b>", heading_style)
    elements.append(details_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    # Details Table
    details_data = [
        ['Description', 'Quantity', 'Rate', 'Amount'],
        ['Silver Weight', f"{invoice_data['silver_weight']} kg", '', ''],
        ['Piece Size', invoice_data['piece_size'], '', ''],
        ['Number of Pieces', f"{invoice_data['num_pieces']}", '', ''],
        ['Billing Mode', invoice_data['billing_mode'], '', ''],
    ]
    
    # Add rate row based on billing mode
    if invoice_data['billing_mode'] == 'Ready':
        details_data.append(['Silver Rate (per kg)', '', f"$ {invoice_data['rate']:,.2f}", ''])
    else:  # Mazduri
        details_data.append(['Mazduri Rate (per piece)', '', f"$ {invoice_data['rate']:,.2f}", ''])
    
    details_table = Table(details_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    details_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment Summary
    payment_heading = Paragraph("<b>Payment Summary:</b>", heading_style)
    elements.append(payment_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    payment_data = [
        ['Total Amount:', f"$ {invoice_data['total_amount']:,.2f}"],
        ['Advance Payment:', f"$ {invoice_data['advance_payment']:,.2f}"],
        ['Remaining Balance:', f"$ {invoice_data['remaining_balance']:,.2f}"],
    ]
    
    payment_table = Table(payment_data, colWidths=[5*inch, 2.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#d9534f')),
        ('FONTSIZE', (0, 2), (-1, 2), 13),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#333333')),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = Paragraph(
        "<i>Thank you for your business!</i>",
        ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=9)
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    return output_path


if __name__ == '__main__':
    # Test PDF generation
    test_data = {
        'invoice_number': 'INV-20260205001',
        'date': '2026-02-05',
        'customer_name': 'Test Customer',
        'customer_contact': '+1 234 567 8900',
        'silver_weight': 10.0,
        'piece_size': '1 kg',
        'num_pieces': 10.0,
        'billing_mode': 'Ready',
        'rate': 75000.00,
        'total_amount': 750000.00,
        'advance_payment': 100000.00,
        'remaining_balance': 650000.00
    }
    
    generate_invoice_pdf(test_data, 'test_invoice.pdf')
    print("Test PDF generated successfully!")
