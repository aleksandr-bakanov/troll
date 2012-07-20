package view.menu 
{
	import by.blooddy.crypto.serialization.JSON;
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import model.MainModel;
	import view.MainView;
	
	/**
	 * Окно инвентаря
	 * @author bav
	 */
	public class BackpackWindow extends Sprite 
	{
		public var module:BackpackWindow_asset;
		private var items:Object;
		
		public function BackpackWindow() 
		{
			items = {};
			module = new BackpackWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.INIT_BACKPACK, initBackpack);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
			addEventListener(Event.ADDED, addedHandler);
		}
		
		private function addedHandler(e:Event):void 
		{
			for (var id:String in items)
			{
				var info:Object = MainModel.items[id];
				if (info)
				{
					var item:Item_asset = items[id] as Item_asset;
					item.tf.text = id + ") " + JSON.encode(info);
					/*for (var prop:String in info)
					{
						
					}*/
				}
			}
		}
		
		private function initBackpack(e:UserEvent):void 
		{
			/// TODO: Приделать какую-нибудь прокрутку списку предметов.
			var counter:int = 0;
			for (var id:String in e.data)
			{
				var item:Item_asset = new Item_asset();
				item.y = counter * item.height;
				module.items.addChild(item);
				items[id] = item;
				counter++;
			}
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
	}

}