from flask import Flask, render_template, jsonify, request, session
from proyecto import Cine, Pelicula, Sala, Cliente, Administrador, Boleto
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'cinemax_secret_key_2024'  # Para manejar sesiones

# Inicializar el cine y datos
cine = Cine("CINEMAX")

# Diccionario para gestionar salas por película y horario
# Estructura: salas_por_funcion[pelicula_titulo][horario] = Sala
salas_por_funcion = {}

# Agregar películas de ejemplo
peliculas_iniciales = [
    Pelicula("Dune: Parte Dos", "Ciencia Ficción", 166, 13, ["14:00", "17:30", "21:00"]),
    Pelicula("Oppenheimer", "Drama/Biografía", 180, 16, ["15:00", "19:00", "22:30"]),
    Pelicula("Spider-Man: A Través del Spider-Verso", "Animación/Acción", 140, 7, ["13:00", "16:00", "19:30"]),
    Pelicula("Barbie", "Comedia/Fantasía", 114, 7, ["14:30", "17:00", "20:00"]),
    Pelicula("The Batman", "Acción/Suspenso", 176, 13, ["16:30", "20:30"])
]

# Contador para números de sala
contador_sala = 1

for pelicula in peliculas_iniciales:
    cine.agregar_peliculas(pelicula)

    # Crear una sala independiente para cada horario de la película
    salas_por_funcion[pelicula.titulo] = {}
    for horario in pelicula.horarios:
        nueva_sala = Sala(numero=contador_sala, filas=10, columnas=10)
        salas_por_funcion[pelicula.titulo][horario] = nueva_sala
        cine.salas.append(nueva_sala)
        contador_sala += 1

# Administrador predeterminado
admin = Administrador("Admin", "ADM001", "admin@cinemax.com", "admin123")
admin.contraseña = "admin123"
cine.usuarios.append(admin)


def obtener_sala(pelicula_titulo, horario):
    """Obtiene la sala específica para una película y horario"""
    if pelicula_titulo in salas_por_funcion:
        if horario in salas_por_funcion[pelicula_titulo]:
            return salas_por_funcion[pelicula_titulo][horario]
    return None


def obtener_cliente_actual():
    """Obtiene el cliente actual de la sesión"""
    correo = session.get('usuario_correo')
    if correo:
        for usuario in cine.usuarios:
            if usuario.correo == correo:
                return usuario
    return None


# RUTAS DE LA API

@app.route('/')
def index():
    """Renderiza la página principal"""
    return render_template('index.html')


