import random

from config import (BUILDINGS, UNITS, PLANETS, START_RESOURCES, BOARD_SIZE,
                    SUN_POS, SUN_DAMAGE, ICE_MALUS, BETRAYAL_PENALTY,
                    RESOURCE_VALUE, SLOT_SCORE, REPAIR)
from models import GameState, Player, Planet, Building, Unit

DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
KNIGHT = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
STRAIGHT = [(-1, 0), (1, 0), (0, -1), (0, 1)]
RESOURCES = ("iron", "copper", "silicon", "titanium", "energy")


# ---------- вспомогательные ----------

def in_board(state, pos):
    x, y = pos
    return 0 <= x < state.size and 0 <= y < state.size


def is_sun(state, pos):
    return pos == state.sun_pos


def planet_at(state, pos):
    return next((p for p in state.planets if p.pos == pos), None)


def unit_at(state, pos):
    return next((u for u in state.units if u.pos == pos), None)


def relation(state, a, b):
    if a == b:
        return "self"
    return state.diplomacy.get((min(a, b), max(a, b)), "neutral")


def set_relation(state, a, b, rel):
    state.diplomacy[(min(a, b), max(a, b))] = rel


def enemies_of(state, pid):
    return [p.pid for p in state.players
            if p.alive and relation(state, pid, p.pid) == "war"]


def can_afford(player, cost):
    return all(player.resources.get(r, 0) >= v for r, v in cost.items())


def pay(player, cost):
    for r, v in cost.items():
        player.resources[r] -= v


# ---------- создание игры ----------

def new_game(names):
    players = [Player(i, names[i], i != 0, dict(START_RESOURCES))
               for i in range(len(names))]
    planets = [Planet(d["id"], d["name"], d["kind"], d["slots"], d["pos"])
               for d in PLANETS]
    state = GameState(size=BOARD_SIZE, sun_pos=SUN_POS,
                      planets=planets, units=[], players=players)
    homes = planets[:]
    random.shuffle(homes)
    for player, planet in zip(players, homes):
        planet.owner = player.pid
        planet.buildings = [Building("spaceport", BUILDINGS["spaceport"]["hp"]),
                            Building("generator", BUILDINGS["generator"]["hp"]),
                            Building("iron_mine", BUILDINGS["iron_mine"]["hp"])]
    return state


# ---------- экономика ----------

def planet_income(state, planet):
    inc = {r: 0 for r in RESOURCES}
    use = 0
    for b in planet.buildings:
        cfg = BUILDINGS[b.type]
        for res, amount in cfg["income"].items():
            inc[res] += amount
        use += cfg["energy_use"]
    if use > inc["energy"]:
        for res in RESOURCES:
            if res != "energy":
                inc[res] = int(inc[res] * 0.5)
    if planet.kind == "ice":
        for res in ("iron", "copper", "silicon", "titanium"):
            inc[res] = int(inc[res] * (1 - ICE_MALUS))
    return inc


def start_turn(state, pid):
    player = state.players[pid]
    total = {r: 0 for r in RESOURCES}
    for planet in state.planets:
        if planet.owner == pid:
            planet.built = False
            for r, v in planet_income(state, planet).items():
                total[r] += v
    for r, v in total.items():
        player.resources[r] += v
    state.trades_this_turn[pid] = set()
    # колония «дозрела»
    for u in [u for u in state.units if u.owner == pid and u.colonizing]:
        pl = planet_at(state, u.pos)
        if pl is not None and pl.id == u.colonizing and pl.owner != pid \
                and pl.free_slots() > 0:
            pl.owner = pid
            print(f"  [{player.name}] планета {pl.name} колонизирована!")
        u.colonizing = ""


# ---------- стройка ----------

def build_building(state, pid, planet, btype):
    cfg = BUILDINGS[btype]
    if planet.owner != pid or planet.free_slots() <= 0:
        return False
    if planet.kind not in cfg["allowed"]:
        return False
    player = state.players[pid]
    if not can_afford(player, cfg["cost"]):
        return False
    pay(player, cfg["cost"])
    planet.buildings.append(Building(btype, cfg["hp"]))
    return True


def build_unit(state, pid, planet, utype):
    cfg = UNITS[utype]
    if planet.built or planet.owner != pid or planet.kind == "gas":
        return False
    if not any(b.type == "spaceport" for b in planet.buildings):
        return False
    if unit_at(state, planet.pos) is not None:
        return False
    player = state.players[pid]
    if not can_afford(player, cfg["cost"]):
        return False
    pay(player, cfg["cost"])
    state.units.append(Unit(state.next_uid, utype, pid, planet.pos,
                            cfg["hp"], cfg["hp"]))
    state.next_uid += 1
    planet.built = True
    return True


# ---------- движение ----------

def legal_moves(state, unit):
    cfg = UNITS[unit.type]
    if cfg["move"] == "king":
        cands = [(unit.pos[0] + dx, unit.pos[1] + dy) for dx, dy in DIRS8]
    elif cfg["move"] == "knight":
        cands = [(unit.pos[0] + dx, unit.pos[1] + dy) for dx, dy in KNIGHT]
    else:  # queen — до move_len клеток по прямой
        cands = []
        for dx, dy in DIRS8:
            for step in range(1, cfg["move_len"] + 1):
                cands.append((unit.pos[0] + dx * step, unit.pos[1] + dy * step))
    dests = []
    for p in cands:
        if not in_board(state, p) or is_sun(state, p):
            continue
        if unit_at(state, p) is not None:
            continue
        pl = planet_at(state, p)
        if pl is not None and pl.owner is not None \
                and relation(state, unit.owner, pl.owner) == "ally":
            continue
        dests.append(p)
    return dests


