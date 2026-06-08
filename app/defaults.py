from __future__ import annotations

from pathlib import Path

from .paths import resource_path

# Template presets are examples only. Every field, section, row, and column can be edited in the app.

APP_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LOGO_PATH = str(resource_path("assets", "medikonda_logo.png"))
FIELD_PRESETS = {
    "Botanical + Plant Part": [
        ["Common Name", "Graviola (Soursop) Leaf Powder"],
        ["Botanical Name", "Annona muricata"],
        ["Plant Part Used", "Leaves"],
        ["Shelf Life", "36 Months"],
        ["Country of Origin", "India"],
        ["Manufacture Date", "JULY2025"],
        ["Batch #", "RA380725"],
        ["Product SKU#", "RA38"],
    ],
    "No Plant Part": [
        ["Common Name", "Graviola (Soursop) Leaf Powder"],
        ["Botanical Name", "Annona muricata"],
        ["Shelf Life", "36 Months"],
        ["Country of Origin", "India"],
        ["Manufacture Date", "JULY2025"],
        ["Batch #", "RA380725"],
        ["Product SKU#", "RA38"],
    ],
    "No Botanical Name": [
        ["Common Name", "Copper Chlorophyllin Liquid"],
        ["Plant Part Used", "Leaves"],
        ["Shelf Life", "36 Months"],
        ["Country of Origin", "India"],
        ["Manufacture Date", "SEP20XX"],
        ["Batch #", "RA89809XX"],
        ["Product SKU#", "RA898"],
    ],
    "No Botanical + No Plant Part": [
        ["Common Name", "Black Salt"],
        ["Shelf Life", "36 Months"],
        ["Country of Origin", "India"],
        ["Manufacture Date", "SEP20XX"],
        ["Batch #", "RA211209XX"],
        ["Product SKU#", "RA2112"],
    ],
    "Extract": [
        ["Product Name", "Aloe Vera Extract Powder 20:1"],
        ["Botanical Name", "Aloe barbadensis"],
        ["Shelf Life", "36 months"],
        ["Country of Origin", "India"],
        ["Manufacturing Date", "June 2024"],
        ["Batch #", "RA2490624"],
        ["Product SKU", "RA249"],
    ],
    "Probiotics Specification": [
        ["Product Name", "Probiotics powder"],
        ["Probiotics Type", "Lactobacillus Curvatus"],
        ["Product Form", "Freeze dried powder"],
        ["Product SKU#", "RA1148"],
        ["Package Size", "1/5kg"],
        ["Outer Packing", "Foam Box & Carton"],
    ],
}

BASIC_SECTIONS = [
    {
        "title": "Physical Analysis",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Form", "Powder", "Complies", "Organoleptic"],
            ["Color", "Green", "Complies", "Organoleptic"],
            ["Odor", "Characteristic", "Complies", "Organoleptic"],
            ["Taste", "Characteristic", "Complies", "Organoleptic"],
            ["Mesh Size", "80# mesh", "Complies", "USP <786>"],
            ["Loss on Drying", "NMT 10%", "Complies", "USP <731>"],
        ],
    },
    {
        "title": "Metals",
        "columns": ["Parameter", "Limit (NMT)", "Results", "Test Methods"],
        "rows": [
            ["Total Heavy Metals", "10 ppm", "Complies", "USP <231>"],
            ["Lead", "0.5 ppm", "Complies", "USP <232>"],
            ["Arsenic", "1 ppm", "Complies", "USP <232>"],
            ["Mercury", "0.5 ppm", "Complies", "USP <232>"],
            ["Cadmium", "0.5 ppm", "Complies", "USP <232>"],
        ],
    },
    {
        "title": "Microbiology",
        "columns": ["Parameter", "Limit (NMT)", "Results", "Test Methods"],
        "rows": [
            ["Total Plate Count", "50,000 cfu/g", "Complies", "USP <61>"],
            ["Yeast & Mold", "400 cfu/g", "Complies", "USP <61>"],
            ["E. Coli", "Absent", "Complies", "USP <62>"],
            ["Salmonella", "Absent", "Complies", "USP <62>"],
            ["Staphylococcus aureus", "Absent", "Complies", "USP <62>"],
            ["Coliforms", "NMT 10 cfu/g", "Complies", "USP <62>"],
        ],
    },
]

