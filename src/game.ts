import { Board } from './board';
import { Planet } from './planet';
import { Ship } from './ship';
import { Player } from './player';
import { CombatEngine } from './combat';
import { ConstantsData } from './types';

export class Game {
  public board: Board;
  public players: Player[];
  public turn: number = 0;
  public maxTurns: number;
  public combat: CombatEngine;
  private nextShipId: number = 1;

  constructor(constants: ConstantsData, startResources: { [key: number]: any }) {
    this.board = new Board(constants);
    this.maxTurns = constants.turnsToVictory;
    this.combat = new CombatEngine(this.board);
    this.players = Object.keys(startResources).map(idStr => {
      const id = Number(idStr);
      return new Player(id, startResources[id]);
    });
  }

  setupPlanets(planetDataList: any[], positions: { x: number; y: number }[]) {
    planetDataList.forEach((data, i) => {
      const planet = new Planet(data, positions[i].x, positions[i].y);
      // раздаём стартовые планеты игрокам (например, по кругу)
      const ownerId = this.players[i % this.players.length].id;
      this.players.find(p => p.id === ownerId)!.addPlanet(planet);
      // здесь можно сразу поставить стартовые здания: космопорт, генератор, железную шахту
      // но для простоты пока без этого
    });
  }

  startTurn() {
    this.turn++;
    console.log(`=== Ход ${this.turn} ===`);
  }

  phaseIncome() {
    this.players.forEach(player => {
      let totalEnergyConsumption = 0;
      let totalEnergyProduction = 0;

      player.planets.forEach(planet => {
        const stats = planet.calculateEnergyStats();
        totalEnergyConsumption += stats.consumption;
        totalEnergyProduction += stats.production;
      });

      // считаем доход по всем планетам
      player.planets.forEach(planet => {
        const income = planet.calculateIncome(totalEnergyConsumption, totalEnergyProduction);
        player.gainResources(income);
      });
    });
  }

  phaseBuild(player: Player, buildingName: string, planetIndex: number, shipType?: string) {
    // упрощённо: только один тип действия за вызов. В реальном коде лучше через очередь действий
    const planet = player.planets[planetIndex];
    if (!planet) return;

    const buildingsData = require('../data/buildings.json') as any[];
    const shipsData = require('../data/ships.json') as any[];

    if (shipType) {
      const shipData = shipsData.find(s => s.name === shipType);
      if (!shipData) return;
      // проверяем космопорт и лимит стройки (1 корабль/ход на космопорт)
      const spaceports = planet.buildings.filter(b => b.name === 'Spaceport').length;
      if (spaceports === 0) return; // нельзя строить корабли без космопорта
      // тут можно добавить проверку лимита стройки за ход
      if (player.spendResources(shipData.cost)) {
        const ship = new Ship(this.nextShipId++, shipData, planet.x, planet.y, player.id);
        player.addShip(ship);
      }
      return;
    }

    const buildingData = buildingsData.find(b => b.name === buildingName);
    if (!buildingData) return;
    if (player.spendResources(buildingData.cost) && planet.canBuild(buildingData)) {
      planet.addBuilding(buildingData);
    }
  }

  phaseMove(player: Player, shipIndex: number, newX: number, newY: number) {
    const ship = player.ships[shipIndex];
    if (!ship) return;
    if (!this.board.isValid(newX, newY)) return;
    if (this.board.isSun(newX, newY)) return; // нельзя на Солнце
    // лимит: не больше 1 корабля на клетку
    const occupying = this.players.flatMap(p => p.ships).find(s => s.x === newX && s.y === newY);
    if (occupying && occupying.id !== ship.id) return;

    ship.moveTo(newX, newY);
  }

  phaseCombat() {
    this.combat.resolveTurn(this.players, this.board.size);
  }

  phaseColonizationAndDefeat() {
    // колонизация: если корабль стоит на пустой планете — она становится вашей
    // захват: если корабль пережил ход врага на чужой планете — вы её захватываете
    this.players.forEach(player => {
      player.ships.forEach(ship => {
        const planet = this.players
          .flatMap(p => p.planets)
          .find(p => p.x === ship.x && p.y === ship.y);

        if (!planet) return; // корабль не на планете

        if (planet.ownerId === null) {
          // пустая планета → колонизируем
          planet.ownerId = player.id;
          player.addPlanet(planet);
        } else if (planet.ownerId !== player.id) {
          // чужая планета → проверяем, жив ли корабль после боя
          // если жив — захватываем
          const enemy = this.players.find(p => p.id === planet.ownerId);
          if (!enemy) return;
          // корабль должен пережить ход врага — это уже учтено в phaseCombat
          planet.ownerId = player.id;
          enemy.removePlanet(enemy.planets.findIndex(p => p === planet));
          player.addPlanet(planet);
        }
      });
    });

    // выбывание: если у цивилизации не осталось планет — она выбывает
    this.players.filter(p => !p.isAlive()).forEach(p => {
      console.log(`Игрок ${p.id} выбыл!`);
      p.ships = []; // уничтожаем флот
    });
  }

  checkVictory(): Player | null {
    const alive = this.players.filter(p => p.isAlive());
    if (alive.length === 1) return alive[0];
    if (this.turn >= this.maxTurns) {
      // подсчёт стоимости: здания + корабли + ресурсы × 0.5
      const scores = this.players.map(p => {
        let score = 0;
        // ресурсы
        score += (p.resources.iron + p.resources.copper + p.resources.silicon + p.resources.titanium) * 0.5;
        score += p.resources.energy * 0.5;

        // здания (упрощённо: сумма стоимостей)
        p.planets.forEach(pl => {
          pl.buildings.forEach(b => {
            // тут лучше брать из JSON, но для примера считаем условно
            score += 10; // заглушка
          });
        });

        // корабли
        p.ships.forEach(s => score += 10); // заглушка

        return { player: p, score };
      });
      return scores.reduce((a, b) => (a.score > b.score ? a : b)).player;
    }
    return null;
  }

  nextTurn() {
    this.startTurn();
    this.phaseIncome();
    // фаза стройки и движения — это действия игроков, они вызываются отдельно
    this.phaseCombat();
    this.phaseColonizationAndDefeat();
    return this.checkVictory();
  }
}
