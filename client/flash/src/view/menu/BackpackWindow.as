package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.IEventDispatcher;
	import flash.events.MouseEvent;
	import model.MainModel;
	import view.common.Debug;
	import view.MainView;
	
	/**
	 * Окно инвентаря
	 * @author bav
	 */
	public class BackpackWindow extends Sprite 
	{
		public static const WEAPON:int = 1;
		public static const ARMOUR:int = 2;
		public static const PANTS:int = 3;
		
		private var _model:MainModel;
		public var module:BackpackWindow_asset;
		private var items:Object;
		
		private var _currentItemId:int;
		
		public function BackpackWindow(model:MainModel) 
		{
			_model = model;
			items = {};
			module = new BackpackWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.INIT_BACKPACK, initBackpack);
			Dispatcher.instance.addEventListener(UserEvent.ADD_ITEM, addItem);
			module.returnBtn.addEventListener(MouseEvent.CLICK, returnClickHandler);
			addEventListener(Event.ADDED, addedHandler);
		}
		
		private function addItem(e:UserEvent):void 
		{
			var id:String = String(e.data as int);
			var info:Object = _model.params.backpack[id];
			if (items[id])
				(items[id] as Item_asset).tf.text = id + ") " + info.name + " (" + info.count + ")";
			else
			{
				var item:Item_asset = new Item_asset();
				item.tf.text = id + ") " + info.name + " (" + info.count + ")";
				var counter:int = 0;
				for (var i:String in items)
					counter++;
				item.y = counter * item.height;
				module.items.addChild(item);
				items[id] = item;
				if (info.type == WEAPON || info.type == ARMOUR || info.type == PANTS)
				{
					item.drop.addEventListener(MouseEvent.CLICK, dropHandler);
					item.wear.addEventListener(MouseEvent.CLICK, wearItem);
					item.drop.id = item.wear.id = id;
				}
				else if (item.drop.visible)
				{
					item.drop.visible = item.wear.visible = false;
				}
			}
		}
		
		private function addedHandler(e:Event = null):void 
		{
			var id:String;
			var info:Object;
			var totalWeight:int = 0;
			for (id in _model.params.backpack)
			{
				info = _model.params.backpack[id];
				totalWeight += info.weight * info.count;
			}
			module.rest.text = String(_model.params.maxLoad - totalWeight);
		}
		
		private function wearItem(e:MouseEvent):void 
		{
			var id:String = (e.currentTarget as MovieClip).id;
			var info:Object = _model.params.backpack[id];
			if (info.weared == info.count)
				return;
			var weared:Boolean = false;
			if (info.type == ARMOUR || info.type == PANTS)
			{
				var place:int = info.type == ARMOUR ? 1 : 2;
				if ((info.type == ARMOUR && _model.params.armour) ||
					(info.type == PANTS && _model.params.pants))
					return;
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.WEAR_ITEM,
					{ id:parseInt(id), wear:true, place:place } ));
				var cont:MovieClip = place == 1 ? module.armour : module.pants;
				cont.tf.text = info.name;
				cont.drop.visible = true;
				cont.drop.id = parseInt(id);
				weared = true;
				if (info.type == ARMOUR)
					_model.params.armour = info;
				else
					_model.params.pants = info;
			}
			else if (!(module.handWeapon.drop as DisplayObject).visible ||
				!(module.beltWeapon.drop as DisplayObject).visible)
			{
				_currentItemId = parseInt(id);
				switchChooseHands();
				weared = true;
			}
			if (weared)
			{
				info.weared++;
				if (info.weared == info.count)
					e.currentTarget.visible = (e.currentTarget.parent as MovieClip).drop.visible = false;
			}
		}
		
		private function switchChooseHands():void 
		{
			module.handWeapon.place.visible = !module.handWeapon.drop.visible;
			module.beltWeapon.place.visible = !module.beltWeapon.drop.visible;
			module.blocker.visible = true;
		}
		
		private function wearInHand(e:MouseEvent):void 
		{
			var place:int = e.currentTarget.parent.name == "handWeapon" ? 3 : 4;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.WEAR_ITEM,
				{ id:_currentItemId, wear:true, place:place } ));
			module.handWeapon.place.visible = module.beltWeapon.place.visible = false;
			var cont:MovieClip = place == 3 ? module.handWeapon : module.beltWeapon;
			var info:Object = _model.params.backpack[String(_currentItemId)];
			cont.tf.text = info.name;
			cont.drop.visible = true;
			cont.drop.id = _currentItemId;
			module.blocker.visible = false;
			if (place == 3)
				_model.params.handWeapon = info;
			else
				_model.params.beltWeapon = info;
		}
		
		private function unwearItem(e:MouseEvent):void 
		{
			// currentTarget - это кнопка drop
			var id:int = (e.currentTarget as MovieClip).id;
			var cont:MovieClip = e.currentTarget.parent as MovieClip;
			e.currentTarget.visible = false;
			cont.tf.text = "";
			(items[String(id)] as Item_asset).wear.visible = true;
			(items[String(id)] as Item_asset).drop.visible = true;
			_model.params.backpack[String(id)].weared--;
			_model.params[cont.name] = 0;
			var place:int;
			if (cont.name == "armour")
				place = 1;
			else if (cont.name == "pants")
				place = 2;
			else if (cont.name == "handWeapon")
				place = 3;
			else if (cont.name == "beltWeapon")
				place = 4;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.WEAR_ITEM,
				{ id:id, wear:false, place:place } ));
		}
		
		private function dropHandler(e:MouseEvent):void 
		{
			var id:String = (e.currentTarget as MovieClip).id;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.DROP_ITEM, parseInt(id) ));
		}
		
		public function dropItem(id:int, place:int):void
		{
			var idStr:String = String(id);
			var info:Object = _model.params.backpack[idStr];
			var item:Item_asset = items[idStr] as Item_asset;
			if (!info)
			{
				item.drop.removeEventListener(MouseEvent.CLICK, dropHandler);
				item.wear.removeEventListener(MouseEvent.CLICK, wearItem);
				module.items.removeChild(item);
				delete items[idStr];
				sortItems();
			}
			else
				item.tf.text = idStr + ") " + info.name + " (" + info.count + ")";
			if (place)
			{
				var places:Array = ["armour", "pants", "handWeapon", "beltWeapon"];
				var cont:MovieClip = module[places[place - 1]] as MovieClip;
				cont.drop.visible = false;
				cont.tf.text = "";
				cont.drop.id = 0;
			}
			// Обновляем вес
			addedHandler();
		}
		
		private function sortItems():void 
		{
			var counter:int = 0;
			for (var id:String in items)
			{
				var item:DisplayObject = items[id] as DisplayObject;
				item.y = item.height * counter++;
			}
		}
		
		private function initBackpack(e:UserEvent):void 
		{
			/// TODO: Приделать какую-нибудь прокрутку списку предметов.
			var counter:int = 0;
			var totalWeight:int = 0;
			var info:Object;
			for (var id:String in e.data)
			{
				info = e.data[id];
				// Количество одетых предметов с данным id
				info.weared = 0;
				var item:Item_asset = new Item_asset();
				item.tf.text = id + ") " + info.name + " (" + info.count + ")";
				item.y = counter * item.height;
				module.items.addChild(item);
				items[id] = item;
				totalWeight += e.data[id].weight * e.data[id].count;
				if (info.type == WEAPON || info.type == ARMOUR || info.type == PANTS)
				{
					item.drop.addEventListener(MouseEvent.CLICK, dropHandler);
					item.wear.addEventListener(MouseEvent.CLICK, wearItem);
					item.drop.id = item.wear.id = id;
				}
				else if (item.drop.visible)
				{
					item.drop.visible = item.wear.visible = false;
				}
				counter++;
			}
			module.rest.text = String(_model.params.maxLoad - totalWeight);
			// Скрываем кнопки снятия предметов
			var drops:Array = [
				module.armour.drop, module.pants.drop, 
				module.handWeapon.drop, module.beltWeapon.drop
			];
			var i:int;
			for (i = 0; i < drops.length; i++)
			{
				(drops[i] as DisplayObject).visible = false;
				(drops[i] as EventDispatcher).addEventListener(MouseEvent.CLICK, unwearItem);
			}
			module.handWeapon.place.visible = module.beltWeapon.place.visible =
			module.blocker.visible = false;
			module.handWeapon.place.addEventListener(MouseEvent.CLICK, wearInHand);
			module.beltWeapon.place.addEventListener(MouseEvent.CLICK, wearInHand);
			
			var places:Array = ["armour", "pants", "handWeapon", "beltWeapon"];
			for (i = 0; i < places.length; i++)
			{
				if (_model.params[places[i]])
				{
					var cont:MovieClip = module[places[i]] as MovieClip;
					info = _model.params.backpack[String(_model.params[places[i]].id)];
					info.weared++;
					cont.drop.visible = true;
					cont.tf.text = info.name;
					cont.drop.id = info.id;
					if (info.weared == info.count)
						(items[String(info.id)] as Item_asset).wear.visible = false;
				}
			}
		}
		
		private function returnClickHandler(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
	}

}
