from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .paths import user_path

OUTPUT_DIR = user_path("output", "placeholder").parent
OUTPUT_DIR.mkdir(exist_ok=True)


def _safe_text(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "≤": "<=",
        "≥": ">=",
        "×": "x",
        "℃": "C",
        "°": "",
        "\u2011": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\ufffd": "",
    }
    for src, dest in replacements.items():
        text = text.replace(src, dest)
    return text


def _hex_color(value: str, fallback: str = "#6dbb43") -> colors.Color:
    try:
        return colors.HexColor(value or fallback)
    except Exception:
        return colors.HexColor(fallback)


def _field_value(data: Dict[str, Any], *names: str) -> str:
    lookup = {str(k).strip().lower(): str(v).strip() for k, v in data.get("product_fields", [])}
    for name in names:
        value = lookup.get(name.lower())
        if value:
            return value
    return ""


def _paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe_text(text).replace("\n", "<br/>"), style)


def _make_table(data: List[List[Any]], widths: List[float], style: TableStyle, repeat_rows: int = 0) -> Table:
    tbl = Table(data, colWidths=widths, repeatRows=repeat_rows, hAlign="CENTER")
    tbl.setStyle(style)
    return tbl


def _draw_page_frame(canvas, doc, data: Dict[str, Any]) -> None:
    page_width, page_height = A4
    border = colors.HexColor("#6dbb43")
    canvas.saveState()
    canvas.setStrokeColor(border)
    canvas.setLineWidth(2.0)
    inset = 7 * mm
    canvas.roundRect(inset, inset, page_width - 2 * inset, page_height - 2 * inset, 4 * mm, stroke=True, fill=False)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(18 * mm, 18 * mm, _safe_text(data.get("footer_left_1", "Electronic document valid without signature.")))
    canvas.drawString(18 * mm, 14.5 * mm, _safe_text(data.get("footer_left_2", "Copyright © All rights reserved.")))
    canvas.setFillColor(colors.HexColor("#242424"))
    canvas.setFont("Helvetica", 8.5)
    right_1 = _safe_text(data.get("footer_right_1", "Department of Quality Control"))
    right_2 = _safe_text(data.get("footer_right_2", "www.medikonda.com"))
    canvas.drawRightString(page_width - 18 * mm, 18 * mm, right_1)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("Helvetica", 7.2)
    canvas.drawRightString(page_width - 18 * mm, 14.5 * mm, right_2)
    canvas.restoreState()


