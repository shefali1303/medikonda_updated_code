# Update Notes - Product Specification Spacing Refinement

This package is based on the provided live application ZIP and preserves the existing runtime data folder and database.

Updated files:
- app/pdf_generator.py
- app/defaults.py
- app/web_main.py
- static/app.js
- static/styles.css
- templates/index.html
- README.md

Main changes:
- COA layout remains in the approved format.
- Product Specification Sheet uses RA01-style standard product specification layout for normal products.
- Probiotics Product Specification keeps the probiotics-specific layout.
- Product Specification spacing and typography are improved for readability.
- Fixed Medikonda logo and boundary color remain enforced.
- Document Title remains a dropdown with CERTIFICATE OF ANALYSIS and PRODUCT SPECIFICATION SHEET.

Preserved:
- data/document_records.sqlite3
- data/output
- data/logos
- .git metadata from uploaded live ZIP
