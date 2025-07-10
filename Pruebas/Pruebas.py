import csv
import networkx as nx
from collections import defaultdict
import random

G= nx.DiGraph() # crea un grafo dirigido

with open('BD Grafos.csv', newline='') as archivo_grafos:
    lee_grafos = csv.reader(archivo_grafos)
    next(lee_grafos)  # saltea la primera fila
    Prodx=input(" Ingrese que producto desea producir (A, B o C): ")
    producto_buscado = "Prod" + Prodx.upper()  # Ejemplo: 'A' -> 'ProdA'
    for fila in lee_grafos:
        for i in range(len(fila)):
            if fila[0] == producto_buscado:
                for i in range(0, len(fila)-1, 2):
                    destino = fila[i]
                    origen = fila[i+1]
                    if origen and destino:
                        G.add_edge(origen, destino)
id_carritos=[]         
with open('Carritos.csv', newline='') as archivo_Carritos:
    lector_carritos = csv.reader(archivo_Carritos)
    next(lector_carritos)  # saltea la primera fila
    for fila in lector_carritos:
        for i in range(len(fila)):
            id_carritos.append(fila[i])  # Agrega cada ID de carrito a la lista
            

inventario={}

with open ('BD Materias Primas.csv', newline='') as archivo_materias:
    lector = csv.reader(archivo_materias)
    for row in lector:
        nombre=row[0]
        ubicacion=row[1]
        unidades=row[2]
        if nombre and ubicacion and unidades:
            inventario[nombre] = {'ubicacion': ubicacion, 'unidades': unidades}

Subproductos={}

with open ('BD SubProductos.csv', newline='') as archivo_subproductos: #SubProducto,Operación,Nº Estación,Tiempo de procesado,Tiempo llegada estación
    lector = csv.reader(archivo_subproductos)
    for row in lector:
        SubProducto=row[0]
        Operacion=row[1]
        Estacion=row[2]
        if SubProducto and Operacion and Estacion:
            Subproductos[SubProducto] = {'operacion': Operacion, 'estacion': Estacion}

materias_primas = [n for n in G.nodes if G.in_degree(n) == 0] # creacion de lista de materias primas (nodos sin predecesores)
#print(materias_primas)


print("\nVerificación de stock del depósito:")

for mp in materias_primas:
    if mp in inventario:
        data = inventario[mp]
        unidades = int(data['unidades'])  # Conversión a entero
        if unidades > 0:
            print(f"[OK] Retirar '{mp}' desde ubicación {data['ubicacion']} ({unidades} disponibles).")

        else:

            print(f"[ERROR] No hay unidades disponibles de '{mp}' (ubicación {data['ubicacion']}).")

    else:

        print(f"[ERROR] '{mp}' no está registrado en el inventario.")

# Orden de producción (Topological sort)


orden = list(nx.topological_sort(G))
print("Orden sugerido de producción:")
for item in orden:
    print("-", item)


niveles = {}

for nodo in orden:

    predecesores = list(G.predecessors(nodo))  # nodos que apuntan a este

    if not predecesores:
        niveles[nodo] = 0  # materia prima
    else:
        niveles[nodo] = 1 + max(niveles[p] for p in predecesores)

def subprod(origen, carro, destino, insumo, tarea):
    print(f"Frenar un carrito cualquiera en la estacion {origen} ")
    print(f"se frenó el carrito de ID= {carro}")
    print(f"Retirar {insumo} de la estacion {origen} y ubicarlo en el carrito")
    print(f"Enviar carrito a la estacion {(destino)}")
    print(f"Carrito es frenado en la estación {(destino)} para realizar {(tarea)}")
    print(f"se le ordena a la estacion {(destino)} que extraiga el subproducto {insumo} del carrito")
    print(f"carrito {carro} es dejado ir")
    

def matprima(carro, destino, insumo, tarea):
    print(f"Frenar carrito en el deposito para cargar Materia prima")
    print(f"se frenó el carrito de ID= {carro}")
    print(f"se posiciona a {insumo} en el carrito")
    print(f"Se suelta el carrito y va dirigido a estacion {destino} para realizar {tarea}")
    print(f"Carrito es frenado en la estación {destino}")
    print(f"se le ordena a la estacion {destino} que extraiga la materia prima {insumo} del carrito {carro}")
    print(f"carrito {carro} es dejado ir")
    
# Agrupamos nodos por nivel para mostrar por etapas

por_nivel = defaultdict(list)

for nodo, nivel in niveles.items():

    por_nivel[nivel].append(nodo)

carritos_rdm = random.sample(id_carritos, 20)
car=0
# Mostramos cada etapa: primero las materias primas, luego los procesos

print("\nDesglose por etapas:")

