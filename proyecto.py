from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

class Cine:
    def __init__(self, nombre):
        self.nombre = nombre
        self.salas = []
        self.cartelera = []
        self.ventas = []

    def agregar_peliculas(self, Pelicula):
        self.cartelera.append(Pelicula)
        print(f"Pelicula'{Pelicula.titulo}'agregada a la cartelera.")

    def mostrar_cartelera(self):
        if not self.cartelera:
            print("No hay peliculas en la cartelera actualmente.")
        else:
            print(f"/n--- Cartelera del cine {self.nombre} ---")

    def vender_boleto(self, cliente, pelicula, horario, asientos):
        if pelicula not in self.cartelera:
            print("la pelicula no esta en cartelera")
            return

        if not pelicula.tiene_horario(horario):
            print("el horario no esta disponible")
            return

        if not self.salas:
            print("no hay salas disponibles en el cine")
            return

        sala = self.salas[0]

        try:
            disponibles = all(not sala.asientos[a] for a in asientos)
        except KeyError:
            print("uno o mas asientos seleccionados no existen")
            return

        if not disponibles:
            print("uno o mas asientos ya estan ocupados")
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
                print(f"✅ Boleto {codigo} cancelado y asientos liberados.")
                return
        print("❌ No se encontró ningún boleto con ese código.")
