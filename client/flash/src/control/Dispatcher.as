package control 
{
	import flash.events.EventDispatcher;
	
	/**
	 * Singletone for dispatching different events.
	 * @author bav
	 */
	public class Dispatcher extends EventDispatcher 
	{
		public static const instance:Dispatcher = new Dispatcher();
		public function Dispatcher() 
		{
			
		}
		
	}

}