def _generate_generic_document_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    batch = _field_value(data, "Batch #", "Batch Number") or ""
    title = _safe_text(data.get("document_title", "DOCUMENT")).replace(" ", "_")
    if output_path is None:
        safe_name = f"{title}_{sku}_{batch}.pdf".strip("_").replace("/", "-").replace(" ", "_")
        output_path = OUTPUT_DIR / safe_name
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")
    light_line = colors.HexColor("#b6b6b6")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=24 * mm,
    )

    styles = getSampleStyleSheet()
    normal = ParagraphStyle("normal", parent=styles["Normal"], fontName="Helvetica", fontSize=8.2, leading=10, textColor=dark)
    normal_bold = ParagraphStyle("normal_bold", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("heading", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, alignment=1, textColor=dark, spaceAfter=14)
    brand = ParagraphStyle("brand", parent=styles["Title"], fontName="Helvetica", fontSize=30, leading=31, alignment=1, textColor=border, spaceAfter=0)
    website = ParagraphStyle("website", parent=normal, fontSize=10, leading=11, alignment=1, textColor=border, spaceAfter=8)
    section_title = ParagraphStyle("section_title", parent=normal_bold, fontSize=8.6, leading=10, textColor=dark)
    footer_style = ParagraphStyle("footer", parent=normal, fontSize=7.2, leading=9, textColor=colors.HexColor("#555555"))

    story = []

    logo_path = Path(data.get("logo_path", "")) if data.get("logo_path") else None
    if logo_path and logo_path.exists():
        try:
            img = Image(str(logo_path))
            max_w = 55 * mm
            max_h = 22 * mm
            scale = min(max_w / float(img.imageWidth), max_h / float(img.imageHeight), 1.0)
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 2 * mm))
        except Exception:
            story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))

    if data.get("website"):
        story.append(_paragraph(data.get("website", "www.medikonda.com"), website))
    story.append(_paragraph(data.get("document_title", "DOCUMENT"), heading))

    fields = data.get("product_fields", [])
    field_rows = [[_paragraph("PRODUCTS", normal_bold), _paragraph("INFORMATION", normal_bold)]]
    for idx, row in enumerate(fields):
        if not any(str(cell).strip() for cell in row):
            continue
        label = row[0] if len(row) > 0 else ""
        value = row[1] if len(row) > 1 else ""
        field_rows.append([_paragraph(label, normal), _paragraph(value, normal)])
    if len(field_rows) > 1:
        field_tbl = _make_table(
            field_rows,
            [45 * mm, 64 * mm],
            TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]),
        )
        story.append(field_tbl)
        story.append(Spacer(1, 10 * mm))

    for section in data.get("sections", []):
        title_text = section.get("title", "Section")
        columns = [str(c or "") for c in section.get("columns", [])]
        rows = section.get("rows", [])
        if not columns:
            columns = ["Column 1", "Column 2", "Column 3", "Column 4"]
        filtered_rows = [r for r in rows if any(str(cell).strip() for cell in r)]
        if not filtered_rows:
            continue

        table_data = [[_paragraph(title_text, section_title)] + ["" for _ in columns[1:]]]
        table_data.append([_paragraph(col, normal_bold) for col in columns])
        for row in filtered_rows:
            padded = list(row) + [""] * max(0, len(columns) - len(row))
            table_data.append([_paragraph(cell, normal) for cell in padded[: len(columns)]])

        total_w = A4[0] - doc.leftMargin - doc.rightMargin
        if len(columns) == 1:
            widths = [total_w]
        elif len(columns) == 2:
            widths = [total_w * 0.38, total_w * 0.62]
        elif len(columns) == 3:
            widths = [total_w * 0.36, total_w * 0.40, total_w * 0.24]
        else:
            first = total_w * 0.34
            last = total_w * 0.22
            middle_total = total_w - first - last
            widths = [first] + [middle_total / (len(columns) - 2)] * (len(columns) - 2) + [last]

        tbl = _make_table(
            table_data,
            widths,
            TableStyle([
                ("SPAN", (0, 0), (-1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), grey),
                ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                ("FONT", (0, 0), (-1, 1), "Helvetica-Bold", 8),
                ("GRID", (0, 0), (-1, -1), 0.4, light_line),
                ("LINEABOVE", (0, 0), (-1, 0), 0.8, dark),
                ("LINEBELOW", (0, -1), (-1, -1), 0.8, dark),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]),
            repeat_rows=2,
        )
        story.append(tbl)
        story.append(Spacer(1, 6 * mm))

    story.append(Spacer(1, 4 * mm))

    doc.build(story, onFirstPage=lambda canv, d: _draw_page_frame(canv, d, data), onLaterPages=lambda canv, d: _draw_page_frame(canv, d, data))
    return Path(output_path)


# Backward compatibility for earlier MVP button names/imports.
def generate_coa_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    return generate_document_pdf(data, output_path)



def _float_mm(value: Any, fallback: float) -> float:
    try:
        return float(str(value).strip() or fallback)
    except Exception:
        return fallback


def _prepared_logo_path(path: Path) -> Path:
    """Crop transparent/empty padding from the logo so the visible mark sizes consistently."""
    try:
        from PIL import Image as PILImage
        im = PILImage.open(path).convert("RGBA")
        bbox = im.getchannel("A").getbbox() or im.getbbox()
        if not bbox:
            return path
        cropped = im.crop(bbox)
        out = OUTPUT_DIR / (path.stem + "_cropped.png")
        cropped.save(out)
        return out
    except Exception:
        return path


def _logo_flowable(data: Dict[str, Any], default_w_mm: float = 55, default_h_mm: float = 22):
    logo_path = Path(data.get("logo_path", "")) if data.get("logo_path") else None
    if logo_path and not logo_path.is_absolute():
        logo_path = Path(__file__).resolve().parent.parent / logo_path
    if not logo_path or not logo_path.exists():
        return None
    logo_path = _prepared_logo_path(logo_path)
    try:
        img = Image(str(logo_path))
        max_w = _float_mm(data.get("logo_width_mm"), default_w_mm) * mm
        max_h = _float_mm(data.get("logo_height_mm"), default_h_mm) * mm
        scale = min(max_w / float(img.imageWidth), max_h / float(img.imageHeight), 1.0)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        img.hAlign = "CENTER"
        return img
    except Exception:
        return None


def _standard_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey, dark) -> Table:
    columns = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    if not columns:
        columns = ["Parameter", "Specification", "Results", "Test Methods"]
    first_header = section.get("title", columns[0]).upper()
    header = [first_header] + [c.upper() for c in columns[1:]]
    data_rows = [[_paragraph(c, bold) for c in header]]
    for row in rows:
        padded = list(row) + [""] * max(0, len(columns) - len(row))
        data_rows.append([_paragraph(cell, normal) for cell in padded[: len(columns)]])
    if len(columns) >= 4:
        widths = [total_w * 0.34, total_w * 0.30, total_w * 0.22, total_w * 0.14]
    elif len(columns) == 3:
        widths = [total_w * 0.36, total_w * 0.40, total_w * 0.24]
    else:
        widths = [total_w / len(columns)] * len(columns)
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return tbl


