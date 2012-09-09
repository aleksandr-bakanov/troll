package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.utils.Dictionary;
	import model.MainModel;
	
	/**
	 * ...
	 * @author bav
	 */
	public class FightWindow extends Sprite 
	{
		public var module:FightWindow_asset;
		private var _model:MainModel;
		private var _cells:Array = [];
		private var _floors:Array = [];
		private var _players:Object = { };
		
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
		}
		
		private function startFight(e:UserEvent):void 
		{
			// Размещаем игроков
			for (var id:String in _model.fInfo.players)
			{
				var o:Object = _model.fInfo.players[id];
				if (!_floors[o.floor_id])
					_floors[o.floor_id] = createFloor();
			}
		}
		
		private function createFloor():Sprite
		{
			return new Sprite();
		}
		
	}

}