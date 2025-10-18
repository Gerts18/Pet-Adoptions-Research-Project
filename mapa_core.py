import pandas as pd
import folium
from folium.plugins import HeatMap, MeasureControl, MarkerCluster
import os
from datetime import datetime


EXCEL_PATH = 'Adoptantes_Extract.xlsx'

class MapaAdopcionesCompleto:
    def __init__(self):
        self.mapa = None
        self.df = None
        self.archivo_datos = EXCEL_PATH
        self.archivo_mapa = 'templates/mapa_interactivo.html'
        self.color_dict = {
            'SI': {'color': 'green', 'icon': 'ok-sign'},
            'NO': {'color': 'red', 'icon': 'remove-sign'},
            'NA': {'color': 'orange', 'icon': 'question-sign'}
        }
        
    def cargar_datos(self):
        try:
            if not os.path.exists(self.archivo_datos):
                columnas = ['Fecha', 'Nombre Mascota', 'Domicilio', 
                          'Edad adoptante', 'Buen adoptante', 
                          'Latitud', 'Longitud']
                self.df = pd.DataFrame(columns=columnas)
                self.df.to_excel(self.archivo_datos, index=False)
                return True
                
            self.df = pd.read_excel(self.archivo_datos, engine='openpyxl')
            
            if 'Latitud' in self.df.columns:
                self.df['Latitud'] = pd.to_numeric(self.df['Latitud'], errors='coerce')
            if 'Longitud' in self.df.columns:
                self.df['Longitud'] = pd.to_numeric(self.df['Longitud'], errors='coerce')
                
            self.df = self.df.dropna(subset=['Latitud', 'Longitud'])
            
            valid_coords = (
                (self.df['Latitud'].between(-90, 90)) & \
                (self.df['Longitud'].between(-180, 180))
            )
            self.df = self.df[valid_coords].copy()
            
            required = ['Buen adoptante', 'Nombre Mascota']
            for col in required:
                if col not in self.df.columns:
                    self.df[col] = None if col != 'Buen adoptante' else 'NA'
                    
            self.df['Buen adoptante'] = self.df['Buen adoptante'].fillna('NA').str.upper().str.strip()
            return True
            
        except Exception as e:
            print(f"\n✗ Error al cargar datos: {str(e)}")
            return False
    
    def actualizar_excel(self):
        """Actualiza el archivo Excel con los datos actuales"""
        try:
            self.df.to_excel(self.archivo_datos, index=False)
            return True
        except Exception as e:
            print(f"Error al actualizar Excel: {str(e)}")
            return False

    def crear_mapa_base(self):
        self.mapa = folium.Map(
            location=[19.7018, -101.1854],
            zoom_start=12,
            tiles='cartodbpositron',
            control_scale=True,
            width='100%',
            height='100%'
        )
        
        MeasureControl(position='topleft').add_to(self.mapa)
        folium.TileLayer('openstreetmap').add_to(self.mapa)
        self.cluster = MarkerCluster(name="Agrupamiento").add_to(self.mapa)
        self.heat_layer = folium.FeatureGroup(name="Mapa de calor").add_to(self.mapa)

    def agregar_marcadores(self):
        for idx, row in self.df.iterrows():
            if pd.isna(row['Latitud']) or pd.isna(row['Longitud']):
                continue
                
            status = row['Buen adoptante']
            color_info = self.color_dict.get(status, {'color': 'gray', 'icon': 'info-sign'})
            
            try:
                coords_text = f"{float(row['Latitud']):.6f}, {float(row['Longitud']):.6f}"
            except (ValueError, TypeError):
                coords_text = f"{row['Latitud']}, {row['Longitud']}"
            
            popup_content = f"""
            <div style='width:250px;'>
                <h4 style='color:{color_info['color']};'>{row.get('Nombre Mascota', 'N/A')}</h4>
                <p><b>Estado:</b> <span style='color:{color_info['color']};'>{status}</span></p>
                <p><b>Ubicación:</b> {row.get('Domicilio', 'N/A')}</p>
                <p><b>Fecha:</b> {row.get('Fecha', 'N/A')}</p>
                <p><b>Edad adoptante:</b> {row.get('Edad adoptante', 'N/A')}</p>
                <p><small>Coords: {coords_text}</small></p>
            </div>
            """
            
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(
                    color=color_info['color'],
                    icon=color_info['icon'],
                    prefix='glyphicon'
                ),
                tooltip=f"{row.get('Nombre Mascota', 'N/A')} - {status}"
            ).add_to(self.cluster)
    
    def generar_mapa_calor(self):
        heat_data = []
        for _, row in self.df.iterrows():
            if row['Buen adoptante'] == 'NO':
                if not pd.isna(row['Latitud']) and not pd.isna(row['Longitud']):
                    heat_data.append([row['Latitud'], row['Longitud'], 1])
        
        if heat_data:
            HeatMap(heat_data, name="Zonas problemáticas", radius=20).add_to(self.heat_layer)
    
    def agregar_controles(self):
        folium.LayerControl(collapsed=False).add_to(self.mapa)
        folium.plugins.MiniMap(toggle_display=True, position='bottomright').add_to(self.mapa)
    
    def guardar_mapa(self):
        title = f"""
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.5);">
            <h3 style="margin:0;">Mapa de Adopciones - Morelia</h3>
            <p style="margin:0; font-size:12px;">Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """
        self.mapa.get_root().html.add_child(folium.Element(title))
        
        css = """
        <style>
            .coords-input-container {
                display: flex;
                gap: 5px;
                margin-bottom: 10px;
            }
            
            .coords-input-container input {
                flex: 1;
                padding: 5px;
            }
            
            .coord-status {
                padding: 5px;
                border-radius: 4px;
                margin-top: 5px;
            }
            
            .valid {
                background-color: #d4edda;
                color: #155724;
            }
            
            .invalid {
                background-color: #f8d7da;
                color: #721c24;
            }
        </style>
        """
        self.mapa.get_root().html.add_child(folium.Element(css))
        
        script = """
        <script>
            function getMap() {
                for (var key in window) {
                    if (window[key] instanceof L.Map) {
                        return window[key];
                    }
                }
                return null;
            }
            
            let tempMarker = null;
            
            function mostrarFormulario() {
                const map = getMap();
                if (!map) {
                    alert("El mapa no está disponible. Por favor recargue la página.");
                    return;
                }
                
                const formContainer = document.createElement('div');
                formContainer.id = 'formContainer';
                formContainer.style.cssText = `
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    z-index: 1000;
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                    width: 350px;
                `;
                
                formContainer.innerHTML = `
                    <h4 style="margin-top: 0; color: #333;">Agregar Nuevo Caso</h4>
                    <form id="nuevoCasoForm">
                        <div class="form-group">
                            <label for="nombre">Nombre Mascota:*</label>
                            <input type="text" id="nombre" required style="width: 100%; padding: 5px; margin-bottom: 10px;">
                        </div>
                        
                        <div class="form-group">
                            <label for="domicilio">Domicilio:</label>
                            <input type="text" id="domicilio" style="width: 100%; padding: 5px; margin-bottom: 10px;">
                        </div>
                        
                        <div class="form-group">
                            <label for="edad">Edad adoptante:</label>
                            <input type="number" id="edad" style="width: 100%; padding: 5px; margin-bottom: 10px;">
                        </div>
                        
                        <div class="form-group">
                            <label for="fecha">Fecha:</label>
                            <input type="date" id="fecha" style="width: 100%; padding: 5px; margin-bottom: 10px;">
                        </div>
                        
                        <div class="form-group">
                            <label for="estado">Estado:</label>
                            <select id="estado" style="width: 100%; padding: 5px; margin-bottom: 10px;">
                                <option value="SI">Buen adoptante</option>
                                <option value="NO">Mal adoptante</option>
                                <option value="NA" selected>No especificado</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Ubicación:*</label>
                            <div class="coords-input-container">
                                <input type="text" id="latitud" placeholder="Latitud (ej. 19.7018)" style="width: 100%;">
                                <input type="text" id="longitud" placeholder="Longitud (ej. -101.1854)" style="width: 100%;">
                                <button type="button" onclick="validarCoordenadas()" 
                                        style="padding: 5px 10px; background: #2196F3; color: white; border: none; border-radius: 4px;">
                                    Validar
                                </button>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 5px;">
                                Haz clic en el mapa para seleccionar ubicación
                            </div>
                            <div id="coords-status" class="coord-status"></div>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <button type="button" onclick="guardarCaso()" style="padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                Guardar
                            </button>
                            <button type="button" onclick="cerrarFormulario()" style="padding: 8px 15px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                Cancelar
                            </button>
                        </div>
                    </form>
                `;
                
                document.body.appendChild(formContainer);
                map.on('click', handleMapClick);
            }
            
            function handleMapClick(e) {
                const map = getMap();
                if (!map || !document.getElementById('formContainer')) return;
                
                document.getElementById('latitud').value = e.latlng.lat.toFixed(6);
                document.getElementById('longitud').value = e.latlng.lng.toFixed(6);
                mostrarUbicacion(e.latlng.lat, e.latlng.lng);
                validarCoordenadas();
            }
            
            function validarCoordenadas() {
                const map = getMap();
                if (!map) return;
                
                const latInput = document.getElementById('latitud');
                const lngInput = document.getElementById('longitud');
                const coordsStatus = document.getElementById('coords-status');
                
                coordsStatus.innerHTML = '';
                coordsStatus.className = 'coord-status';
                
                try {
                    const lat = parseFloat(latInput.value.trim().replace(',', '.'));
                    const lng = parseFloat(lngInput.value.trim().replace(',', '.'));
                    
                    if (isNaN(lat) || isNaN(lng)) {
                        throw new Error("Por favor ingrese valores numéricos válidos");
                    }
                    
                    if (lat < -90 || lat > 90) {
                        throw new Error("La latitud debe estar entre -90 y 90");
                    }
                    
                    if (lng < -180 || lng > 180) {
                        throw new Error("La longitud debe estar entre -180 y 180");
                    }
                    
                    coordsStatus.innerHTML = "✓ Coordenadas válidas";
                    coordsStatus.classList.add('valid');
                    mostrarUbicacion(lat, lng);
                    map.setView([lat, lng], 16);
                    
                } catch (error) {
                    coordsStatus.innerHTML = "✗ " + error.message;
                    coordsStatus.classList.add('invalid');
                }
            }
            
            function mostrarUbicacion(lat, lng) {
                const map = getMap();
                if (!map) return;
                
                if (tempMarker) {
                    map.removeLayer(tempMarker);
                }
                
                tempMarker = L.marker([lat, lng], {
                    icon: L.icon({
                        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    }),
                    draggable: true
                }).addTo(map);
                
                tempMarker.on('dragend', function(e) {
                    const newLatLng = e.target.getLatLng();
                    document.getElementById('latitud').value = newLatLng.lat.toFixed(6);
                    document.getElementById('longitud').value = newLatLng.lng.toFixed(6);
                    validarCoordenadas();
                });
            }
            
            function guardarCaso() {
                const nombre = document.getElementById('nombre').value.trim();
                const domicilio = document.getElementById('domicilio').value.trim();
                const edad = document.getElementById('edad').value;
                const estado = document.getElementById('estado').value;
                const lat = document.getElementById('latitud').value;
                const lng = document.getElementById('longitud').value;
                const fecha = document.getElementById('fecha').value;
                
                if (!nombre) {
                    alert("⚠️ Por favor ingrese el nombre de la mascota");
                    return;
                }
                
                if (!lat || !lng) {
                    alert("⚠️ Por favor seleccione una ubicación");
                    return;
                }
                
                let fechaFinal = fecha;
                if (!fechaFinal) {
                    // Si no se seleccionó fecha, usar la fecha actual
                    fechaFinal = new Date().toISOString().split('T')[0];
                }
                
                const nuevoCaso = {
                    Fecha: fechaFinal,
                    'Nombre Mascota': nombre,
                    Domicilio: domicilio,
                    'Edad adoptante': edad,
                    'Buen adoptante': estado,
                    Latitud: lat,
                    Longitud: lng
                };
                
                fetch('/guardar_caso', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(nuevoCaso)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("✅ Caso guardado exitosamente. La página se recargará automáticamente.");
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        alert("❌ Error al guardar: " + data.message);
                    }
                })
                .catch(error => {
                    alert("❌ Error de conexión: " + error);
                });
            }
            
            function cerrarFormulario() {
                const map = getMap();
                if (!map) return;
                
                if (tempMarker) {
                    map.removeLayer(tempMarker);
                    tempMarker = null;
                }
                
                map.off('click', handleMapClick);
                
                const formContainer = document.getElementById('formContainer');
                if (formContainer) {
                    formContainer.remove();
                }
            }
            
            // Botón flotante para agregar casos
            const addButton = document.createElement('button');
            addButton.innerHTML = '➕ Agregar Caso';
            addButton.style.cssText = `
                position: fixed;
                top: 200px;
                right: 20px;
                z-index: 1000;
                padding: 10px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            addButton.onclick = mostrarFormulario;
            document.body.appendChild(addButton);
            
            // Botón flotante para descargar datos
            const downloadButton = document.createElement('button');
            downloadButton.innerHTML = '📥 Descargar Datos';
            downloadButton.style.cssText = `
                position: fixed;
                top: 150px;
                right: 20px;
                z-index: 1000;
                padding: 10px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            downloadButton.onclick = function() {
                fetch('/descargar_datos')
                    .then(response => response.blob())
                    .then(blob => {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'Adoptantes_Completos.xlsx';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                    })
                    .catch(error => {
                        alert('Error al descargar: ' + error.message);
                    });
            };
            document.body.appendChild(downloadButton);
        </script>
        """
        self.mapa.get_root().html.add_child(folium.Element(script))
        self.mapa.save(self.archivo_mapa)
    
    def ejecutar(self):
        print("\n=== Mapa Interactivo de Adopciones ===")
        print("Cargando datos y generando mapa...")
        
        if not self.cargar_datos():
            return False
            
        self.crear_mapa_base()
        self.agregar_marcadores()
        self.generar_mapa_calor()
        self.agregar_controles()
        self.guardar_mapa()
        
        print(f"\n✅ Mapa generado exitosamente")
        return True
