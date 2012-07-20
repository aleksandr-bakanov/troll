package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import model.MainModel;
	import view.MainView;
	
	/**
	 * Основное окно
	 * @author bav
	 */
	public class MainWindow extends Sprite 
	{
		public var module:MainWindow_asset;
		
		public function MainWindow() 
		{
			module = new MainWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			module.levelup.addEventListener(MouseEvent.CLICK, showOtherWindow);
			module.backpack.addEventListener(MouseEvent.CLICK, showOtherWindow);
		}
		
		private function showOtherWindow(e:MouseEvent):void 
		{
			var window:String;
			if (e.currentTarget.name == "levelup")
				window = MainView.LEVEL_UP_WINDOW;
			else if (e.currentTarget.name == "backpack")
				window = MainView.BACKPACK_WINDOW;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, window));
		}
		
		private function paramsUpdated(e:UserEvent):void 
		{
			module.op.text = e.data.usedOP ? e.data.usedOP.toString() : "0";
			module.money.text = e.data.money ? e.data.money.toString() : "0";
			module.energy.bar.scaleX = e.data.energy ? Number(e.data.energy) / MainModel.TOTAL_ENERGY : 1;
		}
		
	}

}