import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

EXPORT_DIR = 'exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

def on_every_page(canvas, doc, footer_text):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    page_num_text = f"Page {canvas.getPageNumber()}"
    canvas.drawString(inch, 0.75 * inch, footer_text)
    canvas.drawRightString(letter[0] - inch, 0.75 * inch, page_num_text)
    canvas.restoreState()

def generate_full_report(volunteers, beneficiaries, programs):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    header = Paragraph("NayePankh Foundation — Management Report", styles['h1'])
    header.style.textColor = colors.white
    header.style.backColor = colors.HexColor('#1565c0')
    header.style.padding = 6
    story.append(header)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y, %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # Summary Table
    summary_data = [
        ['Metric', 'Total'],
        ['Total Volunteers', len(volunteers)],
        ['Total Beneficiaries', len(beneficiaries)],
        ['Total Programs', len(programs)],
        ['Cities Covered', len(set([v.city for v in volunteers] + [b.city for b in beneficiaries]))]
    ]
    summary_table = Table(summary_data, colWidths=[2 * inch, 1 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    # Volunteers Table
    story.append(Paragraph("Volunteers Summary", styles['h2']))
    volunteer_data = [['Name', 'City', 'Status', 'Hours', 'Programs']]
    for v in volunteers:
        volunteer_data.append([v.name, v.city, v.status, v.hours_contributed, v.programs_interested])
    
    volunteer_table = Table(volunteer_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 0.7*inch, 2.5*inch])
    
    # Define a reusable style
    reusable_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ])
    
    volunteer_table.setStyle(reusable_table_style)
    story.append(volunteer_table)
    story.append(Spacer(1, 0.3 * inch))

    # Beneficiaries Table
    story.append(Paragraph("Beneficiaries Summary", styles['h2']))
    beneficiary_data = [['Name', 'Program', 'City', 'Status', 'Score']]
    for b in beneficiaries:
        beneficiary_data.append([b.name, b.program.name, b.city, b.status, b.performance_score or 'N/A'])

    beneficiary_table = Table(beneficiary_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    beneficiary_table.setStyle(reusable_table_style) # reuse style
    story.append(beneficiary_table)
    story.append(Spacer(1, 0.3 * inch))

    # Program Summary
    story.append(Paragraph("Program Summary", styles['h2']))
    program_data = [['Name', 'Enrolled', 'Capacity', 'Status']]
    for p in programs:
        enrolled = len(p.beneficiaries)
        program_data.append([p.name, enrolled, p.capacity, p.status])
    
    program_table = Table(program_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
    program_table.setStyle(reusable_table_style) # reuse style
    story.append(program_table)

    footer_text = "NayePankh Foundation — Confidential"
    doc.build(story, onFirstPage=lambda c, d: on_every_page(c, d, footer_text), onLaterPages=lambda c, d: on_every_page(c, d, footer_text))
    return filename

def generate_volunteer_report(volunteers):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"volunteer_report_{timestamp}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    header = Paragraph("NayePankh Foundation — Volunteer Report", styles['h1'])
    header.style.textColor = colors.white
    header.style.backColor = colors.HexColor('#1565c0')
    header.style.padding = 6
    story.append(header)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Filter Applied: Active Volunteers", styles['Italic']))
    story.append(Spacer(1, 0.3 * inch))

    # Detailed Volunteer Table
    data = [['Name', 'Email', 'Phone', 'City', 'Status', 'Hours']]
    for v in volunteers:
        data.append([v.name, v.email, v.phone, v.city, v.status, v.hours_contributed])
    
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch, 0.8*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(table)

    footer_text = "NayePankh Foundation — Confidential"
    doc.build(story, onFirstPage=lambda c, d: on_every_page(c, d, footer_text), onLaterPages=lambda c, d: on_every_page(c, d, footer_text))
    return filename

def generate_beneficiary_report(beneficiaries):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"beneficiary_report_{timestamp}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    header = Paragraph("NayePankh Foundation — Beneficiary Report", styles['h1'])
    header.style.textColor = colors.white
    header.style.backColor = colors.HexColor('#1565c0')
    header.style.padding = 6
    story.append(header)
    story.append(Spacer(1, 0.3 * inch))

    # Group beneficiaries by program
    from collections import defaultdict
    grouped_beneficiaries = defaultdict(list)
    for b in beneficiaries:
        grouped_beneficiaries[b.program.name].append(b)

    for program_name, ben_list in grouped_beneficiaries.items():
        story.append(Paragraph(f"Program: {program_name}", styles['h2']))
        
        scores = [b.performance_score for b in ben_list if b.performance_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 'N/A'
        story.append(Paragraph(f"Average Performance Score: <b>{avg_score:.2f}</b>" if isinstance(avg_score, float) else "Average Performance Score: <b>N/A</b>", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        data = [['Name', 'City', 'Status', 'Score']]
        for b in ben_list:
            data.append([b.name, b.city, b.status, b.performance_score or 'N/A'])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.honeydew, colors.lightcyan]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

    footer_text = "NayePankh Foundation — Confidential"
    doc.build(story, onFirstPage=lambda c, d: on_every_page(c, d, footer_text), onLaterPages=lambda c, d: on_every_page(c, d, footer_text))
    return filename