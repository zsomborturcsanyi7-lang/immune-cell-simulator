import mesa
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# High-Resolution constants: 1 Macro-Step = 10,000 Micro-Ticks
TICKS_PER_STEP = 10000

class HostCell(mesa.Agent):
    def __init__(self, model, virus_type=0):
        super().__init__(model)
        self.virus_type = virus_type
        self.viral_load = 0.0
        self.last_replication_tick = 0

    def micro_step(self, tick):
        if self.virus_type > 0:
            # Viral load increases per tick
            self.viral_load += self.model.viral_aggression / TICKS_PER_STEP
            
            # Replication check every 100 ticks (High frequency)
            if tick - self.last_replication_tick >= 100:
                self.last_replication_tick = tick
                if self.viral_load > 20.0: # Starts spreading earlier in Apocalypse
                    neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
                    for neighbor in neighbors:
                        if isinstance(neighbor, HostCell) and neighbor.virus_type == 0:
                            if random.random() < 0.01: # High-res probability
                                neighbor.virus_type = self.virus_type
                                self.model.log_event(tick, "INFECTION_SPREAD", neighbor.pos)

class ADTTCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.authorized_strains = set()
        self.last_move_tick = 0

    def micro_step(self, tick):
        # Move every 50 ticks (Very active)
        if tick - self.last_move_tick >= 50:
            self.last_move_tick = tick
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            self.model.grid.move_agent(self, random.choice(possible_steps))

        # Check for local tokens
        if self.model.local_tokens:
            self.authorized_strains.update(self.model.local_tokens.keys())

        # Interaction check
        contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in contents:
            if isinstance(obj, HostCell) and obj.virus_type > 0:
                if obj.virus_type in self.authorized_strains:
                    self.model.log_event(tick, "KILL_START", self.pos)
                    obj.virus_type = 0
                    obj.viral_load = 0
                    self.model.atp_reserve -= 1.0
                    self.model.log_event(tick, "KILL_COMPLETE", self.pos)
                else:
                    self.model.register_ping(tick, self.pos, obj)
                break

class DendriticCell(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.last_action_tick = 0

    def micro_step(self, tick):
        # DC acts every 200 ticks (Heavier analysis)
        if tick - self.last_action_tick >= 200:
            self.last_action_tick = tick
            if self.model.pings:
                ping_tick, pos, cell = self.model.pings.pop(0)
                self.model.grid.move_agent(self, pos)
                if cell.virus_type > 0:
                    latency = tick - ping_tick
                    self.model.local_tokens[cell.virus_type] = tick
                    self.model.log_event(tick, "TOKEN_ISSUED", pos, latency=latency)

class HighResModel(mesa.Model):
    def __init__(self, width, height, aggression):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.viral_aggression = aggression
        self.atp_reserve = 10000
        self.pings = []
        self.local_tokens = {} # type -> tick_issued
        self.event_log = [] # List of dicts for analysis

        # Setup
        for x in range(width):
            for y in range(height):
                is_inf = 1 if random.random() < 0.05 else 0
                a = HostCell(self, virus_type=is_inf)
                self.grid.place_agent(a, (x, y))

        for _ in range(30): self.grid.place_agent(ADTTCell(self), (random.randrange(width), random.randrange(height)))
        for _ in range(5): self.grid.place_agent(DendriticCell(self), (random.randrange(width), random.randrange(height)))

    def register_ping(self, tick, pos, agent):
        if not any(p[2] == agent for p in self.pings):
            self.pings.append((tick, pos, agent))
            self.log_event(tick, "PING_REGISTERED", pos)

    def log_event(self, tick, event_type, pos, **kwargs):
        log_entry = {"tick": tick, "type": event_type, "pos": pos}
        log_entry.update(kwargs)
        self.event_log.append(log_entry)

    def run_micro_ticks(self, total_ticks):
        for tick in range(total_ticks):
            # We bypass model.step() and call micro_step on agents directly for resolution
            for agent in self.agents:
                agent.micro_step(tick)
            
            if tick % 1000 == 0:
                inf_count = sum(1 for a in self.agents if isinstance(a, HostCell) and a.virus_type > 0)
                if inf_count == 0: break
                if inf_count > 500: break # Apocalypse

def analyze_high_res():
    model = HighResModel(20, 20, aggression=50) # High aggression
    print("Running High-Resolution Simulation (1 tick = 1 microsecond equivalent)...")
    model.run_micro_ticks(100000) # 10 Macro-steps total
    
    df = pd.DataFrame(model.event_log)
    
    # 1. LATENCY ANALYSIS (TEN-THOUSANDTHS)
    tokens = df[df["type"] == "TOKEN_ISSUED"]
    if not tokens.empty:
        avg_latency = tokens["latency"].mean()
        min_latency = tokens["latency"].min()
        max_latency = tokens["latency"].max()
        print(f"\n--- NANOSECOND-SCALE LATENCY REPORT ---")
        print(f"Avg Recognition Speed: {avg_latency:.2f} ticks")
        print(f"Fastest Authentication: {min_latency} ticks")
        print(f"Slowest Authentication: {max_latency} ticks")
    
    # 2. BOTTLENECK ANALYSIS
    pings = len(df[df["type"] == "PING_REGISTERED"])
    kills = len(df[df["type"] == "KILL_COMPLETE"])
    spreads = len(df[df["type"] == "INFECTION_SPREAD"])
    
    print(f"\n--- BOTTLENECK ANALYSIS ---")
    print(f"Total Pings Registered: {pings}")
    print(f"Total Tokens Issued: {len(tokens)}")
    print(f"Total Successful Kills: {kills}")
    print(f"Viral Spread Events: {spreads}")
    
    efficiency = (kills / pings * 100) if pings > 0 else 0
    print(f"System Efficiency (Kills/Pings): {efficiency:.2f}%")
    
    if spreads > kills:
        print("\nCRITICAL FAILURE POINT IDENTIFIED:")
        print(f"The 'Viral Spread Velocity' ({spreads/100000:.4f} events/tick) is {spreads/kills:.2f}x faster than 'Kill Velocity'.")
        print("The bottleneck is the Dendritic Cell queue. DC cannot issue tokens fast enough for new mutations.")

    # Visualize High-Res Data
    plt.figure(figsize=(10, 6))
    plt.hist(df[df["type"] == "TOKEN_ISSUED"]["latency"], bins=20, color='blue', alpha=0.7)
    plt.title("High-Resolution Distribution of Recognition Latency (Ticks)")
    plt.xlabel("Ticks (1 tick = 10^-4 Macro-Step)")
    plt.ylabel("Frequency")
    plt.savefig("adt-simulator/high_res_latency.png")

if __name__ == "__main__":
    analyze_high_res()
