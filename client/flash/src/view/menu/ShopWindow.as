package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.sampler.NewObjectSample;
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
			Dispatcher.instance.addEventListener(UserEvent.ADD_ITEM, addItem);
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
			addEventListener(Event.ADDED, addedHandler);
		}
		
		private function addItem(e:UserEvent):void 
		{
			var id:String = String(e.data as int);
			var info:Object = _model.params.backpack[id];
			if (backpack[id])
				(backpack[id] as Shop_item_asset).tf.text = id + ") " + info.name + " (" + info.count + ")";
			else
			{
				var item:Shop_item_asset = new Shop_item_asset();
				item.tf.text = id + ") " + info.name + " (" + info.count + ")";
				var counter:int = 0;
				for (var i:String in backpack)
					counter++;
				item.y = counter * item.height;
				// Вот тут три ссылки на item
				module.backpack.addChild(item);
				backpack[id] = item;
				item.btn.addEventListener(MouseEvent.CLICK, sellItem);
				item.btn.id = id;
			}
		}
		
		private function addedHandler(e:Event):void 
		{
			var id:String;
			var info:Object;
			for (id in backpack)
			{
				info = _model.params.backpack[id];
				(backpack[id] as Shop_item_asset).tf.text = id + ") " + info.name + " (" + info.count + ")";
			}
			var money:int = _model.params.money;
			for (id in shop)
			{
				info = MainModel.items[id];
				(shop[id] as Shop_item_asset).btn.visible = money >= info.cost;
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
				item.btn.id = id;
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
				item.btn.id = id;
			}
		}
		
		private function buyItem(e:MouseEvent):void 
		{
			var id:String = (e.currentTarget as Object).id as String;
			if (_model.params.money >= MainModel.items[id].cost)
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_BUY_ITEM, parseInt(id)));
		}
		
		private function sellItem(e:MouseEvent):void 
		{
			var id:String = (e.currentTarget as Object).id as String;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SELL_ITEM, parseInt(id)));
		}
		
		public function dropBackpackItem(id:int):void
		{
			var idStr:String = String(id);
			var info:Object = _model.params.backpack[idStr];
			var item:Shop_item_asset = backpack[idStr] as Shop_item_asset;
			if (!info)
			{
				item.btn.removeEventListener(MouseEvent.CLICK, sellItem);
				module.backpack.removeChild(item);
				delete backpack[idStr];
				sortItems();
			}
			else
				item.tf.text = idStr + ") " + info.name + " (" + info.count + ")";
		}
		
		private function sortItems():void 
		{
			var counter:int = 0;
			for (var id:String in backpack)
			{
				var item:DisplayObject = backpack[id] as DisplayObject;
				item.y = item.height * counter++;
			}
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
	}

}
