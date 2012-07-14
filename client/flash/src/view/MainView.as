package view 
{
	import flash.display.DisplayObjectContainer;
	import flash.display.Sprite;
	import model.MainModel;
	
	/**
	 * Main application view.
	 * @author bav
	 */
	public class MainView extends Sprite 
	{
		private var _model:MainModel;

		public function MainView(model:MainModel, host:DisplayObjectContainer) 
		{
			_model = model;
			host.addChild(this);
		}
		
	}

}