def move_unit(state, unit, dest):
    if dest not in legal_moves(state, unit):
        return False
    unit.pos = dest
    unit.colonizing = ""
    pl = planet_at(state, dest)
    if pl is not None and pl.owner != unit.owner:
        if pl.owner is None or relation(state, unit.owner, pl.owner) == "war":
            if pl.free_slots() > 0:
                unit.colonizing = pl.id
    return True


# ---------- бой ----------

def attack_targets(state, unit):
    cfg = UNITS[unit.type]
    rng = cfg["range"]
    enemies = set(enemies_of(state, unit.owner))
    targets = []
    if not enemies:
        return targets

    def grab(p):
        t = unit_at(state, p)
        if t is not None and t.owner in enemies:
            targets.append(t)

    if rng == 1:
        for dx, dy in DIRS8:
            p = (unit.pos[0] + dx, unit.pos[1] + dy)
            if in_board(state, p) and not is_sun(state, p):
                grab(p)
    else:
        for dx, dy in STRAIGHT:
            for step in range(1, rng + 1):
                p = (unit.pos[0] + dx * step, unit.pos[1] + dy * step)
                if not in_board(state, p) or is_sun(state, p):
                    break
                grab(p)
    return targets


def attack(state, unit, target):
    if target not in attack_targets(state, unit):
        return False
    target.hp -= UNITS[unit.type]["damage"]
    if target.hp <= 0:
        state.units.remove(target)
    return True


def apply_sun_damage(state, pid):
    sx, sy = state.sun_pos
    for u in [u for u in state.units if u.owner == pid]:
        if max(abs(u.pos[0] - sx), abs(u.pos[1] - sy)) == 1:
            u.hp -= SUN_DAMAGE
            if u.hp <= 0:
                state.units.remove(u)


def defense_fire(state, mover_pid):
    """ПВО всех враждебных планет стреляет в конце хода mover_pid."""
    rng = BUILDINGS["defense"]["range"]
    dmg = BUILDINGS["defense"]["damage"]
    for planet in state.planets:
        if planet.owner is None or planet.owner == mover_pid:
            continue
        if relation(state, planet.owner, mover_pid) != "war":
            continue
        for b in [b for b in planet.buildings if b.type == "defense"]:
            px, py = planet.pos
            targets = [u for u in state.units if u.owner == mover_pid
                       and max(abs(u.pos[0] - px), abs(u.pos[1] - py)) <= rng]
            if targets:
                t = min(targets, key=lambda u: (abs(u.pos[0] - px)
                                                + abs(u.pos[1] - py), u.uid))
                t.hp -= dmg
                if t.hp <= 0:
                    state.units.remove(t)


def repair(state, unit, planet):
    player = state.players[unit.owner]
    if planet.owner != unit.owner or unit.hp >= unit.max_hp:
        return False
    if player.resources["silicon"] < REPAIR["silicon_cost"]:
        return False
    player.resources["silicon"] -= REPAIR["silicon_cost"]
    unit.hp = min(unit.max_hp, unit.hp + REPAIR["hp_healed"])
    return True


# ---------- дипломатия ----------

def declare_war(state, a, b):
    if relation(state, a, b) == "ally":
        planets = sum(1 for p in state.planets if p.owner == a)
        res = state.players[a].resources
        res["energy"] = max(0, res["energy"] - BETRAYAL_PENALTY * planets)
    set_relation(state, a, b, "war")


def make_alliance(state, a, b):
    set_relation(state, a, b, "ally")


def trade(state, a, b, give, get):
    """give — что отдаёт a, get — что получает a (оба словари ресурс->кол-во)."""
    if relation(state, a, b) not in ("ally", "neutral"):
        return False
    if b in state.trades_this_turn.get(a, set()) \
            or a in state.trades_this_turn.get(b, set()):
        return False
    pa, pb = state.players[a], state.players[b]
    if not can_afford(pa, give) or not can_afford(pb, get):
        return False
    pay(pa, give)
    pay(pb, get)
    for r, v in give.items():
        pb.resources[r] += v
    for r, v in get.items():
        pa.resources[r] += v
    state.trades_this_turn.setdefault(a, set()).add(b)
    state.trades_this_turn.setdefault(b, set()).add(a)
    return True


# ---------- итоги ----------

def check_elimination(state):
    for pl in state.players:
        if pl.alive and not any(p.owner == pl.pid for p in state.planets):
            pl.alive = False
            state.units = [u for u in state.units if u.owner != pl.pid]
            print(f"  Цивилизация {pl.name} выбыла из игры!")


def score(state, pid):
    player = state.players[pid]
    s = sum(player.resources[r] * RESOURCE_VALUE[r] for r in RESOURCES)
    for pl in state.planets:
        if pl.owner == pid:
            s += SLOT_SCORE
            s += sum(sum(BUILDINGS[b.type]["cost"].values())
                     for b in pl.buildings)
    s += sum(sum(UNITS[u.type]["cost"].values())
             for u in state.units if u.owner == pid)
    return s


def check_victory(state):
    alive = [p for p in state.players if p.alive]
    if len(alive) <= 1:
        return alive[0].pid if alive else None
    return None
