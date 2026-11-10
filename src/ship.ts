import { ShipData, Resources } from './types';

export class Ship {
  public id: number;
  public typeName: string;
  public hp: number;
  public maxHp: number;
  public damage: number;
  public range: number;
  public x: number;
  public y: number;
  public ownerId: number;

  constructor(id: number, data: ShipData, x: number, y: number, ownerId: number) {
    this.id = id;
    this.typeName = data.name;
    this.hp = data.hp;
    this.maxHp = data.hp;
    this.damage = data.damage;
    this.range = data.range;
    this.x = x;
    this.y = y;
    this.ownerId = ownerId;
  }

  takeDamage(amount: number) {
    this.hp -= amount;
  }

  repair(silicon: number) {
    // 5 кремния = 5 HP
    const hpToRestore = Math.floor(silicon / 5) * 5;
    this.hp = Math.min(this.maxHp, this.hp + hpToRestore);
  }

  moveTo(x: number, y: number) {
    this.x = x;
    this.y = y;
  }
}