def _generate_standard_coa_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    batch = _field_value(data, "Batch #", "Batch Number") or ""
    if output_path is None:
        output_path = OUTPUT_DIR / f"CERTIFICATE_OF_ANALYSIS_{sku}_{batch}.pdf".replace("__", "_")
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=12 * mm, bottomMargin=24 * mm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("std_normal", parent=styles["Normal"], fontName="Helvetica", fontSize=10.0, leading=12.0, textColor=dark)
    bold = ParagraphStyle("std_bold", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("std_heading", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17.0, leading=19, alignment=1, textColor=dark, spaceAfter=18)
    brand = ParagraphStyle("std_brand", parent=styles["Title"], fontName="Helvetica", fontSize=30, leading=31, alignment=1, textColor=border, spaceAfter=0)
    website = ParagraphStyle("std_web", parent=normal, fontSize=12.0, leading=13, alignment=1, textColor=border, spaceAfter=9)

    story: List[Any] = []
    logo = _logo_flowable(data, 70, 26)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 1.2 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    story.append(_paragraph(data.get("document_title", "CERTIFICATE OF ANALYSIS"), heading))

    fields = [row for row in data.get("product_fields", []) if any(str(x).strip() for x in row)]
    field_rows = [[_paragraph("PRODUCTS", bold), _paragraph("INFORMATION", bold)]]
    for row in fields:
        field_rows.append([_paragraph(row[0] if len(row) > 0 else "", normal), _paragraph(row[1] if len(row) > 1 else "", normal)])
    field_tbl = Table(field_rows, colWidths=[55 * mm, 55 * mm], hAlign="LEFT")
    field_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(field_tbl)
    story.append(Spacer(1, 10 * mm))

    total_w = A4[0] - doc.leftMargin - doc.rightMargin
    for idx, section in enumerate(data.get("sections", [])):
        rows = section.get("rows", [])
        if not rows or not any(any(str(cell).strip() for cell in r) for r in rows):
            continue
        story.append(_standard_section_table(section, total_w, normal, bold, grey, dark))
        if idx != len(data.get("sections", [])) - 1:
            story.append(Spacer(1, 8 * mm))

    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)


def _compact_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey, dark) -> Table:
    columns = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    data_rows = [[_paragraph(section.get("title", "Section"), bold)] + ["" for _ in columns[1:]]]
    data_rows.append([_paragraph(c, bold) for c in columns])
    for r in rows:
        padded = list(r) + [""] * max(0, len(columns) - len(r))
        data_rows.append([_paragraph(cell, normal) for cell in padded[:len(columns)]])
    if len(columns) == 4:
        widths = [total_w * 0.22, total_w * 0.30, total_w * 0.23, total_w * 0.25]
    elif len(columns) == 3:
        widths = [total_w * 0.34, total_w * 0.36, total_w * 0.30]
    else:
        widths = [total_w / max(1, len(columns))] * len(columns)
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), grey),
        ("FONT", (0, 0), (-1, 1), "Helvetica-Bold", 6.4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b0b0b0")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, dark),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, dark),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
    ]))
    return tbl


def _generate_probiotics_spec_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    if output_path is None:
        output_path = OUTPUT_DIR / f"PRODUCT_SPECIFICATION_{sku}.pdf"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("pro_normal", parent=styles["Normal"], fontName="Helvetica", fontSize=6.3, leading=7.2, textColor=dark)
    bold = ParagraphStyle("pro_bold", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("pro_heading", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14.5, leading=16, alignment=1, textColor=dark, spaceAfter=6)
    website = ParagraphStyle("pro_web", parent=normal, fontSize=8.5, leading=9, alignment=1, textColor=border, spaceAfter=5)
    brand = ParagraphStyle("pro_brand", parent=styles["Title"], fontName="Helvetica", fontSize=28, leading=30, alignment=1, textColor=border)
    story: List[Any] = []
    logo = _logo_flowable(data, 52, 18)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 0.8 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    story.append(_paragraph(data.get("document_title", "PRODUCT SPECIFICATION"), heading))

    fields = [row for row in data.get("product_fields", []) if any(str(x).strip() for x in row)]
    frows = []
    for row in fields:
        frows.append([_paragraph(row[0] if len(row)>0 else "", bold), _paragraph(row[1] if len(row)>1 else "", normal)])
    if frows:
        ft = Table(frows, colWidths=[42 * mm, 72 * mm], hAlign="LEFT")
        ft.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [grey, colors.white]),
            ("LINEABOVE", (0, 0), (-1, 0), 0.7, dark),
            ("LINEBELOW", (0, -1), (-1, -1), 0.7, dark),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ]))
        story.append(ft)
        story.append(Spacer(1, 6 * mm))
    total_w = A4[0] - doc.leftMargin - doc.rightMargin - 4 * mm
    sections = data.get("sections", [])
    for idx, section in enumerate(sections):
        rows = section.get("rows", [])
        if not rows or not any(any(str(cell).strip() for cell in r) for r in rows):
            continue
        story.append(_compact_section_table(section, total_w, normal, bold, grey, dark))
        story.append(Spacer(1, 3 * mm if idx < len(sections)-1 else 1 * mm))
    note = _paragraph("*Do not exceed 25C during handling or transit to preserve viability of live probiotic.", normal)
    story.append(note)
    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)


