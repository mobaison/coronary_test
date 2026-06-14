from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import tempfile
from PIL import Image as PILImage
import io
import base64
import cv2
import numpy as np

def generate_report(result_data, report_folder):
    """Generate PDF report for analysis results with images"""
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"coronary_report_{result_data['patient_name'].replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(report_folder, filename)
    
    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
    except:
        pass  # Use default fonts if custom fonts not available
    
    # Create document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Center aligned
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db'),
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor('#2980b9'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        textColor=colors.gray,
        fontName='Helvetica'
    )
    
    # Story elements
    story = []
    
    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("CORONARY ANGIOGRAM ANALYSIS REPORT", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("AI-Powered Stenosis Detection System", subtitle_style))
    story.append(Spacer(1, 2*inch))
    
    # Patient Info Box
    patient_info = [
        ["<b>Patient Name:</b>", result_data['patient_name']],
        ["<b>Report Date:</b>", result_data['timestamp'][:10]],
        ["<b>Report Time:</b>", result_data['timestamp'][11:19]],
        ["<b>Session ID:</b>", result_data['session_id']],
        ["<b>Analysis Status:</b>", 
         "<font color='red'><b>STENOSIS DETECTED</b></font>" if result_data['stenosis_detected'] 
         else "<font color='green'><b>NO STENOSIS DETECTED</b></font>"]
    ]
    
    patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Add page break
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    if result_data['stenosis_detected']:
        summary_text = f"""
        This coronary angiogram analysis reveals <b>{result_data['detection_count']} stenosis location(s)</b> 
        in the coronary arteries. The AI-powered detection system has identified potential narrowing 
        in the coronary vessels that requires clinical evaluation.
        
        <b>Key Findings:</b>
        • {result_data['detection_count']} stenosis location(s) detected
        • Multiple artery segments affected
        • Further quantitative analysis recommended
        """
    else:
        summary_text = """
        This coronary angiogram analysis shows <b>no evidence of coronary artery stenosis</b>.
        
        <b>Key Findings:</b>
        • No stenosis detected in coronary arteries
        • Coronary vessels appear patent
        • Routine follow-up recommended as per clinical guidelines
        """
    
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Image Comparison Section
    story.append(Paragraph("IMAGE ANALYSIS", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Create a table for image comparison
    image_table_data = []
    
    # Original Image
    if 'original_filename' in result_data and result_data['original_filename']:
        original_img_path = os.path.join('data/uploads', result_data['original_filename'])
        if os.path.exists(original_img_path):
            try:
                # Resize image for PDF
                img = PILImage.open(original_img_path)
                img.thumbnail((300, 300))
                
                # Save to temporary file
                temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                img.save(temp_img.name)
                
                original_img = Image(temp_img.name, width=3*inch, height=3*inch)
                image_table_data.append([Paragraph("<b>ORIGINAL ANGIOGRAM</b>", heading_style), 
                                        Paragraph("<b>ANALYSIS RESULT</b>", heading_style)])
                image_table_data.append([original_img, ""])
                
                # Clean up
                os.unlink(temp_img.name)
            except Exception as e:
                print(f"Error processing original image: {e}")
                image_table_data.append([Paragraph("<b>ORIGINAL ANGIOGRAM</b>", heading_style), 
                                        Paragraph("<b>ANALYSIS RESULT</b>", heading_style)])
                image_table_data.append([Paragraph("Image not available", normal_style), ""])
    
    # Processed Image with bounding boxes
    if result_data['stenosis_detected'] and 'processed_filename' in result_data and result_data['processed_filename']:
        processed_img_path = os.path.join('data/results', result_data['processed_filename'])
        if os.path.exists(processed_img_path):
            try:
                # Resize image for PDF
                img = PILImage.open(processed_img_path)
                img.thumbnail((300, 300))
                
                # Save to temporary file
                temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                img.save(temp_img.name)
                
                processed_img = Image(temp_img.name, width=3*inch, height=3*inch)
                
                # Replace the empty cell with processed image
                if image_table_data and len(image_table_data) > 1:
                    image_table_data[1][1] = processed_img
                
                # Clean up
                os.unlink(temp_img.name)
            except Exception as e:
                print(f"Error processing result image: {e}")
                if image_table_data and len(image_table_data) > 1:
                    image_table_data[1][1] = Paragraph("Result image not available", normal_style)
    
    # Create image table
    if image_table_data:
        image_table = Table(image_table_data, colWidths=[3.5*inch, 3.5*inch])
        image_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 6),
        ]))
        story.append(image_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Legend for processed image
    if result_data['stenosis_detected']:
        legend_data = [
            ["", "Detection Legend"],
            ["█", "Stenosis detection boundary box"],
            ["█", "Green box indicates detected stenosis location"],
            ["Stenosis", "Text label on boundary box"]
        ]
        
        legend_table = Table(legend_data, colWidths=[0.5*inch, 6.5*inch])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(legend_table)
    
    story.append(PageBreak())
    
    # Detailed Findings Section
    story.append(Paragraph("DETAILED FINDINGS", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    if result_data['stenosis_detected'] and 'detections' in result_data:
        story.append(Paragraph(f"<b>Total Detections:</b> {result_data['detection_count']}", bold_style))
        story.append(Spacer(1, 0.1*inch))
        
        for i, detection in enumerate(result_data['detections'], 1):
            # Detection Header
            story.append(Paragraph(f"<b>Stenosis Detection #{i}</b>", heading_style))
            
            # Detection Details Table
            det_table_data = [
                ["Parameter", "Value"],
                ["Location (X, Y)", f"{detection['bbox'][0]:.1f}, {detection['bbox'][1]:.1f}"],
                ["Box Size", f"{detection['bbox'][2] - detection['bbox'][0]:.1f} × {detection['bbox'][3] - detection['bbox'][1]:.1f} px"],
                ["Artery Segment", f"Segment {detection['segment'].get('segment_id', 'N/A')} ({detection['segment'].get('segment_name', 'Unknown')})"],
                ["Artery Classification", detection['artery'].get('artery_name', 'Unknown')],
                ["Detection Method", detection['segment'].get('method', 'N/A').replace('_', ' ').title()]
            ]
            
            det_table = Table(det_table_data, colWidths=[2*inch, 5*inch])
            det_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(det_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Artery Summary
        if result_data['detections']:
            arteries = list(set([d['artery'].get('artery_name', 'Unknown') for d in result_data['detections']]))
            story.append(Paragraph("<b>Summary of Affected Arteries:</b>", bold_style))
            arteries_text = ', '.join(arteries) if arteries else "None identified"
            story.append(Paragraph(arteries_text, normal_style))
    
    else:
        story.append(Paragraph("<b>No stenosis detected in this angiogram.</b>", bold_style))
        story.append(Paragraph("The coronary vessels appear patent with no significant narrowing.", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Clinical Recommendations
    story.append(Paragraph("CLINICAL RECOMMENDATIONS", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    if result_data['stenosis_detected']:
        recommendations = [
            "1. Quantitative Coronary Angiography (QCA) recommended for precise measurements",
            "2. Consider fractional flow reserve (FFR) assessment if indicated",
            "3. Clinical correlation with patient symptoms and risk factors",
            "4. Follow-up angiography as per clinical guidelines",
            "5. Consider pharmacological optimization",
            "6. Multi-disciplinary team review recommended"
        ]
    else:
        recommendations = [
            "1. Continue routine clinical follow-up",
            "2. Maintain optimal medical therapy",
            "3. Regular cardiovascular risk assessment",
            "4. Lifestyle modification as appropriate",
            "5. Follow standard preventive cardiology guidelines"
        ]
    
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Limitations
    story.append(Paragraph("LIMITATIONS", heading_style))
    limitations = [
        "• This is an AI-assisted analysis and should be reviewed by a qualified cardiologist",
        "• Image quality may affect detection accuracy",
        "• Does not replace clinical judgment or patient assessment",
        "• Technical limitations in image processing may occur",
        "• Requires validation with other diagnostic modalities"
    ]
    
    for limit in limitations:
        story.append(Paragraph(limit, small_style))
    
    story.append(PageBreak())
    
    # Footer Page
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("--- END OF REPORT ---", 
                          ParagraphStyle('EndStyle', parent=styles['Normal'], 
                                        fontSize=12, alignment=1, 
                                        textColor=colors.gray)))
    story.append(Spacer(1, 0.5*inch))
    
    disclaimer_text = """
    <b>IMPORTANT DISCLAIMER:</b><br/>
    This report is generated by an automated AI system for research and 
    demonstration purposes only. It is not intended for clinical 
    decision-making without review by a qualified medical professional.
    All findings should be correlated with clinical assessment and 
    other diagnostic tests.
    """
    story.append(Paragraph(disclaimer_text, 
                          ParagraphStyle('Disclaimer', parent=styles['Normal'], 
                                        fontSize=9, alignment=1, 
                                        textColor=colors.gray)))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          ParagraphStyle('Timestamp', parent=styles['Normal'], 
                                        fontSize=8, alignment=1, 
                                        textColor=colors.gray)))
    story.append(Paragraph("CoronaryAI Stenosis Detection System v1.0", 
                          ParagraphStyle('Version', parent=styles['Normal'], 
                                        fontSize=8, alignment=1, 
                                        textColor=colors.gray)))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Report generated: {filepath}")
    return filepath