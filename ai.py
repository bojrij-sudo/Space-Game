import random

import engine as E


class Bot:
    def __init__(self, pid):
        self.pid = pid

    def my_planets(self, state):
        return [p for p in state.planets if p.owner == self.pid]

    def take_turn(self, state):
        self.economy(state)
        self.build_fleet(state)
        self.military(state)

    def economy(self, state):
        for pl in self.my_planets(state):
            if pl.kind == "gas":
                E.build_building(state, self.pid, pl, "hydrogen_station")
                continue
            types = [b.type for b in pl.buildings]
            for btype in ("iron_mine", "copper_mine", "generator",
                          "silicon_mine", "defense", "titanium_mine"):
                if btype not in types:
                    E.build_building(state, self.pid, pl, btype)
                    break

    def build_fleet(self, state):
        for pl in self.my_planets(state):
            if not any(b.type == "spaceport" for b in pl.buildings):
                continue
            for ut in ("cruiser", "raider", "fighter"):
                if E.build_unit(state, self.pid, pl, ut):
                    break

    def military(self, state):
        enemies = E.enemies_of(state, self.pid)
        if state.turn >= 3 and not enemies:
            neutrals = [p.pid for p in state.players
                        if p.alive and p.pid != self.pid
                        and E.relation(state, self.pid, p.pid) == "neutral"]
            if neutrals and state.units:
                E.declare_war(state, self.pid, random.choice(neutrals))
        for u in [u for u in state.units if u.owner == self.pid]:
            pl = E.planet_at(state, u.pos)
            if pl is not None and pl.owner == self.pid \
                    and u.hp < u.max_hp * 0.5:
                E.repair(state, u, pl)
                continue
            targets = E.attack_targets(state, u)
            if targets:
                E.attack(state, u, min(targets, key=lambda t: t.hp))
                continue
            moves = E.legal_moves(state, u)
            goal = self.choose_goal(state, u, moves)
            if goal is not None:
                E.move_unit(state, u, goal)

    def choose_goal(self, state, u, moves):
        if not moves:
            return None
        free = [p for p in state.planets
                if p.owner is None and p.free_slots() > 0]
        if free:
            target = min(free, key=lambda p: self._dist(p.pos, u.pos))
        else:
            enemy_planets = [p for p in state.planets
                             if p.owner in E.enemies_of(state, self.pid)]
            if not enemy_planets:
                return None
            target = min(enemy_planets,
                         key=lambda p: self._dist(p.pos, u.pos))
        if u.pos == target.pos:
            return None
        return min(moves, key=lambda m: self._dist(m, target.pos))

    @staticmethod
    def _dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
