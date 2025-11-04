from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
from abc import ABC, abstractmethod

class Cine:
    def __init__(self, nombre):
        self.nombre = nombre
        self.salas = []
        self.cartelera = []
        self.ventas = []
        self.usuarios = []

    def registrar_usuario(self, nombre, correo, contraseña):
        for u in self.usuarios:
            if u.correo == correo:
                print("⚠️ Ya existe un usuario registrado con ese correo.")
                return None

        nuevo_cliente = Cliente(nombre, correo, contraseña)
        self.usuarios.append(nuevo_cliente)
        print(f"✅ Usuario '{nombre}' registrado exitosamente.")
        return nuevo_cliente

    def iniciar_sesion(self, correo, contraseña):
        for u in self.usuarios:
            if u.correo == correo and u.contraseña == contraseña:
                print(f"✅ Bienvenido de nuevo, {u.nombre}!")
                return u
        print("❌ Correo o contraseña incorrectos.")
        return None

    def agregar_peliculas(self, Pelicula):
        self.cartelera.append(Pelicula)
        print(f"Pelicula '{Pelicula.titulo}' agregada a la cartelera.")

    def mostrar_cartelera(self):
        if not self.cartelera:
            print("No hay peliculas en la cartelera actualmente.")
        else:
            print(f"\n--- Cartelera del cine {self.nombre} ---")
            for p in self.cartelera:
                p.mostrar_informacion()

    def vender_boleto(self, cliente, pelicula, horario, asientos):
        if pelicula not in self.cartelera:
            print("La pelicula no esta en cartelera")
            return

        if not pelicula.tiene_horario(horario):
            print("El horario no esta disponible")
            return

        if not self.salas:
            print("No hay salas disponibles en el cine")
            return

        sala = self.salas[0]

        try:
            disponibles = all(not sala.asientos[a] for a in asientos)
        except KeyError:
            print("Uno o mas asientos seleccionados no existen")
            return

        if not disponibles:
            print("Uno o mas asientos ya estan ocupados")
            return

        for a in asientos:
            sala.asientos[a] = True

        codigo = str(uuid.uuid4())
        boleto = Boleto(
            codigo=codigo,
            pelicula=pelicula.titulo,
            horario=horario,
            asientos=asientos,
            cliente=cliente.nombre
        )

        self.ventas.append(boleto)
        cliente.boletos.append(boleto)
        print(f"Boleto generado con éxito. Código: {codigo}")

    def cancelar_boleto(self, codigo):
        for boleto in self.ventas:
            if boleto.codigo == codigo:
                sala = self.salas[0]
                for a in boleto.asientos:
                    if a in sala.asientos:
                        sala.asientos[a] = False

                self.ventas.remove(boleto)
                print(f"Boleto {codigo} cancelado y asientos liberados.")
                return
        print("No se encontró ningún boleto con ese código.")

    def mostrar_estadisticas(self):
        if not self.ventas:
            print("No hay ventas registradas aún.")
            return

        conteo_peliculas = {}
        conteo_horarios = {}
        conteo_clientes = {}

        total_asientos_vendidos = 0
        for boleto in self.ventas:
            num_asientos = len(boleto.asientos)
            total_asientos_vendidos += num_asientos

            conteo_peliculas[boleto.pelicula] = conteo_peliculas.get(boleto.pelicula, 0) + num_asientos
            conteo_horarios[boleto.horario] = conteo_horarios.get(boleto.horario, 0) + num_asientos
            conteo_clientes[boleto.cliente] = conteo_clientes.get(boleto.cliente, 0) + num_asientos

        pelicula_top = max(conteo_peliculas, key=conteo_peliculas.get)
        horario_top = max(conteo_horarios, key=conteo_horarios.get)
        cliente_top = max(conteo_clientes, key=conteo_clientes.get)

        capacidad_total = sum(len(sala.asientos) for sala in self.salas) if self.salas else 100
        ocupacion = (total_asientos_vendidos / capacidad_total) * 100 if capacidad_total > 0 else 0.0

        print("\n --- Estadísticas del Cine ---")
        print(f" Película más vendida: {pelicula_top} ({conteo_peliculas[pelicula_top]} asientos vendidos)")
        print(f" Horario más popular: {horario_top} ({conteo_horarios[horario_top]} asientos vendidos)")
        print(f" Cliente más activo: {cliente_top} ({conteo_clientes[cliente_top]} asientos vendidos)")
        print(f" Asientos vendidos totales: {total_asientos_vendidos} / {capacidad_total}")
        print(f" Ocupación total del cine: {ocupacion:.2f}%\n")

    def recomendar_funcion(self, pelicula):
        if not self.salas:
            print("No hay salas disponibles para hacer recomendaciones.")
            return

        sala = self.salas[0]  # por simplicidad usamos la primera sala
        total_asientos = len(sala.asientos)
        ocupados = sum(sala.asientos.values())
        porcentaje_ocupacion = (ocupados / total_asientos) * 100

        print(f"\nLa sala para '{pelicula.titulo}' tiene una ocupación del {porcentaje_ocupacion:.2f}%.")

        if porcentaje_ocupacion >= 80:
            print("⚠️ Esta función está bastante llena.")
            # Buscar otra película con menos ocupación si existe
            sugerida = None
            menor_ocupacion = 100
            for p in self.cartelera:
                total_asientos = len(sala.asientos)
                ocupados = sum(sala.asientos.values())
                ocupacion_actual = (ocupados / total_asientos) * 100
                if ocupacion_actual < menor_ocupacion:
                    menor_ocupacion = ocupacion_actual
                    sugerida = p

            if sugerida and sugerida != pelicula:
                print(f"🎬 Te recomendamos ver '{sugerida.titulo}', tiene solo {menor_ocupacion:.2f}% de ocupación.")
            else:
                print("No hay otra función con menor ocupación disponible.")
        elif porcentaje_ocupacion <= 30:
            print("✅ Excelente elección, la sala está bastante libre.")
        else:
            print(" La ocupación es moderada, hay buena disponibilidad de asientos.")

