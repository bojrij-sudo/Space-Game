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
    for (const key in cost) {
      const amount = cost
