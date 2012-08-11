package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.EventDispatcher;
	import flash.events.MouseEvent;
	import model.MainModel;
	import view.common.Debug;
	import view.MainView;
	
	/**
	 * Основное окно
	 * @author bav
	 */
	public class MainWindow extends Sprite 
	{
		private static const BID_MARGIN:int = 2;
		
		public var module:MainWindow_asset;
		private var _model:MainModel;
		private var bids:Array = [];
		
		public function MainWindow(model:MainModel) 
		{
			_model = model;
			module = new MainWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			Dispatcher.instance.addEventListener(UserEvent.NEW_BID, newBidHandler);
			Dispatcher.instance.addEventListener(UserEvent.REMOVE_BID, removeBidHandler);
			Dispatcher.instance.addEventListener(UserEvent.UPDATE_BID, updateBidHandler);
			module.levelup.addEventListener(MouseEvent.CLICK, showOtherWindow);
			module.backpack.addEventListener(MouseEvent.CLICK, showOtherWindow);
			module.shop.addEventListener(MouseEvent.CLICK, showOtherWindow);
			module.multi.addEventListener(MouseEvent.CLICK, showOtherWindow);
			module.exitBid.addEventListener(MouseEvent.CLICK, exitBid);
		}
		
		private function exitBid(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.EXIT_BID));
		}
		
		private function updateBidHandler(e:UserEvent):void 
		{
			var id:int = e.data as int;
			var bid:Bid_asset = bids[id] as Bid_asset;
			var b:Object = _model.bids[id];
			bid.tf.text = b.name + '\t|\t' + b.op + ' ОП' + '\t|\t' + b.curCount + ' / ' + b.count;
		}
		
		private function removeBidHandler(e:UserEvent):void 
		{
			var id:int = e.data as int;
			Debug.out("id = " + id);
			var bid:DisplayObject = bids[id] as DisplayObject;
			(bid as EventDispatcher).removeEventListener(MouseEvent.CLICK, bidClickHandler);
			module.bids.removeChild(bid);
			sortBids();
			bids[id] = null;
		}
		
		private function newBidHandler(e:UserEvent):void 
		{
			var b:Object = _model.bids[e.data as int];
			var bid:Bid_asset = new Bid_asset();
			bid.id = b.id;
			bid.tf.text = b.name + '\t|\t' + b.op + ' ОП' + '\t|\t' + b.curCount + ' / ' + b.count;
			bid.addEventListener(MouseEvent.CLICK, bidClickHandler);
			module.bids.addChild(bid);
			bids[b.id] = bid;
			sortBids();
		}
		
		private function bidClickHandler(e:MouseEvent):void
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.ENTER_BID, e.currentTarget.id));
		}
		
		private function sortBids():void 
		{
			for (var i:int = 0; i < module.bids.numChildren; i++)
			{
				var bid:DisplayObject = module.bids.getChildAt(i);
				bid.y = (bid.height + BID_MARGIN) * i;
			}
		}
		
		private function showOtherWindow(e:MouseEvent):void 
		{
			var window:String;
			if (e.currentTarget.name == "levelup")
				window = MainView.LEVEL_UP_WINDOW;
			else if (e.currentTarget.name == "backpack")
				window = MainView.BACKPACK_WINDOW;
			else if (e.currentTarget.name == "shop")
				window = MainView.SHOP_WINDOW;
			else if (e.currentTarget.name == "multi")
				window = MainView.CREATE_BID_WINDOW;
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