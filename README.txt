# Research resultas
- This project renders an interactive map of adoption cases in Morelia.
- It records cases with coordinates, adopter status (SI-YES/NO-NOT/NA), and additional data.
- The map provides:
  - Marker clustering by proximity.
  - Heatmap for cases marked "NO" (Bad adopter).
  - Form to add cases with coordinate validation and direct selection on the map.
  - Download of the dataset as Excel.
- Data is stored in a local Excel file: Adoptantes_Extract.xlsx.

For more information about the research, see the PDF files included:
- 2024-3-PI-002-AC-InformeInv (Original version in Spanish)
- 2024-3-PI-002-AC-ResearchReport-Transcript (English transcript)

# Overview
Flask application that generates an interactive map (Folium/Leaflet) with:
- Marker clustering (MarkerCluster).
- Heatmap for problematic zones.
- Form to add new cases with coordinate validation.
- Button to download the updated dataset.

# Requirements
- Python 3.9+ (recommended 3.10 or 3.11).
- Updated pip.
- Libraries (see requirements.txt):
  - flask
  - pandas
  - folium
  - openpyxl

# Installation
1) Create and activate a virtual environment (optional, recommended):
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1
2) Install dependencies:
   - pip install -r requirements.txt

# Project structure
- app.py: Flask server entry point.
- routes.py: HTTP routes to render the map, save cases, and download data.
- mapa_core.py: Logic to load data, build the map, and save the HTML.
- templates/mapa_interactivo.html: Generated automatically at startup.
- Adoptantes_Extract.xlsx: Excel database (auto-created if missing).
- requirements.txt: Project dependencies.

# How to run
1) From the project folder:
   - python app.py
2) Open in your browser:
   - http://127.0.0.1:5000/
   - The file templates/mapa_interactivo.html is generated on start.
3) Stop the server with Ctrl + C in the terminal.

# Using the map
- “➕ Add Case” button:
  - Fill required fields (Name and Location).
  - Pick coordinates by:
    - Clicking on the map, or
    - Typing Latitude and Longitude and pressing “Validate”.
  - Save. The page reloads and shows the new marker.
- “📥 Download Data” button:
  - Downloads the up-to-date Excel with all records.
- Layers:
  - “Clustering”: markers grouped by area.
  - “Heatmap”: intensity for “NO” (Bad adopter) cases.

# Available endpoints
- GET / : Generates and shows the interactive map.
- POST /guardar_caso : Saves a record with coordinate validation.
  - Expected JSON:
    {
      "Fecha": "YYYY-MM-DD",
      "Nombre Mascota": "string",
      "Domicilio": "string",
      "Edad adoptante": number | string,
      "Buen adoptante": "SI" | "NO" | "NA",
      "Latitud": number,
      "Longitud": number
    }
- GET /descargar_datos : Returns the current Excel file.

# Data file (Excel)
- Path: Adoptantes_Extract.xlsx (project root).
- Columns: Fecha, Nombre Mascota, Domicilio, Edad adoptante, Buen adoptante, Latitud, Longitud.
- If missing, it is created automatically with headers.

# Validation and considerations
- Valid coordinates:
  - Latitude: -90 to 90
  - Longitude: -180 to 180
- “Buen adoptante” is normalized to SI/NO/NA (default NA if empty).
- Only rows with valid coordinates are plotted.

# Troubleshooting
- Map does not open:
  - Ensure the server runs without errors.
  - Check that templates/mapa_interactivo.html was generated.
- openpyxl/pandas error:
  - Reinstall deps: pip install --upgrade --force-reinstall -r requirements.txt
- Excel file locked:
  - Close the Excel file before saving a new case.
- Change port:
  - Edit app.py: app.run(port=5000, debug=False) -> set desired port.
- Enable debug (dev only):
  - app.run(port=5000, debug=True)

# Notes
- The templates directory is created automatically if missing.
- The map shows a fixed title with generation date and time.
- Marker colors by status:
  - Green (SI/YES), Red (NO/NOT), Orange (NA).