def generate_document_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    template = str(data.get("template_name", ""))
    title = str(data.get("document_title", ""))
    if "Probiotics" in template or "PRODUCT SPECIFICATION" in title.upper():
        return _generate_probiotics_spec_pdf(data, output_path)
    if template.startswith("Standard COA") or "CERTIFICATE OF ANALYSIS" in title.upper():
        return _generate_standard_coa_pdf(data, output_path)
    return _generate_generic_document_pdf(data, output_path)

# ---------------------------------------------------------------------------
# V1 final refinement: document-title-aware PDF templates
# - CERTIFICATE OF ANALYSIS keeps the standard COA layout.
# - PRODUCT SPECIFICATION SHEET uses the RA01-style product specification layout,
#   except the Probiotics preset keeps its own probiotic-specific layout.
# ---------------------------------------------------------------------------


def _spec_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    """RA01-style product-spec table: Parameter | Specification/Limit | Test Methods.

    If the source section has a Results column, it is intentionally removed for
    product specification output. This lets the same editable COA data produce
    a correct specification sheet when the document title is changed.
    """
    original_cols = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    title = str(section.get("title", "Section") or "Section").upper()
    title_l = title.lower()

    # Second-column heading follows the original document.
    second_heading = "LIMIT (NMT)" if ("metal" in title_l or "micro" in title_l) else "SPECIFICATION"
    header = [title, second_heading, "TEST METHODS"]
    data_rows = [[_paragraph(c, bold) for c in header]]

    lower_cols = [c.strip().lower() for c in original_cols]
    def idx_for(names, default):
        for n in names:
            if n in lower_cols:
                return lower_cols.index(n)
        return default

    param_i = idx_for(["parameter", "test items", "test item"], 0)
    spec_i = idx_for(["specification", "specifications", "limit (nmt)", "limit", "limits"], 1 if len(original_cols) > 1 else 0)
    method_i = idx_for(["test methods", "test method", "method"], len(original_cols)-1 if original_cols else 2)

    for row in rows:
        padded = list(row) + [""] * 6
        data_rows.append([
            _paragraph(padded[param_i], normal),
            _paragraph(padded[spec_i], normal),
            _paragraph(padded[method_i], normal),
        ])

    widths = [total_w * 0.43, total_w * 0.42, total_w * 0.15]
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10.0),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.25),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.25),
    ]))
    return tbl


