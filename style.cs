body { font-family: Arial, sans-serif; padding: 10px; }
.board { display: grid; grid-template-columns: repeat(100, 20px); grid-template-rows: repeat(100, 20px); gap: 0; }
.cell { width: 20px; height: 20px; border: 1px solid #ccc; box-sizing: border-box; }
.sun { background: radial-gradient(circle, #ffaa00 0%, #ff0000 100%); }
.burn-zone { background: #ffcccc; }
.planet { background: #888; }
.ship { background: blue; border: 2px solid white; }
.log { margin-top: 10px; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 5px; }
.controls { margin-bottom: 10px; }
