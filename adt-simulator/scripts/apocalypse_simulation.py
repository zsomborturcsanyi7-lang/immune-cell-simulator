import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, virus_type=0):
        super().__init__(model)
        self.virus_type = virus_type
        self.viral_load = 0 # 0-100%
        self.stress_signal = False

    def step(self):
        if self.virus_type > 0:
            self.viral_load += self.model.viral_aggression
            self.stress_signal = True
            
            # Massive Replication: Infects ALL neighbors if load > 50%
            if self.viral_load > 50:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, HostCell) and neighbor.virus_type == 0:
                        if self.random.random() < 0.5: # 50% chance to infect per neighbor
                            neighbor.virus_type = self.virus_type

            # Cell death at 100% load
            if self.viral_load >= 100:
                self.die()

    def die(self):
        self.virus_type = 0
        self.viral_load = 0
        self.stress_signal = False

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set()
        self.kills = 0

    def move(self):
        # Hyper-speed movement in high-stress scenario
        for _ in range(2): 
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            self.model.grid.move_agent(self, self.random.choice(possible_steps))

    def step(self):
        self.move()
        # Edge Computing: Check for local tokens broadcasted by DCs
        if self.model.local_tokens:
            self.authorized_strains.update(self.model.local_tokens)

        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.stress_signal:
                if obj.virus_type in self.authorized_strains:
                    obj.virus_type = 0
                    obj.viral_load = 0
                    self.kills += 1
                    self.model.inflammation += 1
                    self.model.atp_reserve -= 1.0
                else:
                    self.model.register_ping(self.pos, obj)
                break

class DendriticCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.tokens_issued = 0

    def step(self):
        # Processing Pings at 1.1 optimized speed
        for _ in range(3): # Process 3 pings per step
            if self.model.pings:
                start_time = self.model.steps
                pos, cell = self.model.pings.pop(0)
                if cell.virus_type > 0:
                    self.model.local_tokens.add(cell.virus_type)
                    self.tokens_issued += 1
                    # Record recognition latency
                    self.model.latencies.append(self.model.steps - start_time)

class ApocalypseModel(mesa.Model):
    def __init__(self, width, height, aggression):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.viral_aggression = aggression
        self.atp_reserve = 10000
        self.inflammation = 0
        self.pings = []
        self.local_tokens = set()
        self.latencies = []
        self.history = {"infected": [], "atp": []}

        # Setup: 10% Initial Infection (The Apocalypse)
        for x in range(width):
            for y in range(height):
                is_inf = 1 if self.random.random() < 0.1 else 0
                a = HostCell(self, virus_type=is_inf)
                self.grid.place_agent(a, (x, y))

        for _ in range(30): self.grid.place_agent(ADTTCell(self), (self.random.randrange(width), self.random.randrange(height)))
        for _ in range(5): self.grid.place_agent(DendriticCell(self), (self.random.randrange(width), self.random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        self.agents.shuffle_do("step")
        inf_count = sum(1 for a in self.agents if isinstance(a, HostCell) and a.virus_type > 0)
        self.history["infected"].append(inf_count)
        self.history["atp"].append(self.atp_reserve)
        
        if inf_count == 0:
            self.running = False

def run_gauntlet():
    # Aggression 20: Each infected cell fills 20% viral load per step (Extremely fast)
    model = ApocalypseModel(25, 25, aggression=20)
    
    steps = 0
    while model.running and steps < 200:
        model.step()
        steps += 1
        if model.atp_reserve < 1500:
            break
            
    print(f"--- GAUNTLET RESULTS ---")
    print(f"Total Steps to Clearance: {steps}")
    print(f"Avg Recognition Latency: {np.mean(model.latencies):.2f} steps")
    print(f"Tokens Issued: {len(model.local_tokens)}")
    print(f"Final ATP: {model.atp_reserve:.2f}")
    print(f"System Status: {'SUCCESS' if sum(1 for a in model.agents if isinstance(a, HostCell) and a.virus_type > 0) == 0 else 'COLLAPSE'}")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(model.history["infected"], color='darkred', linewidth=3, label="Viral Cells")
    plt.title("Apocalypse Scenario: ADT Response Under Extreme Pressure")
    plt.xlabel("Time Steps")
    plt.ylabel("Infected Population")
    plt.grid(True)
    plt.savefig("assets/apocalypse_test.png")
    print("Graph saved as 'assets/apocalypse_test.png'")
if __name__ == "__main__":
    run_gauntlet()
