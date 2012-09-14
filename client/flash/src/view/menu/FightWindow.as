package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObject;
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.utils.Dictionary;
	import model.MainModel;
	import view.common.Debug;
	
	/**
	 * ...
	 * @author bav
	 */
	public class FightWindow extends Sprite 
	{
		public static const CELL_WIDTH:Number = 43.1;
		public static const CELL_HEIGHT:Number = 49.9;
		public static const CT_FLOOR:int = 1;
		public static const CT_WALL:int = 2;
		public static const CT_DOOR:int = 3;
		
		public var module:FightWindow_asset;
		private var _model:MainModel;
		private var _cells:Object = { };
		private var _floors:Object = { };
		private var _players:Object = { };
		// Игроков будем добавлять на уровни addChild. Новые ячейки будем добавлять на уровни addChildAt(cell, 0).
		// Игроку показывается его текущий уровень.
		
		public function FightWindow(model:MainModel) 
		{
			_model = model;
			module = new FightWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void
		{
			Dispatcher.instance.addEventListener(UserEvent.START_FIGHT, startFight);
			Dispatcher.instance.addEventListener(UserEvent.AREA_OPEN, areaOpen);
		}
		
		private function startFight(e:UserEvent):void 
		{
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
				module.map.addChild(floor);
				var player:Player_asset = new Player_asset();
				player.x = o.x * CELL_WIDTH + (o.y % 2 ? CELL_WIDTH / 2 : 0);
				player.y = o.y * CELL_HEIGHT * 0.75;
				floor.addChild(player);
				_players[id] = player;
			}
		}
		
		private function createFloor():Sprite
		{
			var floor:Sprite = new Sprite();
			floor.x = floor.y = 100;
			return floor;
		}
		
		private function areaOpen(e:UserEvent):void 
		{
			for (var id:String in e.data)
			{
				if (!_cells[id])
					_cells[id] = [];
				var floor:Array = _cells[id] as Array;
				// Проверяем создан ли floorView
				if (!_floors[id])
				{
					_floors[id] = createFloor();
					var f:Sprite = _floors[id] as Sprite;
					module.map.addChild(f);
				}
				var floorInfo:Array = e.data[id] as Array;
				for (var i:int = 0; i < floorInfo.length; i++)
				{
					var info:Object = floorInfo[i];
					if (!floor[info.y])
						floor[info.y] = [];
					// Не забыть про type.
					var cell:Cell_asset = new Cell_asset();
					// Сохраняем ссылку на ячейку.
					floor[info.y][info.x] = cell;
					cell.x = CELL_WIDTH * info.x + (info.y % 2 ? CELL_WIDTH / 2 : 0);
					cell.y = CELL_HEIGHT * info.y * 0.75;
					(_floors[id] as DisplayObjectContainer).addChildAt(cell, 0);
				}
			}
		}
		
	}

}