package control 
{
	import flash.events.Event;
	
	/**
	 * Пользовательские события
	 * @author bav
	 */
	public class UserEvent extends Event 
	{
		public static const SEND_LOGIN:String = "send_login";
		public static const WRONG_LOGIN:String = "wrong_login";
		public static const SHOW_WINDOW:String = "show_window";
		public static const PARAM_CHANGED:String = "param_changed";
		public static const PARAM_UPDATED:String = "param_updated";
		public static const SEND_REGISTER:String = "send_register";
		
		public var data:Object;
		
		public function UserEvent(type:String, data:Object = null, bubbles:Boolean = false, cancelable:Boolean = false) 
		{ 
			super(type, bubbles, cancelable);
			this.data = data;
		} 
		
		public override function clone():Event 
		{ 
			return new UserEvent(type, data, bubbles, cancelable);
		} 
		
		public override function toString():String 
		{ 
			return formatToString("UserEvent", "type", "bubbles", "cancelable", "eventPhase"); 
		}
		
	}
	
}
