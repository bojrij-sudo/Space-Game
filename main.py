import argparse

import engine as E
from ai import Bot
from config import BUILDINGS, UNITS, MAX_TURNS

PLANET_CODE = {"mercury": "m", "venus": "v", "earth": "e", "mars": "r",
               "jupiter": "j", "saturn": "s", "uranus": "u", "neptune": "n"}


def render(state):
    grid = [["." for _ in range(state.size)] for _ in range(state.size)]
    sx, sy = state.sun_pos
    grid[sy][sx] = "S"
    for p in state.planets:
        ch = PLANET_CODE[p.id]
        grid[p.pos[1]][p.pos[0]] = ch.upper() if p.owner is not None else ch
    for u in state.units:
        grid[u.pos[1]][u.pos[0]] = str(u.owner)
    print("   " + " ".join(str(x % 10) for x in range(state.size)))
    for y in range(state.size):
        print(f"{y:2d} " + " ".join(grid[y]))
    for p in state.players:
        if not p.alive:
            continue
        r = p.resources
        planets = ", ".join(pl.name for pl in state.planets
                            if pl.owner == p.pid) or "нет"
        print(f"Цивилизация {p.pid} [{p.name}]: Ж {r['iron']} М {r['copper']} "
              f"К {r['silicon']} Т {r['titanium']} Э {r['energy']} | {planets}")


def find_planet(state, token):
    t = token.lower()
    return next((p for p in state.planets
                 if p.id == t or PLANET_CODE[p.id] == t), None)


def find_unit(state, uid, pid):
    return next((u for u in state.units if u.uid == uid and u.owner == pid),
                None)


def human_turn(state, pid):
    print("Команды: build <планета> <здание> | ship <планета> <юнит> | "
          "move <uid> <x> <y> | atk <uid> <x> <y> | repair <uid> | "
          "war <pid> | ally <pid> | trade <pid> <ресурс> <кол> <ресурс> <кол> | end")
    print("Планеты: " + ", ".join(f"{PLANET_CODE[p.id]}={p.name}"
                                  for p in state.planets))
    print(f"Здания: {', '.join(BUILDINGS)}")
    print(f"Юниты: {', '.join(UNITS)}")
    while True:
        try:
            parts = input("> ").strip().split()
        except EOFError:
            return
        if not parts:
            continue
        cmd, args = parts[0].lower(), parts[1:]
        try:
            if cmd == "end":
                return
            elif cmd == "build" and len(args) == 2:
                pl = find_planet(state, args[0])
                ok = pl is not None and E.build_building(state, pid, pl, args[1])
                print("Построено." if ok else "Нельзя построить.")
            elif cmd == "ship" and len(args) == 2:
                pl = find_planet(state, args[0])
                ok = pl is not None and E.build_unit(state, pid, pl, args[1])
                print("Корабль построен." if ok else "Нельзя построить корабль.")
            elif cmd == "move" and len(args) == 3:
                u = find_unit(state, int(args[0]), pid)
                dest = (int(args[1]), int(args[2]))
                ok = u is not None and E.move_unit(state, u, dest)
                print(f"Корабль {u.uid} на {dest}." if ok else "Нельзя так.")
            elif cmd == "atk" and len(args) == 3:
                u = find_unit(state, int(args[0]), pid)
                t = E.unit_at(state, (int(args[1]), int(args[2])))
                ok = u is not None and t is not None and E.attack(state, u, t)
                print("Атака выполнена." if ok else "Нельзя атаковать.")
            elif cmd == "repair" and len(args) == 1:
                u = find_unit(state, int(args[0]), pid)
                pl = E.planet_at(state, u.pos) if u else None
                ok = u is not None and pl is not None and E.repair(state, u, pl)
                print("Отремонтирован." if ok else "Ремонт невозможен.")
            elif cmd in ("war", "ally") and len(args) == 1:
                other = int(args[0])
                (E.declare_war if cmd == "war" else E.make_alliance)(state, pid, other)
                print("Дипломатия обновлена.")
            elif cmd == "trade" and len(args) == 5:
                give = {args[1]: int(args[2])}
                get = {args[3]: int(args[4])}
                ok = E.trade(state, pid, int(args[0]), give, get)
                print("Сделка заключена." if ok
                      else "Сделка не удалась (лимит 1 за ход с цивилизацией).")
            else:
                print("Не понял команду.")
        except (ValueError, KeyError):
            print("Ошибка в аргументах.")


def run_game(names, max_turns=MAX_TURNS):
    state = E.new_game(names)
    bots = {p.pid: Bot(p.pid) for p in state.players if p.is_bot}
    for state.turn in range(1, max_turns + 1):
        print(f"\n===== ХОД {state.turn} =====")
        for player in state.players:
            if not player.alive:
                continue
            state.current = player.pid
            E.start_turn(state, player.pid)
            if player.is_bot:
                bots[player.pid].take_turn(state)
            else:
                render(state)
                human_turn(state, player.pid)
            E.apply_sun_damage(state, player.pid)
            E.defense_fire(state, player.pid)
            E.check_elimination(state)
            winner = E.check_victory(state)
            if winner is not None:
                render(state)
                print(f"\nПобеда! Цивилизация {state.players[winner].name}.")
                return
    alive = [p for p in state.players if p.alive]
    if alive:
        best = max(alive, key=lambda p: E.score(state, p.pid))
        print(f"\nЛимит ходов истёк. Победа по очкам: {best.name} "
              f"({E.score(state, best.pid):.0f} очков)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Космическая стратегия")
    ap.add_argument("--bots", type=int, default=1,
                    help="число ботов (человек — цивилизация 0)")
    ap.add_argument("--botgame", type=int, default=0,
                    help="бой N ботов, наблюдаем со стороны")
    ap.add_argument("--turns", type=int, default=MAX_TURNS)
    args = ap.parse_args()
    if args.botgame:
        run_game([f"Бот-{i}" for i in range(args.botgame)], args.turns)
    else:
        run_game(["Игрок"] + [f"Бот-{i}" for i in range(args.bots)], args.turns)
