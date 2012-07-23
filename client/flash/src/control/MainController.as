package control 
{
	import flash.display.DisplayObjectContainer;
	import model.MainModel;
	import view.common.Debug;
	import view.MainView;
	
	/**
	 * Main application controller.
	 * @author bav
	 */
	public class MainController 
	{
		private var _mainView:MainView;
		private var _mainModel:MainModel;
		private var _connector:Connector;

		public function MainController(host:DisplayObjectContainer) 
		{
			Debug.init(host.stage);
			_mainModel = new MainModel();
			_mainView = new MainView(_mainModel, host);
			_connector = new Connector(_mainModel, host.stage.loaderInfo.parameters.host, host.stage.loaderInfo.parameters.port);
			configureHandlers();
			_connector.connect();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.DROP_ITEM, dropItemHandler);
			Dispatcher.instance.addEventListener(UserEvent.SELL_ITEM, sellItemHandler);
		}
		
		private function dropItemHandler(e:Object):void 
		{
			var id:int;
			if (e is UserEvent)
				id = e.data as int;
			else if (e is int)
				id = e as int;
			var place:int = 0;
			var idStr:String = String(id);
			var info:Object = _mainModel.params.backpack[idStr];
			info.count--;
			if (info.count < info.weared)
			{
				var places:Array = ["armour", "pants", "handWeapon", "beltWeapon"];
				for (var i:int = 0; i < places.length; i++)
				{
					if (_mainModel.params[places[i]] && _mainModel.params[places[i]].id == id)
					{
						_mainModel.params[places[i]] = 0;
						info.weared--;
						place = i + 1;
						break;
					}
				}
			}
			if (!info.count)
				delete _mainModel.params.backpack[idStr];
			_mainView.backpackWindow.dropItem(id, place);
			_mainView.shopWindow.dropBackpackItem(id);
			if (e is UserEvent)
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_DROP_ITEM, { id:id, place:place } ));
		}
		
		private function sellItemHandler(e:UserEvent):void 
		{
			var id:int = e.data as int;
			dropItemHandler(id);
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_SELL_ITEM, id));
		}
		
	}

}
