import { ConstantsData } from './types';

export class Board {
  public readonly size: number;
  private readonly sunPos: { x: number; y: number };
  private readonly burnDamage: number;

  constructor(constants: ConstantsData) {
    this.size = constants.boardSize;
    this.sunPos = constants.sunPosition;
    this.burnDamage = constants.sunBurnDamage;
  }

  isValid(x: number, y: number): boolean {
    return x >= 0 && x < this.size && y >= 0 && y < this.size;
  }

  isSun(x: number, y: number): boolean {
    return x === this.sunPos.x && y === this.sunPos.y;
  }

  getBurnDamage(x: number, y: number): number {
    if (!this.isValid(x, y)) return 0;
    const dx = Math.abs(x - this.sunPos.x);
    const dy = Math.abs(y - this.sunPos.y);
    // урон в соседних клетках (включая диагональные)
    return (dx <= 1 && dy <= 1) ? this.burnDamage : 0;
  }

  distance(x1: number, y1: number, x2: number, y2: number): number {
    return Math.max(Math.abs(x1 - x2), Math.abs(y1 - y2)); // Чебышёв
  }

  cellsInRange(x: number, y: number, range: number): [number, number][] {
    const cells: [number, number][] = [];
    for (let dx = -range; dx <= range; dx++) {
      for (let dy = -range; dy <= range; dy++) {
        const nx = x + dx;
        const ny = y + dy;
        if (this.isValid(nx, ny) && this.distance(x, y, nx, ny) <= range) {
          cells.push([nx, ny]);
        }
      }
    }
    return cells;
  }
}
