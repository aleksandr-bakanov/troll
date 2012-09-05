package view.menu 
{
	import flash.display.Sprite;
	import model.MainModel;
	
	/**
	 * ...
	 * @author bav
	 */
	public class FightWindow extends Sprite 
	{
		public var module:FightWindow_asset;
		private var _model:MainModel;
		
		public function FightWindow(model:MainModel) 
		{
			_model = model;
			module = new FightWindow_asset();
			addChild(module);
		}
		
	}

}