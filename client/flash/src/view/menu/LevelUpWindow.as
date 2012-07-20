package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import view.MainView;
	
	/**
	 * Окно прокачки
	 * @author bav
	 */
	public class LevelUpWindow extends Sprite 
	{
		public var module:LevelUpWindow_asset;
		
		public function LevelUpWindow() 
		{
			module = new LevelUpWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			var names:Array = ["plus_strength", "plus_dexterity", "plus_intellect", "plus_health"];
			for (var i:int = 0; i < names.length; i++)
				module.getChildByName(names[i]).addEventListener(MouseEvent.CLICK, paramChange);
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
		private function paramsUpdated(e:UserEvent):void 
		{
			module.rest.text = e.data.unusedOP.toString();
			module.strength.text = e.data.strength.toString();
			module.dexterity.text = e.data.dexterity.toString();
			module.intellect.text = e.data.intellect.toString();
			module.health.text = e.data.health.toString();
			module.speed.text = e.data.speed.toFixed(1);
			module.hitPoints.text = e.data.hitPoints.toString();
			module.deviation.text = e.data.deviation.toString();
			module.maxLoad.text = e.data.maxLoad.toString();
			var names:Array = ["strength", "dexterity", "intellect", "health"];
			for (var i:int = 0; i < names.length; i++)
			{
				if (names[i] == "strength" || names[i] == "health")
					module.getChildByName("plus_" + names[i]).visible = e.data.unusedOP >= 10;
				else
					module.getChildByName("plus_" + names[i]).visible = e.data.unusedOP >= 20;
			}
		}
		
		private function paramChange(e:MouseEvent):void 
		{
			var n:String = e.currentTarget.name;
			var sign:int = n.indexOf("plus") == 0 ? 1 : -1;
			var param:String = n.split("_")[1];
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.PARAM_CHANGED, { param:param, sign:sign } ));
		}
		
	}

}