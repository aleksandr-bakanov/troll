package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import model.MainModel;
	
	/**
	 * Окно создания аккаунта
	 * @author bav
	 */
	public class RegistrationWindow extends Sprite 
	{
		public static const LOGIN_REGEXP:RegExp = /[a-zA-Zа-яА-ЯЁё]+[a-zA-Zа-яА-Я0-9Ёё]*/;
		public var module:RegistrationWindow_asset;
		private var _model:MainModel;
		
		public function RegistrationWindow(model:MainModel) 
		{
			_model = model;
			module = new RegistrationWindow_asset();
			module.login.restrict = "0-9a-zA-Zа-яА-ЯЁё";
			addChild(module);
			configureHandlers();
			paramsUpdated();
		}
		
		private function configureHandlers():void 
		{
			var names:Array = ["minus_strength", "plus_strength", "minus_dexterity", "plus_dexterity",
				"minus_intellect", "plus_intellect", "minus_health", "plus_health"];
			for (var i:int = 0; i < names.length; i++)
				module.getChildByName(names[i]).addEventListener(MouseEvent.CLICK, paramChange);
			Dispatcher.instance.addEventListener(UserEvent.PARAMS_UPDATED, paramsUpdated);
			module.register.addEventListener(MouseEvent.CLICK, registerClickHandler);
		}
		
		private function registerClickHandler(e:MouseEvent):void 
		{
			var match:Array = module.login.text.match(LOGIN_REGEXP);
			if (!match.length || match[0].length != module.login.text.length)
				return;
			if (module.password1.text && module.password2.text &&
				module.login.text.length <= 16 && module.password1.length <= 16 &&
				module.password1.text == module.password2.text)
			{
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_REGISTER,
					{ login:module.login.text, password:module.password1.text } ));
				module.register.removeEventListener(MouseEvent.CLICK, registerClickHandler);
			}
		}
		
		private function paramsUpdated(e:UserEvent = null):void 
		{
			module.rest.text = _model.params.unusedOP.toString();
			module.strength.text = _model.params.strength.toString();
			module.dexterity.text = _model.params.dexterity.toString();
			module.intellect.text = _model.params.intellect.toString();
			module.health.text = _model.params.health.toString();
			module.speed.text = _model.params.speed.toFixed(1);
			module.hitPoints.text = _model.params.hitPoints.toString();
			module.deviation.text = _model.params.deviation.toString();
			module.maxLoad.text = _model.params.maxLoad.toString();
		}
		
		private function paramChange(e:MouseEvent):void 
		{
			var n:String = e.currentTarget.name;
			var sign:int = n.indexOf("plus") == 0 ? 1 : -1;
			var param:String = n.split("_")[1];
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.PARAM_CHANGED, { param:param, sign:sign } ));
		}
		
	}

}