EXTRACT_SECTIONS = [
    {
        "title": "Physical Analysis",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Form", "Fine Powder", "Complies", "Organoleptic"],
            ["Color", "Light Brown Color", "Complies", "Organoleptic"],
            ["Odor", "Characteristic", "Complies", "Organoleptic"],
            ["Taste", "Characteristic", "Complies", "Organoleptic"],
            ["Mesh Size", "80 mesh", "Complies", "USP <786>"],
            ["Ash", "NMT 5%", "2.38%", "In House"],
            ["Moisture", "NMT 5%", "4.33%", "In House"],
            ["Acid-insoluble ash", "NMT 5%", "1.84%", "USP <786>"],
            ["Bulk Density", "40-80 g/100mL", "Complies", "USP <786>"],
            ["Aloe Polysaccharides Content", "NLT 20.00%", "25.18%", "Gravimetric"],
        ],
    },
    {
        "title": "Total Heavy Metals",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Lead", "NMT 0.5 ppm", "Complies", "USP <232>"],
            ["Arsenic", "NMT 1 ppm", "Complies", "USP <232>"],
            ["Mercury", "NMT 0.5 ppm", "Complies", "USP <232>"],
            ["Cadmium", "NMT 0.5 ppm", "Complies", "USP <232>"],
        ],
    },
    {
        "title": "Microbiology Test",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Total Plate Count", "NMT 10,000 cfu/g", "Complies", "USP <61>"],
            ["Yeast & Mold", "NMT 100 cfu/g", "Complies", "USP <61>"],
            ["E. Coli", "Absent", "Complies", "USP <62>"],
            ["Salmonella", "Absent", "Complies", "USP <62>"],
            ["Staphylococcus aureus", "Absent", "Complies", "USP <62>"],
            ["Coliforms", "NMT 10 cfu/g", "Complies", "USP <62>"],
        ],
    },
]

PROBIOTICS_SECTIONS = [
    {
        "title": "Physical & Chemical Properties",
        "columns": ["Test Items", "Specifications", "Test Methods"],
        "rows": [
            ["Appearance", "White to Light Yellow", "Organoleptic"],
            ["Odor", "Slight Fermentation", "Organoleptic"],
            ["Mesh Size", "#60 Mesh", "USP <786>"],
            ["Moisture %", "<=8.0", "USP <731>"],
            ["Water activity", "<=0.15", "USP <922>"],
        ],
    },
    {
        "title": "Heavy Metals",
        "columns": ["Test Items", "Specifications", "Test Methods"],
        "rows": [
            ["Lead (Pb) ppm", "<=0.5", "USP <232>"],
            ["Arsenic (As) ppm", "<=0.5", "USP <232>"],
            ["Cadmium (Cd) ppm", "<=0.5", "USP <232>"],
            ["Mercury (Hg) ppm", "<=0.5", "USP <232>"],
        ],
    },
    {
        "title": "Microbiology",
        "columns": ["Test Items", "Specifications", "Test Methods"],
        "rows": [
            ["Viable-cell (CFU/g)", "1.0 x 10^11", "USP <61>"],
            ["Non LAB Count (CFU/g)", "<=1,000", "USP <61>"],
            ["Yeast & Mold (CFU/g)", "<=100", "USP <61>"],
            ["Coliform (CFU/g)", "<=10", "USP <62>"],
            ["Escherichia coli (CFU/g)", "Absent", "USP <62>"],
            ["Salmonella", "Absent", "USP <62>"],
            ["Staphylococcus aureus", "Absent", "USP <62>"],
            ["Shigella", "Absent", "USP <62>"],
        ],
    },
    {
        "title": "Packaging & Storage Guidelines",
        "columns": ["Shelf Life", "Packing", "Health & Safety", "Storage Conditions"],
        "rows": [[
            "24 Month from the date of Manufacture",
            "Packed in Carton Box with LDPE pharma-grade pouches placed inside thermal insulated boxes with ice gel packs",
            "Manufactured, packed, stored, and shipped according to International food safety standards.",
            "2C - 8C for short term storage in sealed packaging. Store at -18C for long term storage in sealed packaging.",
        ]],
    },
]

