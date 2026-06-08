# Sample update: Oils and Chemical templates + 6-dot movement handles

## Files changed

- `app/defaults.py`
  - Added `Standard COA - Oils` template preset.
  - Added `Standard COA - Chemical` template preset.
  - Added CAS Number field for Oils and Chemical presets.
  - Oils template starts with a `Physical Appearance` section.
  - Chemical template starts with a `Physical Analysis` section.

- `templates/index.html`
  - Added a Move header column to the Product / Document Fields table.

- `static/app.js`
  - Added 6-dot handles for Product / Document Fields rows.
  - Added move up/down for Product / Document Fields rows.
  - Added 6-dot handles for Section table rows.
  - Added move up/down for Section rows.
  - Added 6-dot handles for Section table columns.
  - Added move left/right for Section columns.
  - Preserved normal text field typing behavior by using handle-only selection actions.

- `static/styles.css`
  - Added styling for 6-dot handles, selected rows, selected columns, and mini movement buttons.

## Files not changed

- `app/pdf_generator.py`
- `app/database.py`
- `app/paths.py`
- `data/document_records.sqlite3`
- `data/output`

## Testing checklist

- Select `Standard COA - Oils` from Template Preset.
- Select `Standard COA - Chemical` from Template Preset.
- Check Product / Document Fields rows can move with the 6-dot handle.
- Check Section rows can move with the 6-dot handle.
- Check Section columns can move left/right with the column 6-dot handle.
- Generate COA PDF for Oils.
- Generate COA PDF for Chemical.
- Verify old COA, Product Specification, and Probiotics presets still work.
