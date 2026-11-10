import { Game } from './game';
import { ConstantsData } from './types';
import * as constantsJson from '../data/constants.json';

const constants = constantsJson as ConstantsData;

// стартовые ресурсы для 2 игроков
const startResources = {
  0: { iron: 20, copper: 10, silicon: 10, titanium: 5, energy: 20 },
  1: { iron: 20, copper: 10, silicon: 10, titanium: 5, energy: 20 }
};

const game = new Game(constants, startResources);

// расставляем планеты (пример: Меркурий и Венера рядом с Солнцем, но не на нём)
const planetData = [
  { name: 'Mercury', type: 'rocky', slots: 4 },
  { name: 'Venus', type: 'rocky', slots: 9 }
];
const positions = [
  { x: 48, y: 50 }, // рядом с Солнцем (50,50) — будет получать урон
  { x: 52, y: 50 }
];

game.setupPlanets(planetData, positions);

// Пример симуляции 3 ходов
for (let i = 0; i < 3; i++) {
  const winner = game.nextTurn();
  if (winner) {
    console.log(`Победа игрока ${winner.id}!`);
    break;
  }
}