def _default_storage_guidelines_table(total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    data_rows = [
        [_paragraph("Sterilization", bold), _paragraph("Packaging", bold), _paragraph("Health & Safety", bold), _paragraph("Storage Conditions", bold)],
        [
            _paragraph("Steam Treatment", normal),
            _paragraph("Carton boxes with inner double-layer LDPE bags and outer stretch wrap for airtight packaging.", normal),
            _paragraph("Manufactured, packaged, stored, and shipped according to International food safety standards.", normal),
            _paragraph("Store in a cool, Dry place.<br/><br/>Keep away from sunlight and infestation.", normal),
        ],
    ]
    tbl = Table(data_rows, colWidths=[total_w * 0.22, total_w * 0.23, total_w * 0.23, total_w * 0.32], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#242424")),
        ("BACKGROUND", (0, 0), (-1, 0), grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica", 10.0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def _generate_standard_spec_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    if output_path is None:
        output_path = OUTPUT_DIR / f"PRODUCT_SPECIFICATION_{sku}.pdf"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=12 * mm, bottomMargin=24 * mm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("spec_normal", parent=styles["Normal"], fontName="Helvetica", fontSize=10.0, leading=12.0, textColor=dark)
    bold = ParagraphStyle("spec_bold", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("spec_heading", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17.0, leading=19, alignment=1, textColor=dark, spaceAfter=20)
    website = ParagraphStyle("spec_web", parent=normal, fontSize=12.0, leading=13, alignment=1, textColor=border, spaceAfter=8)
    brand = ParagraphStyle("spec_brand", parent=styles["Title"], fontName="Helvetica", fontSize=30, leading=31, alignment=1, textColor=border, spaceAfter=0)
    guide_heading = ParagraphStyle("guide_heading", parent=styles["Heading2"], fontName="Helvetica", fontSize=17.0, leading=20, alignment=0, textColor=dark, spaceBefore=6, spaceAfter=6)

    story: List[Any] = []
    logo = _logo_flowable(data, 70, 26)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 1.5 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    # Match the RA01 product specification reference title.
    story.append(_paragraph("PRODUCT SPECIFICATION", heading))

    # Product specification does not show manufacture date or batch number.
    hidden_fields = {"manufacture date", "manufacturing date", "batch #", "batch number"}
    fields = []
    for row in data.get("product_fields", []):
        if not any(str(x).strip() for x in row):
            continue
        label = str(row[0] if len(row) > 0 else "").strip()
        if label.lower() in hidden_fields:
            continue
        fields.append(row)

    field_rows = [[_paragraph("PRODUCTS", bold), _paragraph("INFORMATION", bold)]]
    for row in fields:
        field_rows.append([_paragraph(row[0] if len(row) > 0 else "", normal), _paragraph(row[1] if len(row) > 1 else "", normal)])
    field_tbl = Table(field_rows, colWidths=[62 * mm, 76 * mm], hAlign="LEFT")
    field_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
    ]))
    story.append(field_tbl)
    story.append(Spacer(1, 9 * mm))

    total_w = A4[0] - doc.leftMargin - doc.rightMargin
    for section in data.get("sections", []):
        title = str(section.get("title", "")).lower()
        if "packaging" in title or "storage" in title or "guideline" in title:
            continue
        rows = section.get("rows", [])
        if not rows or not any(any(str(cell).strip() for cell in r) for r in rows):
            continue
        story.append(_spec_section_table(section, total_w, normal, bold, grey))
        story.append(Spacer(1, 6.5 * mm))

    story.append(_paragraph("Sterilization, Packaging & Storage Guidelines", guide_heading))
    story.append(_default_storage_guidelines_table(total_w, normal, bold, grey))

    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)


# Override probiotic layout with larger text while keeping it as its own template.
def _compact_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey, dark) -> Table:
    columns = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    data_rows = [[_paragraph(section.get("title", "Section"), bold)] + ["" for _ in columns[1:]]]
    data_rows.append([_paragraph(c, bold) for c in columns])
    for r in rows:
        padded = list(r) + [""] * max(0, len(columns) - len(r))
        data_rows.append([_paragraph(cell, normal) for cell in padded[:len(columns)]])
    if len(columns) == 4:
        widths = [total_w * 0.22, total_w * 0.30, total_w * 0.23, total_w * 0.25]
    elif len(columns) == 3:
        widths = [total_w * 0.34, total_w * 0.36, total_w * 0.30]
    else:
        widths = [total_w / max(1, len(columns))] * len(columns)
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), grey),
        ("FONT", (0, 0), (-1, 1), "Helvetica-Bold", 8.4),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b0b0b0")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, dark),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, dark),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
    ]))
    return tbl


def _generate_probiotics_spec_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    if output_path is None:
        output_path = OUTPUT_DIR / f"PROBIOTICS_PRODUCT_SPECIFICATION_{sku}.pdf"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("pro_normal_big", parent=styles["Normal"], fontName="Helvetica", fontSize=8.3, leading=9.1, textColor=dark)
    bold = ParagraphStyle("pro_bold_big", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("pro_heading_big", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16.0, leading=18, alignment=1, textColor=dark, spaceAfter=6)
    website = ParagraphStyle("pro_web_big", parent=normal, fontSize=9.5, leading=10, alignment=1, textColor=border, spaceAfter=5)
    brand = ParagraphStyle("pro_brand_big", parent=styles["Title"], fontName="Helvetica", fontSize=28, leading=30, alignment=1, textColor=border)
    story: List[Any] = []
    logo = _logo_flowable(data, 58, 20)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 0.8 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    story.append(_paragraph("PRODUCT SPECIFICATION", heading))

    fields = [row for row in data.get("product_fields", []) if any(str(x).strip() for x in row)]
    frows = []
    for row in fields:
        frows.append([_paragraph(row[0] if len(row)>0 else "", bold), _paragraph(row[1] if len(row)>1 else "", normal)])
    if frows:
        ft = Table(frows, colWidths=[42 * mm, 72 * mm], hAlign="LEFT")
        ft.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [grey, colors.white]),
            ("LINEABOVE", (0, 0), (-1, 0), 0.7, dark),
            ("LINEBELOW", (0, -1), (-1, -1), 0.7, dark),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 1.4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
        ]))
        story.append(ft)
        story.append(Spacer(1, 4.5 * mm))
    total_w = A4[0] - doc.leftMargin - doc.rightMargin - 4 * mm
    sections = data.get("sections", [])
    for idx, section in enumerate(sections):
        rows = section.get("rows", [])
        if not rows or not any(any(str(cell).strip() for cell in r) for r in rows):
            continue
        story.append(_compact_section_table(section, total_w, normal, bold, grey, dark))
        story.append(Spacer(1, 2.4 * mm if idx < len(sections)-1 else 0.5 * mm))
    note = _paragraph("*Do not exceed 25C during handling or transit to preserve viability of live probiotic.", normal)
    story.append(note)
    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)


