import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, virus_type=0):
        super().__init__(model)
        self.virus_type = virus_type # 0 = Healthy, 1, 2, 3... = Strains
        self.stress_signal = False
        self.age = 0
        self.max_age = self.random.randint(80, 150)

    @property
    def infected(self):
        return self.virus_type > 0

    def step(self):
        self.age += 1
        if self.age > self.max_age or (self.infected and self.random.random() < 0.03):
            self.die()
            return

        self.stress_signal = self.infected
        
        # Viral Replication + Mutation
        if self.infected and self.pos[0] < self.model.tissue_width: # Only in tissue
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            for neighbor in neighbors:
                if isinstance(neighbor, HostCell) and not neighbor.infected:
                    if self.random.random() < self.model.replication_rate:
                        # Mutation Logic
                        new_virus = self.virus_type
                        if self.random.random() < self.model.mutation_rate:
                            new_virus += 1 # New strain!
                        neighbor.virus_type = new_virus
        
        self.model.atp_reserve -= 0.01

    def die(self):
        self.virus_type = 0
        self.age = 0
        self.stress_signal = False

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set() # Acquired in Lymph Node

    def move(self):
        # Move randomly but stay within current zone unless activated? 
        # For simplicity, full freedom but cost reflects distance.
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, self.random.choice(possible_steps))
        self.model.atp_reserve -= 0.1

    def step(self):
        self.move()
        is_in_lymph = self.pos[0] >= self.model.tissue_width

        if is_in_lymph:
            # Acquire tokens from the Lymph Node environment (broadcasted by DCs)
            if self.model.lymph_node_tokens:
                self.authorized_strains.update(self.model.lymph_node_tokens)

        else: # In Tissue
            contents = self.model.grid.get_cell_list_contents([self.pos])
            for obj in contents:
                if isinstance(obj, HostCell) and obj.stress_signal:
                    if obj.virus_type in self.authorized_strains:
                        # Verified Kill
                        obj.virus_type = 0
                        self.model.atp_reserve -= 2.0
                        self.model.inflammation += 1
                    else:
                        # Ping
                        self.model.register_ping(self.pos, obj)
                    break

class DendriticCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.sample = None # Stores virus_type
        self.state = "PATROL" # PATROL, TRAVEL_TO_NODE, AUTHENTICATING, TRAVEL_TO_TISSUE

    def step(self):
        self.model.atp_reserve -= 0.2
        is_in_lymph = self.pos[0] >= self.model.tissue_width

        if self.state == "PATROL":
            if self.model.pings:
                target_pos, target_cell = self.model.pings.pop(0)
                self.model.grid.move_agent(self, target_pos)
                if target_cell.infected:
                    self.sample = target_cell.virus_type
                    self.state = "TRAVEL_TO_NODE"
            else:
                # Random patrol in tissue
                possible = [p for p in self.model.grid.get_neighborhood(self.pos, moore=True) if p[0] < self.model.tissue_width]
                if possible: self.model.grid.move_agent(self, self.random.choice(possible))

        elif self.state == "TRAVEL_TO_NODE":
            # Move towards x = tissue_width
            new_x = min(self.pos[0] + 1, self.model.grid.width - 1)
            self.model.grid.move_agent(self, (new_x, self.pos[1]))
            if new_x >= self.model.tissue_width:
                self.state = "AUTHENTICATING"
                self.auth_timer = 3 # 3 steps to process

        elif self.state == "AUTHENTICATING":
            self.auth_timer -= 1
            if self.auth_timer <= 0:
                self.model.lymph_node_tokens.add(self.sample)
                self.sample = None
                self.state = "PATROL"

class ADTHighFidelityModel(mesa.Model):
    def __init__(self, width, height, tissue_width, repl_rate, mut_rate):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.tissue_width = tissue_width
        self.atp_reserve = 5000
        self.inflammation = 0
        self.replication_rate = repl_rate
        self.mutation_rate = mut_rate
        self.pings = []
        self.lymph_node_tokens = set()
        self.history = {"atp": [], "infected": [], "strains": []}

        # Setup Grid
        for x in range(width):
            for y in range(height):
                if x < tissue_width:
                    is_inf = 1 if self.random.random() < 0.05 else 0
                    a = HostCell(self, virus_type=is_inf)
                    self.grid.place_agent(a, (x, y))

        for _ in range(15): self.grid.place_agent(ADTTCell(self), (self.random.randrange(width), self.random.randrange(height)))
        for _ in range(3): self.grid.place_agent(DendriticCell(self), (self.random.randrange(tissue_width), self.random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        if self.atp_reserve < 1500:
            self.running = False
            return

        self.agents.shuffle_do("step")
        
        inf_cells = [a for a in self.agents if isinstance(a, HostCell) and a.infected]
        self.history["atp"].append(self.atp_reserve)
        self.history["infected"].append(len(inf_cells))
        self.history["strains"].append(len(set(c.virus_type for c in inf_cells if c.virus_type > 0)))

def run_high_fid_sim():
    # Width 25, Tissue 15, Lymph 10
    model = ADTHighFidelityModel(25, 20, 15, repl_rate=0.08, mut_rate=0.05)
    
    steps = 0
    for _ in range(300):
        model.step()
        steps += 1
        if not model.running or model.atp_reserve < 1500:
            print(f"!!! METABOLIC COLLAPSE AT STEP {steps} !!!")
            break
    
    print(f"Final ATP: {model.atp_reserve:.2f}")
    print(f"Final Strains Active: {model.history['strains'][-1]}")
    print(f"Total Inflammation: {model.inflammation}")

    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.plot(model.history["infected"], color='red', label="Total Infected")
    ax1.plot(model.history["strains"], color='purple', label="Distinct Strains", linestyle='--')
    ax1.set_title("Viral Evolution & Load")
    ax1.legend()
    
    ax2.plot(model.history["atp"], color='blue', label="ATP")
    ax2.axhline(y=1500, color='black', linestyle=':', label="Collapse Threshold")
    ax2.set_title("Metabolic Drain")
    ax2.legend()
    
    plt.savefig("adt-simulator/high_fidelity_results.png")
    print("Results saved to 'adt-simulator/high_fidelity_results.png'")

if __name__ == "__main__":
    run_high_fid_sim()
