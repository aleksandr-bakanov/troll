package control 
{
	import flash.display.DisplayObjectContainer;
	import model.MainModel;
	import view.common.Debug;
	import view.MainView;
	
	/**
	 * Main application controller.
	 * @author bav
	 */
	public class MainController 
	{
		private var _mainView:MainView;
		private var _mainModel:MainModel;
		private var _connector:Connector;

		public function MainController(host:DisplayObjectContainer) 
		{
			Debug.init(host.stage);
			_mainModel = new MainModel();
			_mainView = new MainView(_mainModel, host);
			_connector = new Connector(_mainModel, host.stage.loaderInfo.parameters.host, host.stage.loaderInfo.parameters.port);
		}
		
	}

}