TEMPLATE_PRESETS = {
    "Standard COA - Botanical + Plant Part": {
        "document_title": "CERTIFICATE OF ANALYSIS",
        "document_type": "Certificate of Analysis",
        "field_preset": "Botanical + Plant Part",
        "product_fields": FIELD_PRESETS["Botanical + Plant Part"],
        "sections": BASIC_SECTIONS,
    },
    "Standard COA - No Plant Part": {
        "document_title": "CERTIFICATE OF ANALYSIS",
        "document_type": "Certificate of Analysis",
        "field_preset": "No Plant Part",
        "product_fields": FIELD_PRESETS["No Plant Part"],
        "sections": BASIC_SECTIONS,
    },
    "Standard COA - No Botanical Name": {
        "document_title": "CERTIFICATE OF ANALYSIS",
        "document_type": "Certificate of Analysis",
        "field_preset": "No Botanical Name",
        "product_fields": FIELD_PRESETS["No Botanical Name"],
        "sections": BASIC_SECTIONS,
    },
    "Standard COA - No Botanical + No Plant Part": {
        "document_title": "CERTIFICATE OF ANALYSIS",
        "document_type": "Certificate of Analysis",
        "field_preset": "No Botanical + No Plant Part",
        "product_fields": FIELD_PRESETS["No Botanical + No Plant Part"],
        "sections": BASIC_SECTIONS,
    },
    "Extract COA": {
        "document_title": "CERTIFICATE OF ANALYSIS",
        "document_type": "Certificate of Analysis",
        "field_preset": "Extract",
        "product_fields": FIELD_PRESETS["Extract"],
        "sections": EXTRACT_SECTIONS,
    },
    "Probiotics Product Specification": {
        "document_title": "PRODUCT SPECIFICATION SHEET",
        "document_type": "Product Specification",
        "field_preset": "Probiotics Specification",
        "product_fields": FIELD_PRESETS["Probiotics Specification"],
        "sections": PROBIOTICS_SECTIONS,
    },
    "Blank Universal Template": {
        "document_title": "DOCUMENT",
        "document_type": "Custom Document",
        "field_preset": "Custom",
        "product_fields": [["Field Name", "Field Value"]],
        "sections": [
            {
                "title": "Section Name",
                "columns": ["Column 1", "Column 2", "Column 3", "Column 4"],
                "rows": [["", "", "", ""]],
            }
        ],
    },
}

DEFAULT_DATA = {
    "id": None,
    "template_name": "Standard COA - No Plant Part",
    "document_type": "Certificate of Analysis",
    "document_title": "CERTIFICATE OF ANALYSIS",
    "brand_name": "medikonda",
    "website": "www.medikonda.com",
    "logo_path": DEFAULT_LOGO_PATH,
    "border_color": "#6dbb43",
    "logo_width_mm": "66",
    "logo_height_mm": "24",
    "product_fields": FIELD_PRESETS["No Plant Part"],
    "sections": BASIC_SECTIONS,
    "footer_left_1": "Electronic document valid without signature.",
    "footer_left_2": "Copyright © All rights reserved.",
    "footer_right_1": "Department of Quality Control",
    "footer_right_2": "www.medikonda.com",
}


# ---------------------------------------------------------------------------
# Sample template update: Oils and Chemical COA presets
# These templates use the existing standard COA PDF layout. They only add
# default fields and initial rows from the supplied Oils/Chemical references.
# Users can still add, remove, edit, and reorder fields/sections/rows/columns.
# ---------------------------------------------------------------------------

STANDARD_REQUIRED_FIELDS = [
    ["Common Name", ""],
    ["Botanical Name", ""],
    ["Shelf Life", "36 Months"],
    ["Country of Origin", "India"],
    ["Manufacture Date", ""],
    ["Batch #", ""],
    ["Product SKU#", ""],
]

# Oils: based on the supplied Castor Oil reference.
# CAS Number is included as a blank editable field because oils/chemical products
# may require it, even if the specific Castor Oil reference does not show it.
OIL_FIELDS = [
    ["Product Name", "Castor Oil"],
    ["Botanical Name", "Ricinus Communis"],
    ["CAS Number", ""],
    ["Shelf Life", "36 months"],
    ["Country of Origin", "India"],
    ["Manufacture Date", ""],
    ["Batch #", ""],
    ["Product SKU#", "RA324"],
]

