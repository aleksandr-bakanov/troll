package view.menu 
{
	import com.greensock.TweenLite;
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.display.Graphics;
	import flash.display.MovieClip;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.events.TimerEvent;
	import flash.geom.Point;
	import flash.utils.Dictionary;
	import flash.utils.Timer;
	import model.MainModel;
	import view.common.Debug;
	import view.fight.Unit;
	
	/**
	 * ...
	 * @author bav
	 */
	public class FightWindow extends Sprite 
	{
		// Константы эффектов на ячейках поля боя
		// Ячейка является препятствием
		public static const EFFECT_OBSTACLE:int = 1;
		// На ячейку можно встать
		public static const EFFECT_WALK:int = 2;
		// Ячейка может быть атакована
		public static const EFFECT_ATTACK:int = 4;
		public static var VISUAL_CELL_HEIGHT:Number = 100.0;
		public static var VISUAL_CELL_WIDTH:Number = 86.6025404;
		public static var VISUAL_CELL_RADIUS:Number = 50.0;
		public static const CELL_WIDTH:Number = 43.1;
		public static const CELL_HEIGHT:Number = 49.9;
		public static const CT_FLOOR:int = 1;
		public static const CT_WALL:int = 2;
		public static const CT_DOOR:int = 3;
		// Типы действий
		public static const ACT_WALK:int = 1;
		public static const ACT_ATTACK:int = 2;
		public static const ACT_CHANGE_WEAPON:int = 3;
		// TweenLite константы
		public static const STEP_DURATION:Number = 0.5;
		
		public var module:FightWindow_asset;
		private var _model:MainModel;
		private var _cells:Object = { };
		private var _floors:Object = { };
		private var _units:Object = { };
		// Текущее действие выбранное игроком
		private var _currentAction:int;
		// Игроков будем добавлять на уровни addChild. Новые ячейки будем добавлять на уровни addChildAt(cell, 0).
		// Игроку показывается его текущий уровень.
		private var _glowedActionRange:Array = [];
		private var _glowedCells:Array = [];
		// Таймер хода
		private var _moveTimer:Timer = new Timer(1000);
		private var _secondsLeft:int;
		
		public function FightWindow(model:MainModel) 
		{
			_model = model;
			module = new FightWindow_asset();
			addChild(module);
			configureHandlers();
			_moveTimer.addEventListener(TimerEvent.TIMER, moveTimerHandler);
			module.time.textColor = 0x000000;
		}
		
		private function configureHandlers():void
		{
			Dispatcher.instance.addEventListener(UserEvent.START_FIGHT, startFight);
			Dispatcher.instance.addEventListener(UserEvent.AREA_OPEN, areaOpen);
			Dispatcher.instance.addEventListener(UserEvent.KEYS_OPEN, keysOpen);
			Dispatcher.instance.addEventListener(UserEvent.S_CHAT_MESSAGE, sChatMessage);
			Dispatcher.instance.addEventListener(UserEvent.MOVE_UNIT, moveUnit);
			Dispatcher.instance.addEventListener(UserEvent.CHANGE_CELL, changeCell);
			Dispatcher.instance.addEventListener(UserEvent.TELEPORT_UNIT, teleportUnit);
			Dispatcher.instance.addEventListener(UserEvent.YOUR_MOVE, yourMove);
			
			module.enter.addEventListener(MouseEvent.CLICK, enterHandler);
		}
		
		private function yourMove(e:UserEvent):void 
		{
			Debug.out(e.data.unitId + " : " + _model.fInfo.selfId + " (" + e.data.seconds + ")");
			if (e.data.unitId == _model.fInfo.selfId)
			{
				_secondsLeft = e.data.seconds;
				_moveTimer.start();
			}
		}
		
		private function moveTimerHandler(e:TimerEvent):void 
		{
			Debug.out("timer: " + _secondsLeft);
			if (!_secondsLeft)
			{
				_moveTimer.stop();
				return;
			}
			module.time.text = String(_secondsLeft);
			_secondsLeft--;
		}
		
		private function enterHandler(e:MouseEvent):void 
		{
			if (module.input.text.length)
			{
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.C_CHAT_MESSAGE, module.input.text));
				module.input.text = "";
			}
		}
		
		private function sChatMessage(e:UserEvent):void 
		{
			var mes:String = e.data as String;
			module.output.appendText(mes + "\n");
			module.output.scrollV = module.output.maxScrollV;
		}
		
		private function startFight(e:UserEvent):void 
		{
			var ourFloor:int;
			// Размещаем игроков
			for (var id:String in _model.fInfo.players)
			{
				var o:Object = _model.fInfo.players[id];
				if (!_floors[o.floorId])
				{
					_floors[o.floorId] = createFloor();
				}
				var floor:Sprite = _floors[o.floorId] as Sprite;
				// Показываем этаж если мы на нем находимся.
				if (id == String(_model.fInfo.selfId))
				{
					module.map.addChild(floor);
					ourFloor = parseInt(id);
				}
				else
				{
					module.map.addChildAt(floor, 0);
				}
				var player:Unit = new Unit();
				player.x = o.x * CELL_WIDTH + (o.y % 2 ? CELL_WIDTH / 2 : 0);
				player.y = o.y * CELL_HEIGHT * 0.75;
				floor.addChild(player);
				_units[id] = player;
			}
			showFloor(ourFloor);
		}
		
		private function createFloor():Sprite
		{
			var floor:Sprite = new Sprite();
			floor.x = floor.y = 100;
			return floor;
		}
		
		private function showFloor(floorId:int):void
		{
			for (var id:String in _floors)
				(_floors[id] as DisplayObject).visible = id == String(floorId);
		}
		
		private function areaOpen(e:UserEvent):void 
		{
			for (var id:String in e.data)
			{
				// Создаем этаж если его еще не было.
				if (!_cells[id])
				{
					_cells[id] = [];
				}
				var floor:Array = _cells[id] as Array;
				// Проверяем создан ли floorView
				if (!_floors[id])
				{
					_floors[id] = createFloor();
					var f:Sprite = _floors[id] as Sprite;
					f.visible = _model.fInfo.players[_model.fInfo.selfId].floorId == parseInt(id);
					module.map.addChildAt(f, 0);
				}
				var floorInfo:Array = e.data[id] as Array;
				for (var i:int = 0; i < floorInfo.length; i++)
				{
					var info:Object = floorInfo[i];
					if (!floor[info.y])
						floor[info.y] = [];
					// Не забыть про type.
					var cell:Cell_asset = new Cell_asset();
					cell.addEventListener(MouseEvent.CLICK, cellClickHandler);
					cell.info = info;
					var s:Shape, g:Graphics;
					if (info.type == CT_FLOOR)
					{
						cell.gotoAndStop("floor");
						if (info.toFloor >= 0)
						{
							s = new Shape();
							g = s.graphics;
							g.lineStyle(1);
							g.beginFill(0x3333FF);
							g.drawCircle(0, 0, 5);
							g.endFill();
							cell.addChild(s);
						}
					}
					else if (info.type == CT_WALL)
					{
						cell.gotoAndStop("wall");
						if (info.key >= 0)
						{
							// Нужен какой-нибудь вразумительный сигнал о том, что на данной ячейке появился ключ.
							s = new Shape();
							g = s.graphics;
							g.lineStyle(1);
							g.beginFill(0xFF0000);
							g.drawCircle(0, 0, 5);
							g.endFill();
							cell.addChild(s);
						}
					}
					else if (info.type == CT_DOOR)
					{
						cell.gotoAndStop("wall");
						/// TODO: Как-то показать замки на двери
					}
					// Сохраняем ссылку на ячейку.
					floor[info.y][info.x] = cell;
					cell.x = CELL_WIDTH * info.x + (info.y % 2 ? CELL_WIDTH / 2 : 0);
					cell.y = CELL_HEIGHT * info.y * 0.75;
					(_floors[id] as DisplayObjectContainer).addChildAt(cell, 0);
				}
			}
		}
		
		private function keysOpen(e:UserEvent):void 
		{
			for (var id:String in e.data)
			{
				// Вьюшки
				var floor:Array = _cells[id] as Array;
				var floorInfo:Array = e.data[id] as Array;
				for (var i:int = 0; i < floorInfo.length; i++)
				{
					var info:Object = floorInfo[i];
					var cell:Cell_asset = floor[info.y][info.x] as Cell_asset;
					// Нужен какой-нибудь вразумительный сигнал о том, что на данной ячейке появился ключ.
					var s:Shape = new Shape();
					var g:Graphics = s.graphics;
					g.lineStyle(1);
					g.beginFill(0xFF0000);
					g.drawCircle(0, 0, 5);
					g.endFill();
					cell.addChild(s);
					
					cell.info.key = info.id;
				}
			}
		}
		
		private function changeCell(e:UserEvent):void 
		{
			var floor:Array = _cells[e.data.floor] as Array;
			if (!floor) return;
			var cell:Cell_asset = floor[e.data.y][e.data.x] as Cell_asset;
			if (!cell) return;
			cell.info.type = e.data.type;
			if (cell.info.type == CT_FLOOR) cell.gotoAndStop("floor");
			else cell.gotoAndStop("wall");
		}
		
		private function cellClickHandler(e:MouseEvent):void 
		{
			var cell:Cell_asset = e.currentTarget as Cell_asset;
			if (cell.info.type == CT_FLOOR)
				if (cell.info.toFloor < 0)
					Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.C_WANT_MOVE, new Point(cell.info.x, cell.info.y)));
				else
					Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.C_ACTION, new Point(cell.info.x, cell.info.y)));
			// Пока условимся, что кнопки могут быть расположены только на стенах
			else if (cell.info.type == CT_WALL && cell.info.key >= 0)
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.C_ACTION, new Point(cell.info.x, cell.info.y)));
		}
		
		private function moveUnit(e:UserEvent):void 
		{
			var unit:Unit = _units[e.data.id] as Unit;
			unit.move(e.data.path as Array);
		}
		
		private function teleportUnit(e:UserEvent):void 
		{
			var unit:Unit = _units[e.data.unitId] as Unit;
			unit.stopMove();
			var floor:Sprite = _floors[e.data.floor] as Sprite;
			unit.x = e.data.x * CELL_WIDTH + (e.data.y % 2 ? CELL_WIDTH / 2 : 0);
			unit.y = e.data.y * CELL_HEIGHT * 0.75;
			floor.addChild(unit);
			if (_model.fInfo.selfId == e.data.unitId)
				showFloor(e.data.floor);
		}
		
		/**
		 * Подсветка ячеек на расстоянии radius от ячейки, координаты
		 * которой указаны в center. Если isActionArea == true, ячейки подсвечиваются красным,
		 * иначе - серым.
		 * @param	center
		 * @param	radius
		 * @param	isActionArea
		 */
		private function glowRadius(floorId:int, width:int, height:int, xc:int, yc:int, r1:int, r2:int, glowCenter:Boolean = false, isActionArea:Boolean = false):void
		{
			var cells:Array = _cells[floorId] as Array;
			// Проверка на неверные данные
			if (width <= 0 || height <= 0 || !cells || yc < 0 || yc >= height || xc < 0 || xc >= width || r1 < 0 || r2 < 0 || (r1 >= r2 && r2 > 0))
				return;
			
			// Массив, в который будут собираться объекты вида { cell:cell, x:x, y:y }
			var array:Array = [];
			
			// Начальные значения переменных
			var lenStart:int = r2 * 2 + 1;
			var length:int = lenStart;
			var countDiscard:int = r1 * 2 + 1;
			var countAllow:int = length - countDiscard;
			var xs:int = xc - r2;
			var xe:int = xs + length - 1;
			var xcur:int = xs;
			var ycur:int = 0;
			var dy:int = 0;
			var cell:MovieClip;
			// Проходимся по вертикали r2 количество раз
			for (var a:int = 0; a <= r2 && r2 > 0; a++)
			{
				// Начинаем с центральной полосы
				for (var b:int = 0; b < length; b++)
				{
					//if (dy == 2 && xcur == 2)
						//Debug.out( "("+Math.abs(xs - xcur)+" < "+(countAllow / 2)+") || ("+Math.abs(xe - xcur)+" < "+(countAllow / 2)+")" );
					if ((Math.abs(xs - xcur) < (countAllow / 2)) || (Math.abs(xe - xcur) < (countAllow / 2)))
					{
						if (dy == 0)
						{
							ycur = yc;
							if (xcur >= 0 && xcur < width)
							{
								cell = cells[ycur][xcur] as MovieClip;
								array.push( { cell:cell, x:xcur, y:ycur } );
							}
						}
						else
						{
							ycur = yc + dy;
							if (xcur >= 0 && xcur < width && ycur >= 0 && ycur < height)
							{
								cell = cells[ycur][xcur] as MovieClip;
								array.push( { cell:cell, x:xcur, y:ycur } );
							}
							ycur = yc - dy;
							if (xcur >= 0 && xcur < width && ycur >= 0 && ycur < height)
							{
								cell = cells[ycur][xcur] as MovieClip;
								array.push( { cell:cell, x:xcur, y:ycur } );
							}
						}
					}
					xcur++;
				}
				// При переходе на следующую полосу корректируем значения переменных
				if (((yc + a) % 2) > 0) 
					xs++;
				xcur = xs;
				
				length--;
				countDiscard--;
				dy++;
				countAllow = length - (dy <= r1 ? countDiscard : 0);
				xe = xs + length - 1;
			}
			
			if (glowCenter && xc >= 0 && xc < width && yc >= 0 && yc < height)
			{
				cell = cells[yc][xc] as MovieClip;
				array.push( { cell:cell, x:xc, y:yc } );
			}
			
			//Debug.out("array.length = " + array.length);
			
			// Теперь, если ячейки необходимо подсветить серым цветом, т.е. не для показа радиуса
			// зонной атаки, нужно исключить из массива те ячейки которые будут недоступны из-за
			// препятствий на поле.
			if (!isActionArea)
			{
				// Будем просмотривать только те ячейки, которые являются препятствиями
				var obstacles:Array = getObstacles(array, xc, yc);
				// Удалим ячейки закрытые препятствиями
				array = reduceCellsByObstacles(xc, yc, array, obstacles);
				initCellsForChoising(array);
			}
			else
				glowActionAreaCells(array);
		}
		
		/**
		 * Функция удаляет из массива cells те ячейки, которые перекрываются препятствиями,
		 * представленными в массиве obstacles.
		 * @param	xc
		 * @param	yc
		 * @param	cells		массив объектов вида { cell:cell, x:x, y:y }
		 * @param	obstacles	массив точек, представляющих координаты ячеек-препятствий
		 */
		private function reduceCellsByObstacles(xc:int, yc:int, cells:Array, obstacles:Array):Array
		{
			// Проходимся по всем ячейкам, содержащимся в cells
			for (var i:int = 0; i < cells.length; i++)
			{
				var o:Object = cells[i];
				if (isObstacled(xc, yc, o.x, o.y, obstacles))
				{
					cells.splice(i--, 1);
				}
			}
			return cells;
		}
		
		/**
		 * Функция возвращает true если точку cell при наблюдении из (xc;yc) загораживает
		 * какое-нибудь препятствие из obstacles.
		 * @param	xc
		 * @param	yc
		 * @param	toX
		 * @param	toY
		 * @param	obstacles
		 * @return
		 */
		private function isObstacled(xc:int, yc:int, toX:int, toY:int, obstacles:Array):Boolean
		{
			// Визуальные координаты
			var vxc:Number = Number(xc) * VISUAL_CELL_WIDTH + (yc % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
			var vyc:Number = Number(yc) * VISUAL_CELL_HEIGHT * 0.75;
			var vtoX:Number = Number(toX) * VISUAL_CELL_WIDTH + (toY % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
			var vtoY:Number = Number(toY) * VISUAL_CELL_HEIGHT * 0.75;
			
			// Анализируем все препятствия
			for (var i:int = 0; i < obstacles.length; i++)
			{
				// Визуальные координаты текущего препятствие
				var vox:Number = obstacles[i].x * VISUAL_CELL_WIDTH + (int(obstacles[i].y) % 2 ? VISUAL_CELL_WIDTH / 2.0 : 0);
				var voy:Number = obstacles[i].y * VISUAL_CELL_HEIGHT * 0.75;
				
				// Во-первых узнаем, если расстояние до текущего препятствия больше
				// чем до целевой точки, можно пропустить это препятствие.
				if (Math.sqrt(Math.pow(vxc - vox, 2) + Math.pow(vyc - voy, 2)) > Math.sqrt(Math.pow(vxc - vtoX, 2) + Math.pow(vyc - vtoY, 2)))
					continue;
				
				// Иначе составляем нормальное уравнение прямой (по координатам точки наблюдения и препятствия)
				// и выясняем расстояние от целевой точки до этой прямой.
				// Если это расстояние меньше чем VISUAL_CELL_RADIUS, значит клетка не видна из точки наблюдения.
				var d:Number = getPerpDistance(vxc, vyc, vtoX, vtoY, vox, voy);
				if (d < VISUAL_CELL_RADIUS && !(toX == int(obstacles[i].x) && toY == int(obstacles[i].y)))
				{
					var R:Number = Math.sqrt(Math.pow(vtoX - vox, 2) + Math.pow(vtoY - voy, 2));
					var L:Number = Math.sqrt(Math.pow(vxc - vtoX, 2) + Math.pow(vyc - vtoY, 2));
					if (R < L) {
						return true;
					}
				}
			}
			return false;
		}
		
		/**
		 * Функция возвращает расстояние от точки (vtoX, vtoY) до прямой, проходящей через
		 * точки (vxc, vyc) и (vox, voy).
		 * @param	vxc
		 * @param	vyc
		 * @param	vox
		 * @param	voy
		 * @param	vtoX
		 * @param	vtoY
		 * @return
		 */
		private function getPerpDistance(vxc:Number, vyc:Number, vtoX:Number, vtoY:Number, vox:Number, voy:Number):Number
		{
			var A:Number = vyc - vtoY;
			var B:Number = vtoX - vxc;
			var C:Number = vxc * vtoY - vtoX * vyc;
			var d:Number = Math.abs( Number(A * vox + B * voy + C) / Math.sqrt(A * A + B * B) );
			return d;
		}
		
		/**
		 * Функция возвращает массив точек, таких что клетки на соответствующих
		 * координатах являются препятствием.
		 * Функция получает массив объектов вида { cell:cell, x:x, y:y }
		 * @return
		 */
		private function getObstacles(cells:Array, exceptX:int, exceptY:int):Array
		{
			var r:Array = [];
			for (var i:int = 0; i < cells.length; i++)
				if (!(exceptX == cells[i].x && exceptY == cells[i].y) && cells[i].cell.info.type == CT_WALL)
					r.push(new Point(cells[i].x, cells[i].y));
			return r;
		}
		
		/**
		 * Функция получает массив объектов вида { cell:cell, x:x, y:y }
		 * @param	cells
		 */
		private function glowActionAreaCells(cells:Array):void
		{
			for (var i:int = 0; i < cells.length; i++)
			{
				var o:Object = cells[i];
				// Проверим можно ли атаковать эту ячейку
				//if (_mainModel.fightInfo.cells[o.y][o.x] & EFFECT_ATTACK)
				{
					if (_glowedActionRange.indexOf(o.cell) < 0)
					{
						_glowedActionRange.push(o.cell);
						o.cell.gotoAndStop("red");
					}
				}
			}
		}

		private function removeActionAreaGlowing():void
		{
			while (_glowedActionRange.length)
			{
				var cell:MovieClip = _glowedActionRange.pop() as MovieClip;
				cell.gotoAndStop(cell.previousState);
			}
		}

		/**
		 * Функция получает массив объектов вида { cell:cell, x:x, y:y }
		 * @param	cells
		 */
		private function initCellsForChoising(cells:Array):void
		{
			for (var i:int = 0; i < cells.length; i++)
			{
				var o:Object = cells[i];
				// Сохраняем ячейку в массиве _glowedCells
				// Здесь проверяем нет ли какого игрока на этой ячейке.
				//var canGlow:Boolean = true;
				var canGlow:Boolean = o.cell.info.type == CT_FLOOR;
				/*if (_currentAction == FightSkills.ACTION_SIMPLE_WALK)
					canGlow = Boolean(_mainModel.fightInfo.cells[o.y][o.x] & EFFECT_WALK);
				else
					canGlow = Boolean(_mainModel.fightInfo.cells[o.y][o.x] & EFFECT_ATTACK);*/
				if (canGlow)
				{
					_glowedCells.push(o.cell);
					o.cell.gotoAndStop("green");
					o.cell.previousState = "green";
					/*o.cell.addEventListener(MouseEvent.ROLL_OVER, rollOverGlowedCellHandler);
					o.cell.addEventListener(MouseEvent.ROLL_OUT, rollOutGlowedCellHandler);
					o.cell.addEventListener(MouseEvent.MOUSE_DOWN, mouseDownGlowedCellHandler);*/
				}
			}
		}
		
	}

}
