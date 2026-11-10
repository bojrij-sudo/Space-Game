import { PlanetData, Resources, BuildingData, PlanetType } from './types';
import { Board } from './board';

export class Planet {
  public name: string;
  public type: PlanetType;
  public slots: number;
  public x: number;
  public y: number;
  public ownerId: number | null = null;
  
  private buildings: BuildingData[] = [];
  private colonizingShipId: number | null = null;

  constructor(data: PlanetData, x: number, y: number) {
    this.name = data.name;
    this.type = data.type;
    this.slots = data.slots;
    this.x = x;
    this.y = y;
  }

  get usedSlots(): number {
    return this.buildings.length + (this.colonizingShipId !== null ? 1 : 0);
  }

  get freeSlots(): number {
    return Math.max(0, this.slots - this.usedSlots);
  }

  canBuild(building: BuildingData): boolean {
    if (this.freeSlots === 0) return false;
    if (building.allowedOn && !building.allowedOn.includes(this.type)) return false;
    return true;
  }

  addBuilding(building: BuildingData) {
    if (!this.canBuild(building)) throw new Error('Cannot build here');
    this.buildings.push(building);
  }

  removeBuilding(index: number) {
    this.buildings.splice(index, 1);
  }

  setColonizingShip(shipId: number | null) {
    this.colonizingShipId = shipId;
  }

  calculateIncome(totalEnergyConsumption: number, totalEnergyProduction: number): Resources {
    const income: Resources = { iron: 0, copper: 0, silicon: 0, titanium: 0, energy: 0 };
    let productionEnergy = 0;

    for (const b of this.buildings) {
      if ('energyPerTurn' in b.effect) {
        productionEnergy += b.effect.energyPerTurn;
      }
      if ('ironPerTurn' in b.effect) income.iron += b.effect.ironPerTurn;
      if ('copperPerTurn' in b.effect) income.copper += b.effect.copperPerTurn;
      if ('siliconPerTurn' in b.effect) income.silicon += b.effect.siliconPerTurn;
      if ('titaniumPerTurn' in b.effect) income.titanium += b.effect.titaniumPerTurn;
    }

    income.energy = productionEnergy;

    // если потребление > производства, добыча падает вдвое
    if (totalEnergyConsumption > totalEnergyProduction) {
      income.iron = Math.floor(income.iron / 2);
      income.copper = Math.floor(income.copper / 2);
      income.silicon = Math.floor(income.silicon / 2);
      income.titanium = Math.floor(income.titanium / 2);
    }

    return income;
  }

  calculateEnergyStats(): { consumption: number; production: number } {
    let consumption = 0;
    let production = 0;
    for (const b of this.buildings) {
      consumption += b.energyConsumption;
      if ('energyPerTurn' in b.effect) production += b.effect.energyPerTurn;
    }
    return { consumption, production };
  }
}
