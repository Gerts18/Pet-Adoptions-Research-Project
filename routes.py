from flask import Blueprint, request, jsonify, render_template, current_app
import pandas as pd
from io import BytesIO
from mapa_core import MapaAdopcionesCompleto 

bp = Blueprint('main', __name__)
mapa_app = MapaAdopcionesCompleto()

@bp.route('/')
def index():
    if mapa_app.ejecutar():
        return render_template('mapa_interactivo.html')
    return "Error al generar el mapa", 500

@bp.route('/guardar_caso', methods=['POST'])
def guardar_caso():
    try:
        data = request.json
        try:
            lat = float(data['Latitud'])
            lng = float(data['Longitud'])
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return jsonify({
                    'success': False, 
                    'message': 'Coordenadas fuera de rango válido'
                })
        except (ValueError, TypeError):
            return jsonify({
                'success': False, 
                'message': 'Coordenadas deben ser números válidos'
            })
        df = pd.read_excel(mapa_app.archivo_datos)
        nuevo_registro = {
            'Fecha': data['Fecha'],
            'Nombre Mascota': data['Nombre Mascota'],
            'Domicilio': data['Domicilio'],
            'Edad adoptante': data['Edad adoptante'],
            'Buen adoptante': data['Buen adoptante'],
            'Latitud': lat,
            'Longitud': lng
        }
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_excel(mapa_app.archivo_datos, index=False)
        mapa_app.cargar_datos()
        return jsonify({
            'success': True, 
            'message': 'Caso guardado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': str(e)
        })

@bp.route('/descargar_datos')
def descargar_datos():
    try:
        mapa_app.cargar_datos()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            mapa_app.df.to_excel(writer, index=False)
        output.seek(0)
        return current_app.response_class(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment;filename=Adoptantes_Completos.xlsx'}
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
