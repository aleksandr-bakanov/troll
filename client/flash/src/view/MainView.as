package view 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import flash.events.Event;
	import model.MainModel;
	import view.menu.LoginWindow;
	import view.menu.RegistrationWindow;
	
	/**
	 * Main application view.
	 * @author bav
	 */
	public class MainView extends Sprite 
	{
		public static const LOGIN_WINDOW:String = "login_window";
		public static const REGISTRATION_WINDOW:String = "registration_window";

		private var _model:MainModel;
		private var _windows:Object;
		private var _loginWindow:LoginWindow;
		private var _registrationWindow:RegistrationWindow;

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
			_registrationWindow = new RegistrationWindow();
			_windows[REGISTRATION_WINDOW] = _registrationWindow;
			resizeHandler();
		}
		
	}

}
