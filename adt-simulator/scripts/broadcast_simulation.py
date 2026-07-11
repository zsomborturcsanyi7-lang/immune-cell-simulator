import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, virus_type=0):
        super().__init__(model)
        self.virus_type = virus_type
        self.viral_load = 0.0

    def step(self):
        if self.virus_type > 0:
            self.viral_load += self.model.viral_aggression
            if self.viral_load > 30:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, HostCell) and neighbor.virus_type == 0:
                        if random.random() < 0.1:
                            neighbor.virus_type = self.virus_type

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set()

    def step(self):
        # Move
        possible = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, random.choice(possible))

        # 1. Listen for Exosome Cloud (Broadcast)
        for (strain, pos, radius) in self.model.active_broadcasts:
            # Manual Euclidean distance
            dist = ((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2)**0.5
            if dist <= radius:
                self.authorized_strains.add(strain)

        # 2. Act
        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.virus_type > 0:
                if obj.virus_type in self.authorized_strains:
                    obj.virus_type = 0
                    obj.viral_load = 0
                    self.model.inflammation += 1
                else:
                    self.model.register_ping(self.pos, obj)
                break

class DendriticCell(mesa.Agent):
    def step(self):
        if self.model.pings:
            pos, cell = self.model.pings.pop(0)
            self.model.grid.move_agent(self, pos)
            if cell.virus_type > 0:
                # NEW: EXOSOME BROADCAST (Radius = 5)
                self.model.active_broadcasts.append((cell.virus_type, pos, 5))
                self.model.log_event("BROADCAST_EMITTED", pos)

class BroadcastModel(mesa.Model):
    def __init__(self, width, height, aggression):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.viral_aggression = aggression
        self.pings = []
        self.active_broadcasts = [] # (strain, pos, radius)
        self.inflammation = 0
        self.history = {"infected": []}

        for x in range(width):
            for y in range(height):
                is_inf = 1 if random.random() < 0.1 else 0
                a = HostCell(self, virus_type=is_inf)
                self.grid.place_agent(a, (x, y))

        for _ in range(30): self.grid.place_agent(ADTTCell(self), (random.randrange(width), random.randrange(height)))
        for _ in range(5): self.grid.place_agent(DendriticCell(self), (random.randrange(width), random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def log_event(self, type, pos):
        pass # Internal logging

    def step(self):
        self.agents.shuffle_do("step")
        inf_count = sum(1 for a in self.agents if isinstance(a, HostCell) and a.virus_type > 0)
        self.history["infected"].append(inf_count)
        if inf_count == 0: self.running = False

def run_broadcast_test():
    print("Running ADT 'Exosome Cloud' Broadcast Simulation...")
    model = BroadcastModel(25, 25, aggression=20)
    
    steps = 0
    while model.running and steps < 200:
        model.step()
        steps += 1
        # Clear broadcasts every 5 steps (Signal decay)
        if steps % 5 == 0: model.active_broadcasts = []

    print(f"\n--- BROADCAST PROTOCOL RESULTS ---")
    print(f"Total Steps to Clearance: {steps}")
    print(f"System Status: {'SUCCESS' if steps < 200 else 'FAILED'}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(model.history["infected"], color='blue', linewidth=3, label="Exosome Cloud (Broadcast)")
    plt.title("ADT Broadcast vs Apocalypse Scenario")
    plt.xlabel("Steps")
    plt.ylabel("Infected Population")
    plt.savefig("adt-simulator/broadcast_test.png")
    print("Graph saved as 'adt-simulator/broadcast_test.png'")

if __name__ == "__main__":
    run_broadcast_test()
