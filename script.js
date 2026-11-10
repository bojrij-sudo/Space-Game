// --- ДАННЫЕ (вместо data/*.json) ---
const constants = {
  boardSize: 100,
  sunPosition: { x: 50, y: 50 },
  sunBurnDamage: 10,
  turnsToVictory: 30
};

const planetsData = [
  { name: 'Mercury', type: 'rocky', slots: 4, x: 48, y: 50 },
  { name: 'Venus', type: 'rocky', slots: 9, x: 52, y: 50 }
];

const buildingsData = [
  { name: 'IronMine', cost: { iron: 10, copper: 5 }, effect: { ironPerTurn: 3 } },
  { name: 'Generator', cost: { iron: 10, copper: 5, silicon: 5 }, effect: { energyPerTurn: 5 } }
];

const shipsData = [
  { name: 'Fighter', cost: { iron: 5, copper: 3, silicon: 2 }, hp: 10, damage: 4, range: 1 }
];

// --- ТИПЫ / КЛАССЫ ---
class Planet {
  constructor(data) {
    this.name = data.name;
    this.type = data.type;
    this.slots = data.slots;
    this.x = data.x;
    this.y = data.y;
    this.ownerId = null;
    this.buildings = [];
  }
  canBuild() { return this.buildings.length < this.slots; }
  addBuilding(b) { if (this.canBuild()) this.buildings.push(b); }
}

class Ship {
  constructor(id, data, x, y, ownerId) {
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
  takeDamage(amount) { this.hp -= amount; }
}

class Player {
  constructor(id) {
    this.id = id;
    this.resources = { iron: 20, copper: 10, silicon: 10, titanium: 5, energy: 20 };
    this.planets = [];
    this.ships = [];
  }
  spend(cost) {
    for (const k in cost) {
      if ((this.resources[k] ?? 0) < cost[k]) return false;
    }
    for (const k in cost) this.resources[k] -= cost[k];
    return true;
  }
}

// --- ИГРА ---
class Game {
  constructor() {
    this.boardSize = constants.boardSize;
    this.sun = constants.sunPosition;
    this.turn = 0;
    this.players = [new Player(0), new Player(1)];
    this.planets = planetsData.map(d => new Planet(d));
    this.nextShipId = 1;

    // Раздаём планеты игрокам по очереди
    this.planets.forEach((p, i) => {
      const owner = this.players[i % this.players.length];
      owner.planets.push(p);
      p.ownerId = owner.id;
    });

    // Стартовые корабли на планетах
    const starterShip = shipsData[0];
    this.planets.slice(0, 2).forEach((p, i) => {
      const ship = new Ship(this.nextShipId++, starterShip, p.x, p.y, this.players[i].id);
      this.players[i].ships.push(ship);
    });
  }

  isSun(x, y) { return x === this.sun.x && y === this.sun.y; }

  getBurnDamage(x, y) {
    if (!this.isInBounds(x, y)) return 0;
    const dx = Math.abs(x - this.sun.x);
    const dy = Math.abs(y - this.sun.y);
    return (dx <= 1 && dy <= 1) ? constants.sunBurnDamage : 0;
  }

  isInBounds(x, y) { return x >= 0 && x < this.boardSize && y >= 0 && y < this.boardSize; }

  nextTurn() {
    this.turn++;
    const log = document.getElementById('log');
    log.innerHTML += `<div>[Ход ${this.turn}]</div>`;

    // Доход
    this.players.forEach(p => {
      let totalEnergy = 0, totalConsumption = 0;
      p.planets.forEach(pl => {
        pl.buildings.forEach(b => {
          if (b.effect.energyPerTurn) totalEnergy += b.effect.energyPerTurn;
        });
      });
      // Упрощённо: считаем, что дефицита нет
      p.planets.forEach(pl => {
        if (pl.buildings.some(b => b.name === 'IronMine')) {
          p.resources.iron += 3;
        }
      });
    });

    // Урон от Солнца
    this.players.flatMap(p => p.ships).forEach(s => {
      const dmg = this.getBurnDamage(s.x, s.y);
      if (dmg > 0) {
        s.takeDamage(dmg);
        log.innerHTML += `<div>Корабль ${s.id} получил ${dmg} урона от Солнца (${s.x},${s.y})</div>`;
      }
    });

    // Удаляем мёртвые корабли
    this.players.forEach(p => {
      p.ships = p.ships.filter(s => s.hp > 0);
    });

    // Победа
    const alive = this.players.filter(p => p.planets.length > 0 || p.ships.length > 0);
    if (alive.length === 1) {
      log.innerHTML += `<div style="color:green">Победа игрока ${alive[0].id}!</div>`;
      document.getElementById('btn-next-turn').disabled = true;
      return;
    }
    if (this.turn >= constants.turnsToVictory) {
      log.innerHTML += `<div style="color:orange">Лимит ходов достигнут. Подсчёт очков...</div>`;
      document.getElementById('btn-next-turn').disabled = true;
    }

    this.render();
  }

  render() {
    const boardEl = document.getElementById('board');
    boardEl.innerHTML = '';
    for (let y = 0; y < this.boardSize; y++) {
      for (let x = 0; x < this.boardSize; x++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        if (this.isSun(x, y)) cell.classList.add('sun');
        else if (this.getBurnDamage(x, y) > 0) cell.classList.add('burn-zone');

        // Планета
        const planet = this.planets.find(p => p.x === x && p.y === y);
        if (planet) cell.classList.add('planet');

        // Корабль
        const ship = this.players.flatMap(p => p.ships).find(s => s.x === x && s.y === y);
        if (ship) {
          const shipEl = document.createElement('div');
          shipEl.className = 'ship';
          shipEl.title = `HP: ${ship.hp}`;
          cell.appendChild(shipEl);
        }

        boardEl.appendChild(cell);
      }
    }
    document.getElementById('turn-display').textContent = `Ход: ${this.turn}`;
  }
}

// --- ЗАПУСК ---
const game = new Game();
game.render();

document.getElementById('btn-next-turn').addEventListener('click', () => {
  game.nextTurn();
});
