import { Resources, DiplomacyStatus } from './types';
import { Planet } from './planet';
import { Ship } from './ship';

export class Player {
  public id: number;
  public resources: Resources;
  public planets: Planet[] = [];
  public ships: Ship[] = [];
  public diplomacy: Map<number, DiplomacyStatus> = new Map();

  constructor(id: number, startResources: Resources) {
    this.id = id;
    this.resources = { ...startResources };
  }

  addPlanet(planet: Planet) {
    planet.ownerId = this.id;
    this.planets.push(planet);
  }

  removePlanet(planetIndex: number) {
    this.planets.splice(planetIndex, 1);
  }

  addShip(ship: Ship) {
    this.ships.push(ship);
  }

  removeShip(shipIndex: number) {
    this.ships.splice(shipIndex, 1);
  }

  spendResources(cost: Partial<Resources>): boolean {
    // проверяем, хватает ли ресурсов
    for (const key in cost) {
      const amount = cost[key as keyof Resources] ?? 0;
      if ((this.resources[key as keyof Resources] ?? 0) < amount) {
        return false;
      }
    }
    // списываем
    for (const key in cost) {
      this.resources[key as keyof Resources] -= cost[key as keyof Resources] ?? 0;
    }
    return true;
  }

  gainResources(gain: Partial<Resources>) {
    for (const key in gain) {
      this.resources[key as keyof Resources] += gain[key