# Chemical: based on the supplied Decyl Glucoside COA reference.
CHEMICAL_FIELDS = [
    ["Product Name", "Decyl Glucoside"],
    ["CAS Number", "54549-25-6"],
    ["Shelf Life", "36 months"],
    ["Country of Origin", "India"],
    ["Manufacture Date", ""],
    ["Batch #", ""],
    ["Product SKU#", "RA919"],
]

OIL_SECTIONS = [
    {
        "title": "Physical Analysis",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Form", "Fine Powder", "Complies", "Organoleptic"],
            ["Color", "Pale Yellow Color", "Complies", "Organoleptic"],
            ["Odor", "Characteristic", "Complies", "Organoleptic"],
            ["Taste", "Characteristic", "Complies", "Organoleptic"],
            ["Moisture & Volatile", "0.25% Max", "0.09", "USP <786>"],
            ["Specific Gravity", "0.940-0.970", "0.958", "USP <731>"],
            ["Viscosity", "6.3-9 stokes", "6.8", "USP <731>"],
            ["Refractive Index", "1.470-1.485", "1.472", "USP <731>"],
            ["Acid Value", "2.0 Max (mgKOH/g)", "0.80", "USP <731>"],
            ["Saponification Value", "177-187 (mgKOH/g)", "177.6", "USP <731>"],
            ["Iodine Value", "82-90 (gI2/100g)", "83.4", "USP <731>"],
            ["Unsaponifiable Matter", "<0.8%", "0.6", "USP <731>"],
            ["Peroxide Value", "<5.0 (meqO2/kg)", "2.9", "USP <731>"],
            ["Hydroxyl Value", "160-170 (mgKOH/g)", "164.5", "USP <731>"],
            ["Solubility", "Soluble in alcohols & fixed oils", "Complies", "USP <731>"],
        ],
    }
]

CHEMICAL_SECTIONS = [
    {
        "title": "Physical Analysis",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Form", "Liquid", "Complies", "Organoleptic"],
            ["Color", "Clear to pale yellow", "Complies", "Organoleptic"],
            ["Odor", "Characteristic", "Complies", "Organoleptic"],
            ["Taste", "Characteristic", "Complies", "Organoleptic"],
            ["pH (10% solution, 20C)", "11.5-12.5", "12.0", "USP <791>"],
            ["Dry Matter / Solids Content", "50-55%", "52.4%", "USP <731>"],
            ["Density (20C)", "1.05-1.15 g/ml", "1.09 g/ml", "USP <841>"],
            ["Active Matter (Decyl Glucoside)", "NLT 50%", "51.2%", "Titration (USP)"],
        ],
    },
    {
        "title": "Total Heavy Metals",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Lead", "NMT 0.5 ppm", "Complies", "USP <232>"],
            ["Arsenic", "NMT 1 ppm", "Complies", "USP <232>"],
            ["Mercury", "NMT 0.5 ppm", "Complies", "USP <232>"],
            ["Cadmium", "NMT 0.5 ppm", "Complies", "USP <232>"],
        ],
    },
    {
        "title": "Microbiology Test",
        "columns": ["Parameter", "Specification", "Results", "Test Methods"],
        "rows": [
            ["Total Plate Count", "NMT 10,000 cfu/g", "Complies", "USP <61>"],
            ["Yeast & Mold", "NMT 1000 cfu/g", "Complies", "USP <61>"],
            ["E. Coli", "Absent", "Complies", "USP <62>"],
            ["Salmonella", "Absent", "Complies", "USP <62>"],
            ["Staphylococcus aureus", "Absent", "Complies", "USP <62>"],
            ["Coliforms", "NMT 100 cfu/g", "Complies", "USP <62>"],
        ],
    },
]

FIELD_PRESETS["Oils"] = OIL_FIELDS
FIELD_PRESETS["Chemical"] = CHEMICAL_FIELDS

TEMPLATE_PRESETS["Standard COA - Oils"] = {
    "document_title": "CERTIFICATE OF ANALYSIS",
    "document_type": "Certificate of Analysis",
    "field_preset": "Oils",
    "product_fields": OIL_FIELDS,
    "sections": OIL_SECTIONS,
}

TEMPLATE_PRESETS["Standard COA - Chemical"] = {
    "document_title": "CERTIFICATE OF ANALYSIS",
    "document_type": "Certificate of Analysis",
    "field_preset": "Chemical",
    "product_fields": CHEMICAL_FIELDS,
    "sections": CHEMICAL_SECTIONS,
}
