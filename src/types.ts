export type Resource = 'iron' | 'copper' | 'silicon' | 'titanium' | 'energy';

export interface Resources {
  iron: number;
  copper: number;
  silicon: number;
  titanium: number;
  energy: number;
}

export type PlanetType = 'rocky' | 'gas_giant' | 'ice';

export interface PlanetData {
  name: string;
  type: PlanetType;
  slots: number;
}

export interface BuildingData {
  name: string;
  cost: Partial<Resources>;
  energyConsumption: number;
  effect: any;
  allowedOn?: PlanetType[];
}

export interface ShipData {
  name: string;
  cost: Partial<Resources>;
  hp: number;
  damage: number;
  range: number;
}

export interface ConstantsData {
  boardSize: number;
  sunPosition: { x: number; y: number };
  sunBurnDamage: number;
  turnsToVictory: number;
  resourceValueMultiplier: number;
  betrayalEnergyPenalty: number;
}

export enum DiplomacyStatus {
  Neutral = 'neutral',
  Ally = 'ally',
  Enemy = 'enemy'
}
