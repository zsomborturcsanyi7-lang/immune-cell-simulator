import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, virus_strain=0):
        super().__init__(model)
        self.virus_strain = virus_strain # 0 is healthy
        self.viral_load = 0.0

    def step(self):
        if self.virus_strain > 0:
            self.viral_load += self.model.viral_aggression
            
            # Spread to neighbors
            if self.viral_load > 20:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, HostCell) and neighbor.virus_strain == 0:
                        if random.random() < self.model.spread_chance:
                            # MUTATION LOGIC: High chance to drift to a new strain
                            new_strain = self.virus_strain
                            if random.random() < self.model.mutation_rate:
                                new_strain += 1
                                self.model.total_strains_evolved = max(self.model.total_strains_evolved, new_strain)
                            
                            neighbor.virus_strain = new_strain

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set()

    def step(self):
        # Move
        possible = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, random.choice(possible))

        # 1. Listen for Broadcasts (Radius 6 for better coverage)
        for (strain, pos, radius) in self.model.active_broadcasts:
            dist = ((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2)**0.5
            if dist <= radius:
                self.authorized_strains.add(strain)

        # 2. Check and Neutralize
        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.virus_strain > 0:
                if obj.virus_strain in self.authorized_strains:
                    obj.virus_strain = 0
                    obj.viral_load = 0
                    self.model.inflammation += 1
                    self.model.atp_reserve -= 0.5
                else:
                    self.model.register_ping(self.pos, obj)
                break

class DendriticCell(mesa.Agent):
    def step(self):
        if self.model.pings:
            # Process up to 2 pings to simulate limited bandwidth
            for _ in range(2):
                if not self.model.pings: break
                pos, cell = self.model.pings.pop(0)
                self.model.grid.move_agent(self, pos)
                if cell.virus_strain > 0:
                    # Broadcast the specific strain authorization
                    self.model.active_broadcasts.append((cell.virus_strain, pos, 6))

class EvolutionaryModel(mesa.Model):
    def __init__(self, width, height, aggression, mutation_rate):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.viral_aggression = aggression
        self.mutation_rate = mutation_rate
        self.spread_chance = 0.05
        self.atp_reserve = 15000
        self.inflammation = 0
        self.pings = []
        self.active_broadcasts = []
        self.total_strains_evolved = 1
        self.history = {"infected": [], "strains": [], "atp": []}

        # Initial infection
        for x in range(width):
            for y in range(height):
                is_inf = 1 if random.random() < 0.03 else 0 # 3% start
                a = HostCell(self, virus_strain=is_inf)
                self.grid.place_agent(a, (x, y))

        for _ in range(40): self.grid.place_agent(ADTTCell(self), (random.randrange(width), random.randrange(height)))
        for _ in range(5): self.grid.place_agent(DendriticCell(self), (random.randrange(width), random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        self.agents.shuffle_do("step")
        inf_cells = [a for a in self.agents if isinstance(a, HostCell) and a.virus_strain > 0]
        inf_count = len(inf_cells)
        active_strains = len(set(c.virus_strain for c in inf_cells))
        
        self.history["infected"].append(inf_count)
        self.history["strains"].append(active_strains)
        self.history["atp"].append(self.atp_reserve)
        
        # Decay broadcasts
        if self.steps % 3 == 0: self.active_broadcasts = []
        
        # Host Death
        if self.atp_reserve < 1000: self.running = False
        if inf_count == 0: self.running = False

def run_evolutionary_test():
    # Moderate aggression (10), Very high mutation (20% per spread)
    model = EvolutionaryModel(30, 30, aggression=10, mutation_rate=0.2)
    
    print("Starting Evolutionary Persistence Test (Mutating 'Cold' Virus)...")
    steps = 0
    while model.running and steps < 500:
        model.step()
        steps += 1
        if steps % 50 == 0:
            print(f"Step {steps}: Infected: {model.history['infected'][-1]}, Strains: {model.history['strains'][-1]}, ATP: {model.atp_reserve:.0f}")

    print(f"\n--- EVOLUTIONARY TEST RESULTS ---")
    print(f"Duration: {steps} steps")
    print(f"Total Strains Evolved: {model.total_strains_evolved}")
    print(f"Final ATP: {model.atp_reserve:.2f}")
    print(f"System Status: {'CLEARED' if model.history['infected'][-1] == 0 else 'PERSISTENT INFECTION'}")

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    ax1.plot(model.history["infected"], color='red', label="Infected Cells")
    ax2.plot(model.history["strains"], color='purple', linestyle='--', label="Active Strains")
    ax1.set_xlabel("Steps")
    ax1.set_ylabel("Infected Count", color='red')
    ax2.set_ylabel("Active Strains Count", color='purple')
    plt.title("ADT Response to Rapidly Mutating Pathogen")
    plt.savefig("adt-simulator/evolutionary_test.png")
    print("Graph saved as 'adt-simulator/evolutionary_test.png'")

if __name__ == "__main__":
    run_evolutionary_test()
