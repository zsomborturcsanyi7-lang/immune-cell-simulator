import mesa
import random
import matplotlib.pyplot as plt

class HostCell(mesa.Agent):
    """A host cell that can be infected or just stressed (false alarm)."""
    def __init__(self, model, infected=False, acidic=False):
        super().__init__(model)
        self.infected = infected
        self.acidic = acidic # False alarm cause (e.g. muscle fatigue)
        self.stress_signal = False

    def step(self):
        # Stress signal triggered by infection OR acidity
        self.stress_signal = self.infected or self.acidic

class ADTTCell(mesa.Agent):
    """ADT T-Cell: Monitors stress, pings for verification, and liquidates only if authorized."""
    def __init__(self, model):
        super().__init__(model)
        self.authorized_cells = set()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, HostCell) and neighbor.stress_signal:
                if neighbor in self.authorized_cells:
                    # Verified Liquidation
                    neighbor.infected = False
                    neighbor.acidic = False
                    neighbor.stress_signal = False
                    self.authorized_cells.remove(neighbor)
                    self.model.inflammation += 1 
                else:
                    # Ping for verification
                    self.model.register_ping(neighbor.pos, neighbor)
                break

class StandardTCell(mesa.Agent):
    """Standard T-Cell: Kills immediately upon detecting stress (High False Positives)."""
    def __init__(self, model):
        super().__init__(model)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, HostCell) and neighbor.stress_signal:
                # Immediate Kill (Doesn't care if it's virus or just acidity)
                neighbor.infected = False
                neighbor.acidic = False
                neighbor.stress_signal = False
                self.model.inflammation += 10 
                break

class DendriticCell(mesa.Agent):
    """Turbo Dendritic Cell: Verifies pings using 'Sandbox' analysis."""
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        if self.model.pings:
            target_pos, target_cell = self.model.pings[0]
            self.model.grid.move_agent(self, target_pos)
            
            # Double-Check: Only release token if it's REALLY a virus
            if target_cell.infected:
                # Release token: authorize all ADT T-cells in vicinity
                nearby_tcells = [a for a in self.model.agents if isinstance(a, ADTTCell)]
                for tcell in nearby_tcells:
                    tcell.authorized_cells.add(target_cell)
            else:
                # False alarm detected!
                pass
            
            self.model.pings.pop(0)

class ADTModel(mesa.Model):
    def __init__(self, N_host, N_tcell, width, height, mode='ADT'):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.inflammation = 0
        self.mode = mode
        self.pings = []
        self.history = {"inflammation": [], "infected": []}

        # Create Host Cells (1 per cell for simplicity)
        for x in range(width):
            for y in range(height):
                # 5% Virus, 10% Acidity (False Alarm)
                rand = self.random.random()
                is_infected = rand < 0.05
                is_acidic = 0.05 <= rand < 0.15
                a = HostCell(self, infected=is_infected, acidic=is_acidic)
                self.grid.place_agent(a, (x, y))

        # Create T-Cells
        for i in range(N_tcell):
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            if mode == 'ADT':
                a = ADTTCell(self)
            else:
                a = StandardTCell(self)
            self.grid.place_agent(a, (x, y))

        if mode == 'ADT':
            # Create 2 Dendritic Cells
            for i in range(2):
                x = self.random.randrange(width)
                y = self.random.randrange(height)
                a = DendriticCell(self)
                self.grid.place_agent(a, (x, y))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        self.agents.shuffle_do("step")
        # Track metrics
        inf_count = sum(1 for a in self.agents if isinstance(a, HostCell) and a.infected)
        self.history["inflammation"].append(self.inflammation)
        self.history["infected"].append(inf_count)

def run_simulations():
    width, height, steps = 20, 20, 100
    
    print("Running STD simulation...")
    std_model = ADTModel(400, 15, width, height, mode='STD')
    for _ in range(steps): std_model.step()
    
    print("Running ADT simulation...")
    adt_model = ADTModel(400, 15, width, height, mode='ADT')
    for _ in range(steps): adt_model.step()

    # Generate Graphs
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(std_model.history["infected"], label="Standard (Kill-on-sight)", color='red', linestyle='--')
    ax1.plot(adt_model.history["infected"], label="ADT (Verified)", color='green')
    ax1.set_title("Infected Cells Over Time")
    ax1.set_xlabel("Steps")
    ax1.set_ylabel("Count")
    ax1.legend()

    ax2.plot(std_model.history["inflammation"], label="Standard (High Stress)", color='red', linestyle='--')
    ax2.plot(adt_model.history["inflammation"], label="ADT (Whisper Mode)", color='green')
    ax2.set_title("Cumulative Inflammation (Cytokine Level)")
    ax2.set_xlabel("Steps")
    ax2.set_ylabel("Score")
    ax2.legend()

    plt.tight_layout()
    plt.savefig("assets/simulation_results.png")
    print("\nSimulation complete. Graph saved as 'assets/simulation_results.png'")
    
    print(f"Final Inflammation - STD: {std_model.inflammation}, ADT: {adt_model.inflammation}")
    print(f"Final Infected - STD: {std_model.history['infected'][-1]}, ADT: {adt_model.history['infected'][-1]}")

if __name__ == "__main__":
    run_simulations()
