package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import view.MainView;
	
	/**
	 * Окно создания заявки.
	 * @author bav
	 */
	public class CreateBidWindow extends Sprite 
	{
		public var module:CreateBidWindow_asset;
		
		public function CreateBidWindow() 
		{
			module = new CreateBidWindow_asset();
			addChild(module);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
			module.create.addEventListener(MouseEvent.CLICK, createClickHandler);
			addEventListener(Event.ADDED_TO_STAGE, addedHandler);
		}
		
		private function addedHandler(e:Event):void 
		{
			module.bidName.text = module.count.text = "";
		}
		
		private function createClickHandler(e:MouseEvent):void 
		{
			if (module.count.length)
			{
				var count:int = parseInt(module.count.text);
				if (count && count >= 2 && count <= 6)
				{
					var bidName:String = module.bidName.length ? module.bidName.text : "unnamed";
					Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
					Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.CREATE_BID, { name:bidName, count:count } ));
				}
			}
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
	}

}