package view 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.events.Event;
	import model.MainModel;
	import view.menu.BackpackWindow;
	import view.menu.CreateBidWindow;
	import view.menu.FightWindow;
	import view.menu.LevelUpWindow;
	import view.menu.LoginWindow;
	import view.menu.MainWindow;
	import view.menu.RegistrationWindow;
	import view.menu.ShopWindow;
	
	/**
	 * Main application view.
	 * @author bav
	 */
	public class MainView extends Sprite 
	{
		public static const LOGIN_WINDOW:String = "login_window";
		public static const REGISTRATION_WINDOW:String = "registration_window";
		public static const MAIN_WINDOW:String = "main_window";
		public static const LEVEL_UP_WINDOW:String = "level_up_window";
		public static const BACKPACK_WINDOW:String = "backpack_window";
		public static const SHOP_WINDOW:String = "shop_window";
		public static const CREATE_BID_WINDOW:String = "create_bid_window";
		public static const FIGHT_WINDOW:String = "fight_window";

		private var _model:MainModel;
		private var _windows:Object;
		private var _loginWindow:LoginWindow;
		private var _registrationWindow:RegistrationWindow;
		private var _mainWindow:MainWindow;
		private var _leveUpWindow:LevelUpWindow;
		private var _backpackWindow:BackpackWindow;
		private var _shopWindow:ShopWindow;
		private var _createBidWindow:CreateBidWindow;
		private var _fightWindow:FightWindow;

		public function MainView(model:MainModel, host:DisplayObjectContainer) 
		{
			_model = model;
			host.addChild(this);
			host.stage.addEventListener(Event.RESIZE, resizeHandler);
			initView();
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.SHOW_WINDOW, showWindowHandler);
		}
		
		private function showWindowHandler(e:UserEvent):void 
		{
			hideAllWindows();
			addChild(_windows[e.data]);
		}
		
		private function hideAllWindows():void
		{
			while (numChildren)
				removeChildAt(0);
		}
		
		private function resizeHandler(e:Event = null):void 
		{
			for (var window:String in _windows)
			{
				_windows[window].x = (stage.stageWidth - _windows[window].width) / 2;
				_windows[window].y = (stage.stageHeight - _windows[window].height) / 2;
			}
		}
		
		private function initView():void
		{
			_windows = { };
			_loginWindow = new LoginWindow();
			_windows[LOGIN_WINDOW] = _loginWindow;
			addChild(_loginWindow);
			_registrationWindow = new RegistrationWindow(_model);
			_windows[REGISTRATION_WINDOW] = _registrationWindow;
			_mainWindow = new MainWindow(_model);
			_windows[MAIN_WINDOW] = _mainWindow;
			_leveUpWindow = new LevelUpWindow();
			_windows[LEVEL_UP_WINDOW] = _leveUpWindow;
			_backpackWindow = new BackpackWindow(_model);
			_windows[BACKPACK_WINDOW] = _backpackWindow;
			_shopWindow = new ShopWindow(_model);
			_windows[SHOP_WINDOW] = _shopWindow;
			_createBidWindow = new CreateBidWindow();
			_windows[CREATE_BID_WINDOW] = _createBidWindow;
			_fightWindow = new FightWindow();
			_windows[FIGHT_WINDOW] = _fightWindow;
			resizeHandler();
		}
		
		public function get backpackWindow():BackpackWindow 
		{
			return _backpackWindow;
		}
		
		public function get shopWindow():ShopWindow 
		{
			return _shopWindow;
		}
		
	}

}
