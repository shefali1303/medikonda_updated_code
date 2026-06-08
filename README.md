# Medikonda PDF Generator Web App

This is the browser-based version of the Medikonda PDF Generator.

## Run on Mac

Double-click `start_mac.command`, then open:

```text
http://localhost:8000
```

Other systems on the same office Wi-Fi/LAN can open:

```text
http://YOUR-SERVER-IP:8000
```

## Run on Windows

Double-click `start_windows.bat`, then open:

```text
http://localhost:8000
```

## Find server IP

Mac:

```bash
ipconfig getifaddr en0
```

Windows:

```bat
ipconfig
```

Look for IPv4 Address.

## Notes

- Generated PDFs are saved in `data/output`.
- Saved records are stored in `data/document_records.sqlite3`.
- Uploaded logos are saved in `data/logos`.
- Keep the server computer turned on while staff are using the app.
- This first web version is designed for local/internal office use. Add login before exposing it to the public internet.


## V1 Final Output Update

- PDF logo and boundary color are fixed to Medikonda branding.
- Document Title is now selected from a dropdown: CERTIFICATE OF ANALYSIS or PRODUCT SPECIFICATION SHEET.
- COA PDF typography, spacing, and section alignment were adjusted closer to the provided Original File reference.
