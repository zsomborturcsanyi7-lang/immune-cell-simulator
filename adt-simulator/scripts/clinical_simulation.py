import mesa
import random
import matplotlib.pyplot as plt
import numpy as np

class HostCell(mesa.Agent):
    def __init__(self, model, infected=False):
        super().__init__(model)
        self.infected = infected
        self.viral_load = 0.0
        self.stress_signal = False
        self.health = 100.0

    def step(self):
        if self.infected:
            self.viral_load += self.model.viral_aggression
            self.stress_signal = True
            
            # Replication: SARS-CoV-2 style (droplet/neighbor spread)
            if self.viral_load > 25:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
                for neighbor in neighbors:
                    if isinstance(neighbor, HostCell) and not neighbor.infected:
                        if random.random() < self.model.transmission_rate:
                            neighbor.infected = True
            
            # Damage to host cell
            self.health -= (self.viral_load / 10.0)
            if self.health <= 0:
                self.die()

    def die(self):
        self.infected = False
        self.viral_load = 0
        self.stress_signal = False
        self.health = 100.0 # Regeneration/Scarring

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set()

    def step(self):
        # Move randomly
        possible = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, random.choice(possible))

        # 1. Listen for Exosome Broadcast
        for (strain, pos, radius) in self.model.active_broadcasts:
            dist = ((self.pos[0] - pos[0])**2 + (self.pos[1] - pos[1])**2)**0.5
            if dist <= radius:
                self.authorized_strains.add(strain)

        # 2. Quiet Liquidation (Whisper Mode)
        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.infected:
                if 1 in self.authorized_strains: # SARS-CoV-2 is Strain 1
                    obj.infected = False
                    obj.viral_load = 0
                    self.model.adt_kills += 1
                    self.model.inflammation += 0.5 # Minimal
                    self.model.atp_reserve -= 0.5
                else:
                    self.model.register_ping(self.pos, obj)
                break

class StandardTCell(mesa.Agent):
    """Wild-type immune system: Causes Cytokine Storm."""
    def step(self):
        possible = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        self.model.grid.move_agent(self, random.choice(possible))

        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.stress_signal:
                obj.infected = False
                obj.viral_load = 0
                self.model.std_kills += 1
                self.model.inflammation += 15.0 # CYTOKINE STORM!
                self.model.atp_reserve -= 2.0
                break

class DendriticCell(mesa.Agent):
    def step(self):
        if self.model.pings:
            pos, cell = self.model.pings.pop(0)
            self.model.grid.move_agent(self, pos)
            if cell.infected:
                self.model.active_broadcasts.append((1, pos, 6))

class ClinicalModel(mesa.Model):
    def __init__(self, width, height, adt_injection_step=50):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.viral_aggression = 5.0
        self.transmission_rate = 0.15
        self.atp_reserve = 20000
        self.inflammation = 0
        self.adt_kills = 0
        self.std_kills = 0
        self.pings = []
        self.active_broadcasts = []
        self.adt_injected = False
        self.adt_injection_step = adt_injection_step
        self.history = {"infected": [], "inflammation": [], "atp": []}

        # Initial infection (Patient Zero)
        for x in range(width):
            for y in range(height):
                is_inf = random.random() < 0.02
                a = HostCell(self, infected=is_inf)
                self.grid.place_agent(a, (x, y))

        # Initial Wild-Type Immune System (Weak/Uncoordinated)
        for _ in range(15):
            self.grid.place_agent(StandardTCell(self), (random.randrange(width), random.randrange(height)))

    def register_ping(self, pos, agent):
        if (pos, agent) not in self.pings:
            self.pings.append((pos, agent))

    def step(self):
        # 1. ADT THERAPY INJECTION (Step 20)
        if self.steps == self.adt_injection_step and not self.adt_injected:
            print(f">>> STEP {self.steps}: ADT THERAPY INJECTED (Pre-emptive) <<<")
            self.adt_injected = True
            for _ in range(60): # Therapeutic dose
                self.grid.place_agent(ADTTCell(self), (random.randrange(self.grid.width), random.randrange(self.grid.height)))
            for _ in range(10):
                self.grid.place_agent(DendriticCell(self), (random.randrange(self.grid.width), random.randrange(self.grid.height)))

        # 2. IMMUNOSUPPRESSION (Step 21): Stop wild-type cytokine storm
        if self.steps == self.adt_injection_step + 1:
            print(f">>> STEP {self.steps}: IMMUNOSUPPRESSANTS ADMINISTERED (Silencing Wild-Type) <<<")
            std_cells = [a for a in self.agents if isinstance(a, StandardTCell)]
            for cell in std_cells:
                self.grid.remove_agent(cell)
                self.agents.remove(cell)

        self.agents.shuffle_do("step")
        
        inf_count = sum(1 for a in self.agents if isinstance(a, HostCell) and a.infected)
        self.history["infected"].append(inf_count)
        self.history["inflammation"].append(self.inflammation)
        self.history["atp"].append(self.atp_reserve)
        
        # Broadcast decay
        if self.steps % 4 == 0: self.active_broadcasts = []
        
        # System status checks
        if self.inflammation > 5000:
            print("!!! FATAL CYTOKINE STORM: MULTI-ORGAN FAILURE !!!")
            self.running = False
        if self.atp_reserve < 1000:
            print("!!! METABOLIC COLLAPSE !!!")
            self.running = False
        if inf_count == 0 and self.steps > 10:
            self.running = False

def run_clinical_sim():
    model = ClinicalModel(30, 30, adt_injection_step=20)
    print("Starting Clinical Simulation: SARS-CoV-2 Attack & EARLY ADT Rescue...")
    
    steps = 0
    while model.running and steps < 300:
        model.step()
        steps += 1
        if steps % 20 == 0:
            print(f"Step {steps}: Infected: {model.history['infected'][-1]}, Inflammation: {model.history['inflammation'][-1]:.0f}, ATP: {model.atp_reserve:.0f}")

    print(f"\n--- CLINICAL TRIAL RESULTS ---")
    print(f"Final Outcome: {'SURVIVED' if model.inflammation < 5000 and model.atp_reserve > 1000 else 'DECEASED'}")
    print(f"Total Inflammation: {model.inflammation:.2f}")
    print(f"Infection Cleared at Step: {steps}")
    print(f"ADT Kills: {model.adt_kills} vs Standard Kills: {model.std_kills}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    ax1.plot(model.history["infected"], color='red', label="Infected Population")
    ax1.axvline(x=60, color='green', linestyle='--', label="ADT Injection")
    ax1.set_title("Viral Load Management")
    ax1.legend()

    ax2.plot(model.history["inflammation"], color='orange', label="Cytokine Level (Inflammation)")
    ax2.axvline(x=60, color='green', linestyle='--', label="ADT Injection")
    ax2.set_title("Systemic Inflammatory Response")
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig("adt-simulator/clinical_rescue_test.png")
    print("\nClinical report saved as 'adt-simulator/clinical_rescue_test.png'")

if __name__ == "__main__":
    run_clinical_sim()
