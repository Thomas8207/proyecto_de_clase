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