import { Board } from './board';
import { Ship } from './ship';
import { Player } from './player';
import { DiplomacyStatus } from './types';

export class CombatEngine {
  private board: Board;

  constructor(board: Board) {
    this.board = board;
  }

  // проверка прямой видимости: между (x1,y1) и (x2,y2) не должно быть клеток с Солнцем
  private hasLineOfSight(x1: number, y1: number, x2: number, y2: number): boolean {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const steps = Math.max(Math.abs(dx), Math.abs(dy));
    if (steps === 0) return true;

    for (let i = 1; i < steps; i++) {
      const t = i / steps;
      const cx = Math.round(x1 + dx * t);
      const cy = Math.round(y1 + dy * t);
      if (this.board.isSun(cx, cy)) {
        return false; // Солнце блокирует луч
      }
    }
    return true;
  }

  resolveTurn(players: Player[], boardSize: number) {
    // 1. ПВО бьёт в конце хода противника — значит, в начале хода каждого игрока
    // мы обрабатываем ПВО всех его врагов, которые видят его корабли
    for (const attacker of players) {
      for (const defender of players) {
        if (attacker.id === defender.id) continue;
        const status = attacker.getDiplomacy(defender.id);
        if (status !== DiplomacyStatus.Enemy) continue;

        // найти все ПВО на планетах атакующего
        const aaGuns = attacker.planets
          .flatMap(p => p.buildings)
          .filter(b => b.name === 'AADGun');

        for (const gun of aaGuns) {
          // для каждого орудия ищем цель в радиусе 2
          const targets = defender.ships.filter(s => {
            const dist = Math.max(Math.abs(s.x - gun.x), Math.abs(s.y - gun.y)); // Чебышёв
            return dist <= 2;
          });

          if (targets.length === 0) continue;

          // выбираем первую цель (можно усложнить приоритетами)
          const target = targets[0];
          target.takeDamage(10);
        }
      }
    }

    // 2.
