"""Константы баланса игры. Все числа правьте здесь — логику не трогаем."""

BOARD_SIZE = 13
SUN_POS = (6, 6)          # Солнце в центре, непроходимо
SUN_DAMAGE = 10           # урон кораблю, стоящему вплотную к Солнцу
MAX_TURNS = 30            # лимит ходов (победа по очкам)
SLOT_SCORE = 30           # очки за владение планетой
ICE_MALUS = 0.25          # -25% добычи на ледяных планетах
BETRAYAL_PENALTY = 10     # энергии с каждой планеты за войну с бывшим союзником

PLANETS = [
    {"id": "mercury", "name": "Меркурий", "kind": "rock", "slots": 4,  "pos": (3, 3)},
    {"id": "venus",   "name": "Венера",   "kind": "rock", "slots": 9,  "pos": (3, 6)},
    {"id": "earth",   "name": "Земля",    "kind": "rock", "slots": 9,  "pos": (3, 9)},
    {"id": "mars",    "name": "Марс",     "kind": "rock", "slots": 4,  "pos": (9, 3)},
    {"id": "jupiter", "name": "Юпитер",   "kind": "gas",  "slots": 16, "pos": (6, 3)},
    {"id": "saturn",  "name": "Сатурн",   "kind": "gas",  "slots": 16, "pos": (6, 9)},
    {"id": "uranus",  "name": "Уран",     "kind": "ice",  "slots": 9,  "pos": (9, 6)},
    {"id": "neptune", "name": "Нептун",   "kind": "ice",  "slots": 9,  "pos": (9, 9)},
]

START_RESOURCES = {"iron": 20, "copper": 10, "silicon": 10, "titanium": 5, "energy": 20}

BUILDINGS = {
    "iron_mine":        {"name": "Железная шахта",     "cost": {"iron": 10, "copper": 5},                 "energy_use": 1, "income": {"iron": 3},     "allowed": ["rock", "ice"], "hp": 20},
    "copper_mine":      {"name": "Медная шахта",       "cost": {"iron": 10, "copper": 5},                 "energy_use": 1, "income": {"copper": 3},   "allowed": ["rock", "ice"], "hp": 20},
    "silicon_mine":     {"name": "Кремниевая шахта",   "cost": {"iron": 15, "copper": 10},                "energy_use": 1, "income": {"silicon": 2},  "allowed": ["rock", "ice"], "hp": 20},
    "titanium_mine":    {"name": "Титановая шахта",    "cost": {"iron": 15, "copper": 10, "silicon": 5},  "energy_use": 2, "income": {"titanium": 2}, "allowed": ["rock", "ice"], "hp": 20},
    "generator":        {"name": "Генератор",          "cost": {"iron": 10, "copper": 5, "silicon": 5},   "energy_use": 0, "income": {"energy": 5},   "allowed": ["rock", "ice"], "hp": 20},
    "hydrogen_station": {"name": "Водородная станция", "cost": {"iron": 15, "titanium": 10},              "energy_use": 0, "income": {"energy": 8},   "allowed": ["gas"],         "hp": 20},
    "spaceport":        {"name": "Космопорт",          "cost": {"iron": 20, "copper": 10, "silicon": 10}, "energy_use": 2, "income": {},              "allowed": ["rock", "ice"], "hp": 20},
    "defense":          {"name": "ПВО",                "cost": {"iron": 15, "copper": 10, "silicon": 10}, "energy_use": 1, "income": {},              "allowed": ["rock", "ice"], "hp": 25,
                         "damage": 10, "range": 2},
}

UNITS = {
    "fighter": {"name": "Истребитель", "cost": {"iron": 5,  "copper": 3,  "silicon": 2},                "hp": 10, "damage": 4,  "range": 1, "move": "king",   "move_len": 1},
    "raider":  {"name": "Рейдер",      "cost": {"iron": 8,  "copper": 5,  "silicon": 4},                "hp": 14, "damage": 5,  "range": 5, "move": "knight", "move_len": 1},
    "cruiser": {"name": "Крейсер",     "cost": {"iron": 20, "copper": 12, "silicon": 8, "titanium": 5}, "hp": 30, "damage": 12, "range": 3, "move": "queen",  "move_len": 2},
}

REPAIR = {"silicon_cost": 5, "hp_healed": 5}

RESOURCE_VALUE = {"iron": 1.0, "copper": 1.0, "silicon": 1.5, "titanium": 2.0, "energy": 0.5}
