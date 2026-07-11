import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, infected=False, acidic=False):
        super().__init__(model)
        self.infected = infected
        self.acidic = acidic
        self.stress_signal = False
        self.age = 0
        self.max_age = self.random.randint(80, 120)

    def step(self):
        self.age += 1
        
        # 1. Biological Noise: Natural Cell Death & Turnover
        if self.age > self.max_age or (self.infected and self.random.random() < 0.05):
            self.die()
            return

        self.stress_signal = self.infected or self.acidic
        
        # 2. Viral Replication
        if self.infected:
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for neighbor in neighbors:
                if isinstance(neighbor, HostCell) and not neighbor.infected:
                    if self.random.random() < self.model.replication_rate:
                        neighbor.infected = True
        
        # Metabolism: Passive cost of being alive
        self.model.atp_reserve -= 0.01

    def die(self):
        # Reset cell (replacement by stem cell)
        self.infected = False
        self.acidic = self.random.random() < 0.05 # 5% chance new cell is stressed
        self.age = 0
        self.stress_signal = False

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_tokens = {} # cell -> TTL

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, self.random.choice(possible_steps))
        self.model.atp_reserve -= 0.1 # Movement cost

    def step(self):
        self.move()
        
        # 3. Token TTL (Time to Live) Management
        expired = [cell for cell, ttl in self.authorized_tokens.items() if ttl <= 0]
        for cell in expired: del self.authorized_tokens[cell]
        for cell in self.authorized_tokens: self.authorized_tokens[cell] -= 1

        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        for obj in neighbors:
            if isinstance(obj, HostCell) and obj.stress_signal:
                if obj in self.authorized_tokens:
                    # Verified Liquidation
                    obj.infected = False
                    obj.stress_signal = False
                    self.model.atp_reserve -= 2.0 # Liquidation is expensive
                    self.model.inflammation += 1
                else:
                    # Ping
                    self.model.register_ping(self.pos, obj)
                    self.model.atp_reserve -= 0.5 # Communication cost
                break

class DendriticCell(mesa.Agent):
    def step(self):
        if self.model.pings:
            target_pos, target_cell = self.model.pings.pop(0)
            self.model.grid.move_agent(self, target_pos)
            self.model.atp_reserve -= 1.0 # High movement/analysis cost
            
            if target_cell.infected:
                # Issue Token with TTL
                nearby_tcells = [a for a in self.model.agents if isinstance(a, ADTTCell)]
                for tcell in nearby_tcells:
                    tcell.authorized_tokens[target_cell] = 10 # 10 steps TTL

class BioNetworkModel(mesa.Model):
    def __init__(self, width, height, replication_rate):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.atp_reserve = 5000 # Starting energy
        self.inflammation = 0
        self.replication_rate = replication_rate
        self.pings = []
        self.history = {"atp": [], "infected": []}

        # Create Host Cells
        for x in range(width):
            for y in range(height):
                is_inf = self.random.random() < 0.05
                a = HostCell(self, infected=is_inf)
                self.grid.place_agent(a, (x, y))

        for i in range(10):
            t = ADTTCell(self)
            self.grid.place_agent(t, (self.random.randrange(width), self.random.randrange(height)))

        dc = DendriticCell(self)
        self.grid.place_agent(dc, (self.random.randrange(width), self.random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        self.agents.shuffle_do("step")
        self.history["atp"].append(self.atp_reserve)
        self.history["infected"].append(sum(1 for a in self.agents if isinstance(a, HostCell) and a.infected))

def run_bio_complex_sim():
    model = BioNetworkModel(15, 15, 0.05)
    for _ in range(200):
        model.step()
        if model.atp_reserve <= 0:
            print("!!! HOST DEATH: METABOLIC COLLAPSE !!!")
            break
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(model.history["infected"], color='red', label="Infection")
    ax1.set_title("Viral Load")
    ax1.set_ylabel("Count")
    ax2.plot(model.history["atp"], color='blue', label="ATP")
    ax2.set_title("Metabolic Reserves (ATP)")
    ax2.set_ylabel("Energy")
    plt.savefig("adt-simulator/complex_bio_sim.png")
    print(f"Final ATP: {model.atp_reserve:.2f}, Final Inflammation: {model.inflammation}")

if __name__ == "__main__":
    run_bio_complex_sim()
