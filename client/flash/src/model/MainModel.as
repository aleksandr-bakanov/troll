package model 
{
	import by.blooddy.crypto.serialization.JSON;
	import control.Dispatcher;
	import control.UserEvent;
	import flash.events.EventDispatcher;
	import view.common.Debug;
	
	/**
	 * Main application model
	 * @author bav
	 */
	public class MainModel extends EventDispatcher 
	{
		public var params:Object;
		private var _oldParams:Object;

		public function MainModel() 
		{
			params = {
				strength:10,
				dexterity:10,
				intellect:10,
				health:10,
				unusedOP:50,
				usedOP:0
			};
			// Это такой зверский способ копирования объекта
			_oldParams = JSON.decode(JSON.encode(params));
			calculateParams();
			configureHandlers();
		}
		
		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.PARAM_CHANGED, paramChanged);
		}
		
		private function paramChanged(e:UserEvent):void 
		{
			var param:String = e.data.param;
			var sign:int = e.data.sign;
			var cost:int = (param == "strength" || param == "health") ? 10 : 20;
			var changed:Boolean = false;
			if (sign > 0 && params.unusedOP >= cost)
			{
				params[param] += 1;
				params.unusedOP -= cost;
				params.usedOP += cost;
				changed = true;
			}
			else if (sign < 0 && _oldParams[param] < params[param])
			{
				params[param] -= 1;
				params.unusedOP += cost;
				params.usedOP -= cost;
				changed = true;
			}
			if (changed)
			{
				calculateParams();
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.PARAM_UPDATED, params));
			}
		}
		
		private function calculateParams():void
		{
			params.speed = (params.dexterity + params.health) / 4.0;
			params.hitPoints = params.health;
			params.deviation = int(params.speed) + 3;
			params.maxLoad = int((params.strength * params.strength) / 5.0);
		}

	}

}
