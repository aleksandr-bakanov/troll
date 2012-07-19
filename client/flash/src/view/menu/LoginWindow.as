package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import view.MainView;
	
	/**
	 * Окно логина
	 * @author bav
	 */
	public class LoginWindow extends Sprite 
	{
		public var module:LoginWindow_asset;
		
		public function LoginWindow() 
		{
			module = new LoginWindow_asset();
			addChild(module);
			/// TODO: После успешного коннекта этот слушатель уже не понадобится
			module.goButton.addEventListener(MouseEvent.CLICK, goButtonClick);
			module.registerButton.addEventListener(MouseEvent.CLICK, registerButtonClick);
			module.password.displayAsPassword = true;
			Dispatcher.instance.addEventListener(UserEvent.WRONG_LOGIN, wrongLoginHandler);
		}
		
		private function registerButtonClick(e:MouseEvent):void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.REGISTRATION_WINDOW));
		}
		
		private function wrongLoginHandler(e:UserEvent):void 
		{
			if (!module.goButton.hasEventListener(MouseEvent.CLICK))
				module.goButton.addEventListener(MouseEvent.CLICK, goButtonClick);
		}
		
		private function goButtonClick(e:MouseEvent):void
		{
			if (module.login.text && module.password.text)
			{
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_LOGIN,
					{ login:module.login.text, password:module.password.text } ));
				module.goButton.removeEventListener(MouseEvent.CLICK, goButtonClick);
			}
		}
		
	}

}
