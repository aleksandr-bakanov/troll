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
		public static const PARAMS_UPDATED:String = "params_updated";
		public static const SEND_REGISTER:String = "send_register";
		public static const SEND_ITEM_INFO_REQUEST:String = "send_item_info_request";
		public static const INIT_BACKPACK:String = "init_backpack";
		public static const WEAR_ITEM:String = "wear_item";
		public static const DROP_ITEM:String = "drop_item";
		public static const SEND_DROP_ITEM:String = "send_drop_item";
		public static const INIT_SHOP:String = "init_shop";
		public static const SELL_ITEM:String = "sell_item";
		public static const SEND_SELL_ITEM:String = "send_sell_item";
		public static const SEND_BUY_ITEM:String = "send_buy_item";
		public static const ADD_ITEM:String = "add_item";
		public static const SEND_ADD_STAT:String = "send_add_stat";
		public static const CREATE_BID:String = "create_bid";
		public static const NEW_BID:String = "new_bid";
		public static const REMOVE_BID:String = "remove_bid";
		public static const UPDATE_BID:String = "update_bid";
		public static const EXIT_BID:String = "exit_bid";
		public static const ENTER_BID:String = "enter_bid";
		public static const START_FIGHT:String = "start_fight";
		public static const AREA_OPEN:String = "area_open";
		public static const KEYS_OPEN:String = "keys_open";
		public static const S_CHAT_MESSAGE:String = "s_chat_message";
		public static const C_CHAT_MESSAGE:String = "c_chat_message";
		public static const C_WANT_MOVE:String = "c_want_move";
		public static const C_ACTION:String = "c_action";
		public static const MOVE_UNIT:String = "move_unit";
		
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