def generate_document_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    template = str(data.get("template_name", ""))
    title = str(data.get("document_title", ""))
    title_upper = title.upper()
    if "PROBIOTICS" in template.upper():
        return _generate_probiotics_spec_pdf(data, output_path)
    if "PRODUCT SPECIFICATION" in title_upper:
        return _generate_standard_spec_pdf(data, output_path)
    if template.startswith("Standard COA") or "CERTIFICATE OF ANALYSIS" in title_upper:
        return _generate_standard_coa_pdf(data, output_path)
    return _generate_generic_document_pdf(data, output_path)

# Final compact RA01-style standard product specification override to keep one page.
def _spec_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    original_cols = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    title = str(section.get("title", "Section") or "Section").upper()
    title_l = title.lower()
    second_heading = "LIMIT (NMT)" if ("metal" in title_l or "micro" in title_l) else "SPECIFICATION"
    data_rows = [[_paragraph(title, bold), _paragraph(second_heading, bold), _paragraph("TEST METHODS", bold)]]
    lower_cols = [c.strip().lower() for c in original_cols]
    def idx_for(names, default):
        for n in names:
            if n in lower_cols:
                return lower_cols.index(n)
        return default
    param_i = idx_for(["parameter", "test items", "test item"], 0)
    spec_i = idx_for(["specification", "specifications", "limit (nmt)", "limit", "limits"], 1 if len(original_cols) > 1 else 0)
    method_i = idx_for(["test methods", "test method", "method"], len(original_cols)-1 if original_cols else 2)
    for row in rows:
        padded = list(row) + [""] * 6
        data_rows.append([_paragraph(padded[param_i], normal), _paragraph(padded[spec_i], normal), _paragraph(padded[method_i], normal)])
    widths = [total_w * 0.43, total_w * 0.36, total_w * 0.21]
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.25),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.25),
    ]))
    return tbl


def _default_storage_guidelines_table(total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    data_rows = [
        [_paragraph("Sterilization", bold), _paragraph("Packaging", bold), _paragraph("Health & Safety", bold), _paragraph("Storage Conditions", bold)],
        [
            _paragraph("Steam Treatment", normal),
            _paragraph("Carton boxes with inner double-layer LDPE bags and outer stretch wrap for airtight packaging.", normal),
            _paragraph("Manufactured, packaged, stored, and shipped according to International food safety standards.", normal),
            _paragraph("Store in a cool, Dry place.<br/><br/>Keep away from sunlight and infestation.", normal),
        ],
    ]
    tbl = Table(data_rows, colWidths=[total_w * 0.22, total_w * 0.23, total_w * 0.23, total_w * 0.32], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#242424")),
        ("BACKGROUND", (0, 0), (-1, 0), grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica", 9.2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


def _generate_standard_spec_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    if output_path is None:
        output_path = OUTPUT_DIR / f"PRODUCT_SPECIFICATION_{sku}.pdf"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=10 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("spec_normal_final", parent=styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=10.8, textColor=dark)
    bold = ParagraphStyle("spec_bold_final", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("spec_heading_final", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16.7, leading=18.5, alignment=1, textColor=dark, spaceAfter=15)
    website = ParagraphStyle("spec_web_final", parent=normal, fontSize=11.0, leading=12, alignment=1, textColor=border, spaceAfter=6)
    brand = ParagraphStyle("spec_brand_final", parent=styles["Title"], fontName="Helvetica", fontSize=30, leading=31, alignment=1, textColor=border, spaceAfter=0)
    guide_heading = ParagraphStyle("guide_heading_final", parent=styles["Heading2"], fontName="Helvetica", fontSize=15.5, leading=17, alignment=0, textColor=dark, spaceBefore=2, spaceAfter=3)
    story: List[Any] = []
    logo = _logo_flowable(data, 68, 24)
    if logo:
        story.append(logo); story.append(Spacer(1, 1.0 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    story.append(_paragraph("PRODUCT SPECIFICATION", heading))
    hidden_fields = {"manufacture date", "manufacturing date", "batch #", "batch number"}
    fields = []
    for row in data.get("product_fields", []):
        if not any(str(x).strip() for x in row): continue
        label = str(row[0] if len(row) > 0 else "").strip()
        if label.lower() in hidden_fields: continue
        fields.append(row)
    field_rows = [[_paragraph("PRODUCTS", bold), _paragraph("INFORMATION", bold)]]
    for row in fields:
        field_rows.append([_paragraph(row[0] if len(row) > 0 else "", normal), _paragraph(row[1] if len(row) > 1 else "", normal)])
    field_tbl = Table(field_rows, colWidths=[62 * mm, 76 * mm], hAlign="LEFT")
    field_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.65),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.65),
    ]))
    story.append(field_tbl); story.append(Spacer(1, 6 * mm))
    total_w = A4[0] - doc.leftMargin - doc.rightMargin
    for section in data.get("sections", []):
        title = str(section.get("title", "")).lower()
        if "packaging" in title or "storage" in title or "guideline" in title: continue
        rows = section.get("rows", [])
        if not rows or not any(any(str(cell).strip() for cell in r) for r in rows): continue
        story.append(_spec_section_table(section, total_w, normal, bold, grey))
        story.append(Spacer(1, 3.5 * mm))
    story.append(_paragraph("Sterilization, Packaging & Storage Guidelines", guide_heading))
    story.append(_default_storage_guidelines_table(total_w, normal, bold, grey))
    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)

