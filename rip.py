MAX_HOPS = 15

class Route:
    # Semplice classe che definisce gli attributi di una rotta
    def __init__(self, distance, hops, next):
        self.distance = distance
        self.hops = hops
        self.next = next

class Node:
    # Il nodo rappresenta un router nel grafo della rete
    # ha i riferimenti solo a i suoi vicini
    # contiene una propria tabella di routing
    def __init__(self, name):
        self.name = name.strip()
        self.neighbors = []
        self.routing_table = {self.name: Route(0, 0, self.name)}

    def addNeighbor(self, neighbor, distance):
        # La tabella di routing viene aggiornata con l'aggiunta di un vicino la cui rotta è triviale
        self.neighbors.append(neighbor)
        self.routing_table[neighbor.name] = Route(distance, 1, neighbor.name)

    def updateRoutingTable(self, neighbor, neighbor_routing_table):
        # Aggiorna la propria tabella di routing con quella che gli è stata mandata tramite la logica dell'algorito distance-vector
        # Se viene scoperto un nuovo nodo per cui non esisteva nessuna rotta viene aggiunta una riga alla tabella
        # Se una nuova rotta conterebbe un numero di salti troppo elevato non viene aggiornata
        # Ritorna un booleano True se è stata modificata anche una sola rotta per capire quando si è raggiunta la convergenza
        isChanged = False
        for destination, route in neighbor_routing_table:
            current_route = self.routing_table.get(destination)
            distance = self.routing_table[neighbor.name].distance + route.distance
            hops = route.hops + 1
            if hops < MAX_HOPS and (not current_route or distance < current_route.distance):
                self.routing_table[destination] = Route(distance, hops, neighbor.name)
                isChanged = True
        return isChanged
    
    def updateNeighbors(self):
        # il nodo chiama l'aggiornamento su tutti i vicini mandando la propria tabella di routing
        # ma vengono omesse le rotte che hanno il destinatario come prossimo (Split Horizon)
        isChanged = False
        for neighbor in self.neighbors:
            isChanged |= neighbor.updateRoutingTable(
                self,
                [(d, r) for d, r in self.routing_table.items() if r.next != neighbor.name]
            )
        return isChanged

def networkInit(name_file):
    # funzione per istanziare il grafo della network da un file di testo
    # Ogni nodo riceve i riferimenti a tutti i suoi vicini
    graph = {}
    with open(name_file, "r") as file:
        for linea in file:
            node, neighbors_str = linea.strip().split(";")
            node = node.strip()
            neighbors = [v.strip() for v in neighbors_str.split(",")]
            if node not in graph:
                graph[node] = Node(node)
            for neighbor in neighbors:
                name_neighbor, distance = neighbor.split(":")
                name_neighbor = name_neighbor.strip()
                if name_neighbor not in graph:
                    graph[name_neighbor] = Node(name_neighbor)
                graph[node].addNeighbor(graph[name_neighbor], int(distance))
    return graph

# Simulazione
name_file = "graph.txt"
network = networkInit(name_file)

isChanged = True
counter = 0
while isChanged:
    isChanged = False
    counter += 1
    for node in network.values():
        isChanged |= node.updateNeighbors()

# Output
print("Cicli per la convergenza: ", counter)
for node in network.values():
    print(f"Routing table per nodo {node.name}:")
    for destination, route in node.routing_table.items():
        print(f"  {destination} -> {route.next} ; distanza: {route.distance}, salti: {route.hops}")