@app.route('/api/auth/registro', methods=['POST'])
def registro():
    """Registra un nuevo usuario"""
    data = request.json
    nombre = data.get('nombre')
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    # Verificar si ya existe
    for u in cine.usuarios:
        if u.correo == correo:
            return jsonify({'error': 'Ya existe un usuario con ese correo'}), 400

    # Crear nuevo cliente
    nuevo_cliente = Cliente(nombre, correo, contraseña)
    cine.usuarios.append(nuevo_cliente)

    # Iniciar sesión automáticamente
    session['usuario_correo'] = correo
    session['usuario_nombre'] = nombre
    session['es_admin'] = False

    return jsonify({
        'success': True,
        'mensaje': 'Usuario registrado exitosamente',
        'usuario': {
            'nombre': nombre,
            'correo': correo,
            'es_admin': False
        }
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Inicia sesión de un usuario"""
    data = request.json
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    for usuario in cine.usuarios:
        if usuario.correo == correo and usuario.contraseña == contraseña:
            session['usuario_correo'] = correo
            session['usuario_nombre'] = usuario.nombre
            session['es_admin'] = isinstance(usuario, Administrador)

            return jsonify({
                'success': True,
                'mensaje': f'Bienvenido de nuevo, {usuario.nombre}!',
                'usuario': {
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'es_admin': isinstance(usuario, Administrador)
                }
            })

    return jsonify({'error': 'Correo o contraseña incorrectos'}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Cierra sesión del usuario"""
    session.clear()
    return jsonify({'success': True, 'mensaje': 'Sesión cerrada'})


@app.route('/api/auth/session', methods=['GET'])
def get_session():
    """Obtiene la información de la sesión actual"""
    if 'usuario_correo' in session:
        return jsonify({
            'logged_in': True,
            'usuario': {
                'nombre': session.get('usuario_nombre'),
                'correo': session.get('usuario_correo'),
                'es_admin': session.get('es_admin', False)
            }
        })
    return jsonify({'logged_in': False})


@app.route('/api/cartelera', methods=['GET'])
def get_cartelera():
    """Obtiene todas las películas en cartelera"""
    peliculas = []
    for p in cine.cartelera:
        peliculas.append({
            'titulo': p.titulo,
            'genero': p.genero,
            'duracion': p.duracion,
            'clasificacion': p.clasificacion,
            'horarios': p.horarios
        })
    return jsonify(peliculas)


@app.route('/api/asientos/<pelicula>/<horario>', methods=['GET'])
def get_asientos(pelicula, horario):
    """Obtiene el estado de los asientos para una película y horario específicos"""
    sala = obtener_sala(pelicula, horario)
    if sala:
        return jsonify(sala.asientos)
    return jsonify({})


@app.route('/api/recomendacion/<pelicula>/<horario>', methods=['GET'])
def get_recomendacion(pelicula, horario):
    """Obtiene recomendación de ocupación para una función"""
    sala = obtener_sala(pelicula, horario)

    if not sala:
        return jsonify({'error': 'Sala no encontrada'}), 404

    total_asientos = len(sala.asientos)
    ocupados = sum(sala.asientos.values())
    porcentaje_ocupacion = (ocupados / total_asientos) * 100

    mensaje = ""
    nivel = ""

    if porcentaje_ocupacion >= 80:
        mensaje = "⚠️ Esta función está bastante llena."
        nivel = "alta"
    elif porcentaje_ocupacion <= 30:
        mensaje = "✅ Excelente elección, la sala está bastante libre."
        nivel = "baja"
    else:
        mensaje = "La ocupación es moderada, hay buena disponibilidad de asientos."
        nivel = "media"

    return jsonify({
        'ocupacion': round(porcentaje_ocupacion, 2),
        'asientos_disponibles': total_asientos - ocupados,
        'asientos_totales': total_asientos,
        'mensaje': mensaje,
        'nivel': nivel
    })


@app.route('/api/comprar', methods=['POST'])
def comprar_boleto():
    """Procesa la compra de boletos"""
    cliente = obtener_cliente_actual()
    if not cliente:
        return jsonify({'error': 'Debes iniciar sesión para comprar boletos'}), 401

    data = request.json
    pelicula_titulo = data.get('pelicula')
    horario = data.get('horario')
    asientos = data.get('asientos')
    coleccionable = data.get('coleccionable', None)  # Nuevo campo opcional

    # Buscar la película
    pelicula = None
    for p in cine.cartelera:
        if p.titulo == pelicula_titulo:
            pelicula = p
            break

    if not pelicula:
        return jsonify({'error': 'Película no encontrada'}), 404

    if not pelicula.tiene_horario(horario):
        return jsonify({'error': 'Horario no disponible'}), 400

    # Obtener la sala específica para esta función
    sala = obtener_sala(pelicula_titulo, horario)
    if not sala:
        return jsonify({'error': 'Sala no disponible'}), 404

    # Verificar disponibilidad de asientos
    try:
        disponibles = all(not sala.asientos[a] for a in asientos)
    except KeyError:
        return jsonify({'error': 'Uno o más asientos seleccionados no existen'}), 400

    if not disponibles:
        return jsonify({'error': 'Uno o más asientos ya están ocupados'}), 400

    # Marcar asientos como ocupados
    for a in asientos:
        sala.asientos[a] = True

    # Crear boleto con coleccionable
    codigo = str(uuid.uuid4())
    boleto = Boleto(
        codigo=codigo,
        pelicula=pelicula.titulo,
        horario=horario,
        asientos=asientos,
        cliente=cliente.nombre,
        coleccionables=coleccionable,  # Incluir coleccionable
        fecha_compra=datetime.now()
    )

    cine.ventas.append(boleto)
    cliente.boletos.append(boleto)

    return jsonify({
        'success': True,
        'codigo': codigo,
        'mensaje': 'Boleto comprado exitosamente'
    })


@app.route('/api/boletos', methods=['GET'])
def get_boletos():
    """Obtiene los boletos del cliente actual"""
    cliente = obtener_cliente_actual()
    if not cliente:
        return jsonify({'error': 'Debes iniciar sesión'}), 401

    boletos = []
    for b in cliente.boletos:
        boletos.append({
            'codigo': b.codigo,
            'pelicula': b.pelicula,
            'horario': b.horario,
            'asientos': b.asientos,
            'fecha': b.fecha_compra.isoformat()
        })
    return jsonify(boletos)


@app.route('/api/cancelar/<codigo>', methods=['DELETE'])
def cancelar_boleto(codigo):
    """Cancela un boleto y libera los asientos en la sala correspondiente"""
    cliente = obtener_cliente_actual()
    if not cliente:
        return jsonify({'error': 'Debes iniciar sesión'}), 401

    # Buscar el boleto en el cliente
    boleto_encontrado = None
    for b in cliente.boletos:
        if b.codigo == codigo:
            boleto_encontrado = b
            break

    if not boleto_encontrado:
        return jsonify({'error': 'Boleto no encontrado'}), 404

    # Obtener la sala específica de esta función
    sala = obtener_sala(boleto_encontrado.pelicula, boleto_encontrado.horario)

    if sala:
        # Liberar los asientos
        for asiento in boleto_encontrado.asientos:
            if asiento in sala.asientos:
                sala.asientos[asiento] = False

    # Eliminar el boleto de las ventas del cine
    if boleto_encontrado in cine.ventas:
        cine.ventas.remove(boleto_encontrado)

    # Eliminar el boleto del cliente
    cliente.boletos.remove(boleto_encontrado)

    return jsonify({'success': True, 'mensaje': 'Boleto cancelado exitosamente'})


@app.route('/api/admin/agregar-pelicula', methods=['POST'])
def agregar_pelicula():
    """Agrega una nueva película (Admin)"""
    if not session.get('es_admin'):
        return jsonify({'error': 'Acceso denegado'}), 403

    data = request.json
    try:
        nueva_pelicula = Pelicula(
            titulo=data['titulo'],
            genero=data['genero'],
            duracion=int(data['duracion']),
            clasificacion=int(data['clasificacion']),
            horarios=data['horarios']
        )

        # Buscar el admin
        admin_usuario = obtener_cliente_actual()
        if isinstance(admin_usuario, Administrador):
            admin_usuario.agregar_pelicula(cine, nueva_pelicula)
        else:
            cine.agregar_peliculas(nueva_pelicula)

        # Crear salas para cada horario de la nueva película
        global contador_sala
        salas_por_funcion[nueva_pelicula.titulo] = {}
        for horario in nueva_pelicula.horarios:
            nueva_sala = Sala(numero=contador_sala, filas=10, columnas=10)
            salas_por_funcion[nueva_pelicula.titulo][horario] = nueva_sala
            cine.salas.append(nueva_sala)
            contador_sala += 1

        return jsonify({'success': True, 'mensaje': 'Película agregada exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/eliminar-pelicula/<titulo>', methods=['DELETE'])
def eliminar_pelicula(titulo):
    """Elimina una película (Admin)"""
    if not session.get('es_admin'):
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        # Eliminar las salas asociadas a la película
        if titulo in salas_por_funcion:
            salas_a_eliminar = list(salas_por_funcion[titulo].values())
            for sala in salas_a_eliminar:
                if sala in cine.salas:
                    cine.salas.remove(sala)
            del salas_por_funcion[titulo]

        # Eliminar la película de la cartelera
        admin_usuario = obtener_cliente_actual()
        if isinstance(admin_usuario, Administrador):
            admin_usuario.eliminar_pelicula(cine, titulo)
        else:
            for p in cine.cartelera:
                if p.titulo == titulo:
                    cine.cartelera.remove(p)
                    break

        return jsonify({'success': True, 'mensaje': 'Película eliminada exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/estadisticas', methods=['GET'])
def get_estadisticas():
    """Obtiene las estadísticas del cine"""
    if not session.get('es_admin'):
        return jsonify({'error': 'Acceso denegado'}), 403

    if not cine.ventas:
        return jsonify({
            'topMovie': 'N/A',
            'topMovieSales': 0,
            'totalSold': 0,
            'totalCapacity': sum(len(sala.asientos) for sala in cine.salas),
            'occupation': 0,
            'ventas_por_pelicula': {}
        })

    conteo_peliculas = {}
    total_asientos_vendidos = 0

    for boleto in cine.ventas:
        num_asientos = len(boleto.asientos)
        total_asientos_vendidos += num_asientos
        conteo_peliculas[boleto.pelicula] = conteo_peliculas.get(boleto.pelicula, 0) + num_asientos

    pelicula_top = max(conteo_peliculas, key=conteo_peliculas.get) if conteo_peliculas else 'N/A'
    capacidad_total = sum(len(sala.asientos) for sala in cine.salas) if cine.salas else 100
    ocupacion = (total_asientos_vendidos / capacidad_total) * 100 if capacidad_total > 0 else 0.0

    return jsonify({
        'topMovie': pelicula_top,
        'topMovieSales': conteo_peliculas.get(pelicula_top, 0),
        'totalSold': total_asientos_vendidos,
        'totalCapacity': capacidad_total,
        'occupation': round(ocupacion, 2),
        'ventas_por_pelicula': conteo_peliculas
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)