for nivel in sorted(por_nivel):

    # Etapa 0 = materia prima, el resto son subproductos/procesos

    etapa = "Materias primas" if nivel == 0 else f"Etapa {nivel}"
    print(f"{etapa}:")

    for nodo in por_nivel[nivel]:

        insumos = list(G.predecessors(nodo))  # qué necesito para producir este nodo
        
        if insumos:
            estacion = Subproductos[nodo]['estacion'] if nodo in Subproductos else "Desconocida"
            operacion = Subproductos[nodo]['operacion'] if nodo in Subproductos else "Desconocida"
            if estacion == "Desconocida" and operacion == "Desconocida":
                print (f"{nodo} terminado")
            elif len(insumos) == 2:
                if insumos[0] and insumos[1] in Subproductos:
                    # Acción si ambos insumos están en Subproductos
                    estacion_origen_0 = Subproductos[insumos[0]]['estacion'] if insumos[0] in Subproductos else "Desconocida"
                    estacion_origen_1 = Subproductos[insumos[1]]['estacion'] if insumos[1] in Subproductos else "Desconocida"

                    subprod(estacion_origen_0, carritos_rdm[car], estacion, insumos[0], operacion)
                    print(f"se procede con el siguiente subproducto")
                    car += 1
                    
                    subprod(estacion_origen_1, carritos_rdm[car], estacion, insumos[1], operacion)
                    print(f"se Ordena a la estacion {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                    car += 1
                
                elif insumos[0] or insumos[1] in Subproductos:
                    if insumos[0] in Subproductos:
                        estacion_origen = Subproductos[insumos[0]]['estacion'] if insumos[0] in Subproductos else "Desconocida"
                        subprod(estacion_origen, carritos_rdm[car], estacion, insumos[0], operacion)
                        print(f"se procede con el siguiente subproducto")
                        car += 1
                    elif insumos[1] in Subproductos:
                        estacion_origen = Subproductos[insumos[1]]['estacion'] if insumos[1] in Subproductos else "Desconocida"
                        subprod(estacion_origen, carritos_rdm[car], estacion, insumos[1], operacion)
                        print(f"se Ordena a {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                        car += 1
            
                    elif insumos[0] in inventario and insumos[1] in inventario:
                        matprima(carritos_rdm[car], estacion, insumos[0], operacion)
                        print(f"se procede con la siguiente materia prima")
                        car += 1
                        
                        matprima(carritos_rdm[car], estacion, insumos[1], operacion)
                        print(f"se Ordena a {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                        car += 1
                        
            elif len(insumos) == 3:
                if insumos[0] in inventario and insumos[1] in inventario and insumos[2] in inventario:
                    matprima(carritos_rdm[car], estacion, insumos[0], operacion)
                    print(f"se procede con la siguiente materia prima")
                    car += 1
                    
                    matprima(carritos_rdm[car], estacion, insumos[1], operacion)
                    print(f"se procede con la siguiente materia prima")
                    car += 1
                    
                    matprima(carritos_rdm[car], estacion, insumos[2], operacion)
                    print(f"se Ordena a {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                    car += 1

                elif insumos[0] and insumos[1] in Subproductos and insumos[2] in inventario:
                    estacion_origen_0 = Subproductos[insumos[0]]['estacion'] if insumos[0] in Subproductos else "Desconocida"
                    estacion_origen_1 = Subproductos[insumos[1]]['estacion'] if insumos[1] in Subproductos else "Desconocida"
                    subprod(estacion_origen_0, carritos_rdm[car], estacion, insumos[0], operacion)
                    print(f"se procede con el siguiente subproducto")
                    car += 1
                    
                    subprod(estacion_origen_1, carritos_rdm[car], estacion, insumos[1], operacion)
                    print(f" se procede con el siguiente subproducto")
                    car += 1
                    
                    matprima(carritos_rdm[car], estacion, insumos[2], operacion)
                    print(f"se Ordena a {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                    car += 1
                      
                elif insumos[0] and insumos[1] in inventario and insumos[2] in Subproductos:
                    estacion_origen = Subproductos[insumos[2]]['estacion'] if insumos[2] in Subproductos else "Desconocida"
                    matprima(carritos_rdm[car], estacion, insumos[0], operacion)
                    print(f"se procede con la siguiente materia prima")
                    car += 1
                    
                    matprima(carritos_rdm[car], estacion, insumos[1], operacion)
                    print(f"se procede con la siguiente materia prima")
                    car += 1
    
                    subprod(estacion_origen, carritos_rdm[car], estacion, insumos[2], operacion)
                    print(f"se Ordena a {(estacion)} que realice la operación {(operacion)} para producir {(nodo)}")
                    car += 1
                    

                


