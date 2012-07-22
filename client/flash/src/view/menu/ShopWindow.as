package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import model.MainModel;
	import view.MainView;
	
	/**
	 * Окно магазина
	 * @author bav
	 */
	public class ShopWindow extends Sprite 
	{
		public var module:ShopWindow_asset;
		private var _model:MainModel;
		
		private var shop:Object = {}
		private var backpack:Object = {}
		
		public function ShopWindow(model:MainModel) 
		{
			_model = model;
			module = new ShopWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.INIT_SHOP, initShop);
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
			addEventListener(Event.ADDED, addedHandler);
		}
		
		private function addedHandler(e:Event):void 
		{
			for (var id:String in backpack)
			{
				var info:Object = _model.params.backpack[id];
				item.tf.text = id + ") " + info.name + " (" + info.count + ")";
			}
		}
		
		private function paramsUpdated(e:UserEvent):void 
		{
			module.rest.text = String(_model.params.money);
		}
		
		private function initShop(e:UserEvent):void 
		{
			// Инициализируем предметы из рюкзака
			var id:String;
			var item:Shop_item_asset;
			var info:Object;
			var counter:int = 0;
			for (id in _model.params.backpack)
			{
				item = new Shop_item_asset();
				info = _model.params.backpack[id];
				item.tf.text = id + ") " + info.name + " (" + info.count + ")";
				item.y = counter++ * item.height;
				// Вот тут три ссылки на item
				module.backpack.addChild(item);
				backpack[id] = item;
				item.btn.addEventListener(MouseEvent.CLICK, sellItem);
			}
			// Инициализируем предметы в магазине
			counter = 0;
			for (id in MainModel.items)
			{
				item = new Shop_item_asset();
				info = MainModel.items[id];
				item.tf.text = id + ") " + info.name;
				item.y = counter++ * item.height;
				// Вот тут три ссылки на item
				module.shop.addChild(item);
				shop[id] = item;
				item.btn.addEventListener(MouseEvent.CLICK, buyItem);
			}
		}
		
		private function buyItem(e:MouseEvent):void 
		{
			
		}
		
		private function sellItem(e:MouseEvent):void 
		{
			
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
	}

}