# ---------------------------------------------------------------------------
# V1 readable product-spec refinement
# Standard PRODUCT SPECIFICATION SHEET now uses the available page space more
# like the COA layout: larger row spacing, more readable storage guideline
# table, and no unnecessary compression. Probiotics keeps its own layout.
# ---------------------------------------------------------------------------

def _spec_section_table(section: Dict[str, Any], total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    original_cols = [str(c or "") for c in section.get("columns", [])]
    rows = [r for r in section.get("rows", []) if any(str(cell).strip() for cell in r)]
    title = str(section.get("title", "Section") or "Section").upper()
    title_l = title.lower()
    second_heading = "LIMIT (NMT)" if ("metal" in title_l or "micro" in title_l) else "SPECIFICATION"
    data_rows = [[_paragraph(title, bold), _paragraph(second_heading, bold), _paragraph("TEST METHODS", bold)]]

    lower_cols = [c.strip().lower() for c in original_cols]
    def idx_for(names, default):
        for n in names:
            if n in lower_cols:
                return lower_cols.index(n)
        return default

    param_i = idx_for(["parameter", "test items", "test item"], 0)
    spec_i = idx_for(["specification", "specifications", "limit (nmt)", "limit", "limits"], 1 if len(original_cols) > 1 else 0)
    method_i = idx_for(["test methods", "test method", "method"], len(original_cols) - 1 if original_cols else 2)

    for row in rows:
        padded = list(row) + [""] * 6
        data_rows.append([
            _paragraph(padded[param_i], normal),
            _paragraph(padded[spec_i], normal),
            _paragraph(padded[method_i], normal),
        ])

    widths = [total_w * 0.43, total_w * 0.37, total_w * 0.20]
    tbl = Table(data_rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10.0),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2),
        ("TOPPADDING", (0, 0), (-1, -1), 2.35),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.35),
    ]))
    return tbl


def _default_storage_guidelines_table(total_w: float, normal: ParagraphStyle, bold: ParagraphStyle, grey) -> Table:
    storage_normal = ParagraphStyle(
        "storage_normal_readable",
        parent=normal,
        fontName="Helvetica",
        fontSize=9.8,
        leading=11.7,
        textColor=colors.HexColor("#242424"),
    )
    storage_bold = ParagraphStyle("storage_bold_readable", parent=storage_normal, fontName="Helvetica-Bold")
    data_rows = [
        [
            _paragraph("Sterilization", storage_bold),
            _paragraph("Packaging", storage_bold),
            _paragraph("Health & Safety", storage_bold),
            _paragraph("Storage Conditions", storage_bold),
        ],
        [
            _paragraph("Steam Treatment", storage_normal),
            _paragraph("Carton boxes with inner double-layer LDPE bags and outer stretch wrap for airtight packaging.", storage_normal),
            _paragraph("Manufactured, packaged, stored, and shipped according to International food safety standards.", storage_normal),
            _paragraph("Store in a cool, Dry place.<br/><br/>Keep away from sunlight and infestation.", storage_normal),
        ],
    ]
    tbl = Table(data_rows, colWidths=[total_w * 0.22, total_w * 0.25, total_w * 0.25, total_w * 0.28], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#242424")),
        ("BACKGROUND", (0, 0), (-1, 0), grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5.5),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
    ]))
    return tbl


