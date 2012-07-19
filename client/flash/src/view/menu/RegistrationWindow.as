package view.menu 
{
	import control.Dispatcher;
	import control.UserEvent;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	
	/**
	 * ...
	 * @author bav
	 */
	public class RegistrationWindow extends Sprite 
	{
		public var module:RegistrationWindow_asset;
		
		public function RegistrationWindow() 
		{
			module = new RegistrationWindow_asset();
			addChild(module);
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			var names:Array = ["minus_strength", "plus_strength", "minus_dexterity", "plus_dexterity",
				"minus_intellect", "plus_intellect", "minus_health", "plus_health"];
			for (var i:int = 0; i < names.length; i++)
				module.getChildByName(names[i]).addEventListener(MouseEvent.CLICK, paramChange);
			Dispatcher.instance.addEventListener(UserEvent.PARAM_UPDATED, paramUpdated);
			module.register.addEventListener(MouseEvent.CLICK, registerClickHandler);
		}
		
		private function registerClickHandler(e:MouseEvent):void 
		{
			if (module.login.text && module.password1.text && module.password2.text &&
				module.login.text.length <= 16 && module.password1.length <= 16 &&
				module.password1.text == module.password2.text)
			{
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SEND_REGISTER,
					{ login:module.login.text, password:module.password1.text } ));
				module.register.removeEventListener(MouseEvent.CLICK, registerClickHandler);
			}
		}
		
		private function paramUpdated(e:UserEvent):void 
		{
			module.rest.text = e.data.unusedOP.toString();
			module.strength.text = e.data.strength.toString();
			module.dexterity.text = e.data.dexterity.toString();
			module.intellect.text = e.data.intellect.toString();
			module.health.text = e.data.health.toString();
			module.speed.text = e.data.speed.toFixed(1);
			module.hitPoints.text = e.data.hitPoints.toString();
			module.deviation.text = e.data.deviation.toString();
			module.maxLoad.text = e.data.maxLoad.toString();
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
