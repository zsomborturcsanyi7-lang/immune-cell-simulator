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

    def step(self):
        self.stress_signal = self.infected or self.acidic
        # Viral Replication Logic
        if self.infected:
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for neighbor in neighbors:
                if isinstance(neighbor, HostCell) and not neighbor.infected:
                    if self.random.random() < self.model.replication_rate:
                        neighbor.infected = True

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_cells = set()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, self.random.choice(possible_steps))

    def step(self):
        self.move()
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, HostCell) and neighbor.stress_signal:
                if neighbor in self.authorized_cells:
                    neighbor.infected = False
                    neighbor.acidic = False
                    neighbor.stress_signal = False
                    self.authorized_cells.remove(neighbor)
                    self.model.inflammation += 1 
                else:
                    self.model.register_ping(neighbor.pos, neighbor)
                break

class DendriticCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        # Process pings only up to capacity
        for _ in range(self.model.dc_capacity):
            if self.model.pings:
                target_pos, target_cell = self.model.pings.pop(0)
                self.model.grid.move_agent(self, target_pos)
                if target_cell.infected:
                    nearby_tcells = [a for a in self.model.agents if isinstance(a, ADTTCell)]
                    for tcell in nearby_tcells:
                        tcell.authorized_cells.add(target_cell)
            else:
                break

class ADTModel(mesa.Model):
    def __init__(self, N_host_dim, N_tcell, replication_rate, dc_capacity, mode='ADT'):
        super().__init__()
        self.grid = mesa.space.MultiGrid(N_host_dim, N_host_dim, True)
        self.inflammation = 0
        self.replication_rate = replication_rate
        self.dc_capacity = dc_capacity
        self.pings = []
        
        for x in range(N_host_dim):
            for y in range(N_host_dim):
                rand = self.random.random()
                is_infected = rand < 0.02 # 2% initial infection
                is_acidic = 0.02 <= rand < 0.07 # 5% false alarm
                a = HostCell(self, infected=is_infected, acidic=is_acidic)
                self.grid.place_agent(a, (x, y))

        for i in range(N_tcell):
            a = ADTTCell(self)
            self.grid.place_agent(a, (self.random.randrange(N_host_dim), self.random.randrange(N_host_dim)))

        # 2 Dendritic Cells
        for i in range(2):
            a = DendriticCell(self)
            self.grid.place_agent(a, (self.random.randrange(N_host_dim), self.random.randrange(N_host_dim)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        self.agents.shuffle_do("step")

def run_sensitivity_analysis():
    replication_rates = np.linspace(0.01, 0.20, 10) # 1% to 20%
    iterations = 50 # Reduced from 1000 for speed in CLI environment, but enough for trend
    results = []

    print(f"Starting Sensitivity Analysis ({len(replication_rates)} rates, {iterations} iterations each)...")
    
    for rate in replication_rates:
        success_count = 0
        for _ in range(iterations):
            model = ADTModel(15, 10, rate, dc_capacity=2)
            for _ in range(100): # 100 steps
                model.step()
                infected_count = sum(1 for a in model.agents if isinstance(a, HostCell) and a.infected)
                if infected_count == 0:
                    success_count += 1
                    break
                if infected_count > 150: # System Collapse
                    break
        
        success_rate = (success_count / iterations) * 100
        results.append(success_rate)
        print(f"Rate {rate:.2f}: Success Rate {success_rate}%")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(replication_rates, results, marker='o', color='blue', linewidth=2)
    plt.axhline(y=50, color='red', linestyle='--', label="Collapse Threshold (50%)")
    plt.title("ADT Protocol Reliability vs Viral Replication Rate")
    plt.xlabel("Viral Replication Probability (per step)")
    plt.ylabel("Infection Clearance Success Rate (%)")
    plt.grid(True)
    plt.legend()
    plt.savefig("adt-simulator/sensitivity_analysis.png")
    print("\nAnalysis complete. Result saved as 'adt-simulator/sensitivity_analysis.png'")

if __name__ == "__main__":
    run_sensitivity_analysis()