def _generate_standard_spec_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    sku = _field_value(data, "Product SKU#", "Product SKU", "SKU") or "PRODUCT"
    if output_path is None:
        output_path = OUTPUT_DIR / f"PRODUCT_SPECIFICATION_{sku}.pdf"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    border = colors.HexColor("#6dbb43")
    dark = colors.HexColor("#242424")
    grey = colors.HexColor("#eeeeee")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=24 * mm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("spec_normal_readable_final", parent=styles["Normal"], fontName="Helvetica", fontSize=10.0, leading=12.0, textColor=dark)
    bold = ParagraphStyle("spec_bold_readable_final", parent=normal, fontName="Helvetica-Bold")
    heading = ParagraphStyle("spec_heading_readable_final", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17.0, leading=19, alignment=1, textColor=dark, spaceAfter=17)
    website = ParagraphStyle("spec_web_readable_final", parent=normal, fontSize=12.0, leading=13, alignment=1, textColor=border, spaceAfter=7)
    brand = ParagraphStyle("spec_brand_readable_final", parent=styles["Title"], fontName="Helvetica", fontSize=30, leading=31, alignment=1, textColor=border, spaceAfter=0)
    guide_heading = ParagraphStyle("guide_heading_readable_final", parent=styles["Heading2"], fontName="Helvetica", fontSize=16.0, leading=18, alignment=0, textColor=dark, spaceBefore=2, spaceAfter=5)

    story: List[Any] = []
    logo = _logo_flowable(data, 68, 24)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 1.2 * mm))
    else:
        story.append(_paragraph(data.get("brand_name", "medikonda"), brand))
    if data.get("website"):
        story.append(_paragraph(data.get("website"), website))
    story.append(_paragraph("PRODUCT SPECIFICATION", heading))

    hidden_fields = {"manufacture date", "manufacturing date", "batch #", "batch number"}
    fields = []
    for row in data.get("product_fields", []):
        if not any(str(x).strip() for x in row):
            continue
        label = str(row[0] if len(row) > 0 else "").strip()
        if label.lower() in hidden_fields:
            continue
        fields.append(row)

    field_rows = [[_paragraph("PRODUCTS", bold), _paragraph("INFORMATION", bold)]]
    for row in fields:
        field_rows.append([
            _paragraph(row[0] if len(row) > 0 else "", normal),
            _paragraph(row[1] if len(row) > 1 else "", normal),
        ])
    field_tbl = Table(field_rows, colWidths=[62 * mm, 76 * mm], hAlign="LEFT")
    field_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [grey, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.2),
        ("TOPPADDING", (0, 0), (-1, -1), 2.35),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.35),
    ]))
    story.append(field_tbl)
    story.append(Spacer(1, 8 * mm))

    total_w = A4[0] - doc.leftMargin - doc.rightMargin
    visible_sections = []
    for section in data.get("sections", []):
        title = str(section.get("title", "")).lower()
        if "packaging" in title or "storage" in title or "guideline" in title:
            continue
        rows = section.get("rows", [])
        if rows and any(any(str(cell).strip() for cell in r) for r in rows):
            visible_sections.append(section)

    for idx, section in enumerate(visible_sections):
        story.append(_spec_section_table(section, total_w, normal, bold, grey))
        story.append(Spacer(1, 5.4 * mm if idx < len(visible_sections) - 1 else 6.2 * mm))

    story.append(_paragraph("Sterilization, Packaging & Storage Guidelines", guide_heading))
    story.append(_default_storage_guidelines_table(total_w, normal, bold, grey))

    doc.build(story, onFirstPage=lambda c, d: _draw_page_frame(c, d, data), onLaterPages=lambda c, d: _draw_page_frame(c, d, data))
    return Path(output_path)


def generate_document_pdf(data: Dict[str, Any], output_path: str | Path | None = None) -> Path:
    template = str(data.get("template_name", ""))
    title = str(data.get("document_title", ""))
    title_upper = title.upper()
    if "PROBIOTICS" in template.upper():
        return _generate_probiotics_spec_pdf(data, output_path)
    if "PRODUCT SPECIFICATION" in title_upper:
        return _generate_standard_spec_pdf(data, output_path)
    if template.startswith("Standard COA") or "CERTIFICATE OF ANALYSIS" in title_upper:
        return _generate_standard_coa_pdf(data, output_path)
    return _generate_generic_document_pdf(data, output_path)