@dataclass
class Pelicula:
    titulo: str
    genero: str
    duracion: int
    clasificacion: int
    horarios: list[str] = field(default_factory=list)

    def mostrar_informacion(self):
        print(f"\nPelícula: {self.titulo}")
        print(f"Género: {self.genero}")
        print(f"Duración: {self.duracion} minutos")
        print(f"Clasificación: {self.clasificacion}+ años")
        print(f"Horarios disponibles: {', '.join(self.horarios) if self.horarios else 'No definidos'}")

    def agregar_horario(self, horario):
        if horario not in self.horarios:
            self.horarios.append(horario)
            print(f"Horario {horario} agregado para '{self.titulo}'.")
        else:
            print(f"El horario {horario} ya existe para esta pelicula.")

    def eliminar_horario(self, horario):
        if horario in self.horarios:
            self.horarios.remove(horario)
            print(f"Horario {horario} eliminado de '{self.titulo}'.")
        else:
            print(f"El horario {horario} no existe en esta pelicula.")

    def tiene_horario(self, horario):
        return horario in self.horarios


@dataclass
class Sala:
    numero: int
    filas: int = 10
    columnas: int = 10
    asientos: dict[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        if not self.asientos:
            for fila in range(self.filas):
                letra = chr(65 + fila)
                for col in range(1, self.columnas + 1):
                    asiento = f"{letra}{col}"
                    self.asientos[asiento] = False

    def mostrar_asientos(self):
        print(f"\nPlano de asientos - Sala {self.numero}")
        for fila in range(self.filas):
            letra = chr(65 + fila)
            fila_asientos = []
            for col in range(1, self.columnas + 1):
                asiento = f"{letra}{col}"
                estado = "❌" if self.asientos[asiento] else "🟩"
                fila_asientos.append(estado)
            print(f"{letra}: {' '.join(fila_asientos)}")
        print("🟩 Disponible | ❌ Ocupado\n")


@dataclass
class Boleto:
    codigo: str
    pelicula: str
    horario: str
    asientos: list[str]
    cliente: str
    coleccionables: Optional[str] = None
    fecha_compra: datetime = field(default_factory=datetime.now)

    def mostrar_detalles(self):
        print("\n--- Detalles del Boleto ---")
        print(f"Código: {self.codigo}")
        print(f"Película: {self.pelicula}")
        print(f"Horario: {self.horario}")
        print(f"Asientos: {', '.join(self.asientos)}")
        print(f"Cliente: {self.cliente}")
        print(f"Fecha de compra: {self.fecha_compra.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.coleccionables:
            print(f"Coleccionable incluido: {self.coleccionables}")
        else:
            print("Coleccionable: Ninguno")
        print("------------------------------\n")

@dataclass
class Persona(ABC):
    nombre: str
    correo: str

    @abstractmethod
    def mostrar_informacion(self): ...


class Cliente(Persona):
    def __init__(self, nombre: str, correo: str, contraseña):
        super().__init__(nombre, correo)
        self.contraseña = contraseña
        self.boletos = []


    def comprar_boleto(self, cine, pelicula, horario, asientos):
        print(f"\n{self.nombre} está comprando boletos para '{pelicula.titulo}' en el horario {horario}...")
        cine.vender_boleto(self, pelicula, horario, asientos)


    def cancelar_boletos(self, cine, codigo):
        boleto_encontrado = None
        for b in self.boletos:
            if b.codigo == codigo:
                boleto_encontrado = b
                break
            if boleto_encontrado:
                cine.cancelar_boletos(codigo)
                self.boletos.remove(boleto_encontrado)
                print(f"{self.nombre} cancelo el boleto con codigo {codigo}")
            else:
                print(f"No se encontro ningun boleto con el codigo {codigo}en el historial del cliente")


    def mostrar_boletos(self):
        if not self.boletos:
            print(f"\n{self.nombre} no tiene boletos comprados actualmente.")
        else:
            print (f"\n--- Boletos de {self.nombre} ---")
            for b in self.boletos:
                b.mostrar_detalles()

    def mostrar_informacion(self):
        print(f"cliente: {self.nombre} - {self.correo}")


class Administrador(Cliente):
    def __init__(self, nombre: str, id_admin: str, correo: str, contraseña: str):
        super().__init__(nombre, correo, contraseña)
        self.id_admin = id_admin


    def agregar_pelicula(self, cine, pelicula):
        print(f"\n{self.nombre} está agregando una nueva película al cine '{cine.nombre}'...")


    def eliminar_pelicula(self, cine, titulo_pelicula):
        for p in cine.cartelera:
            if p.titulo == titulo_pelicula:
                cine.cartelera.remove(p)
                print(f"Película '{titulo_pelicula}' eliminada de la cartelera del cine '{cine.nombre}'.")
                return
        print(f"No se encontro pelicula '{titulo_pelicula}' en la cartelera")

    def consultar_cartelera(self, cine):
        print(f"\nCartelera actual del cine '{cine.nombre}':")
        cine.mostrar_cartelera()