package view.common 
{
	import flash.display.DisplayObjectContainer;
	import flash.display.Graphics;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import flash.text.TextFormat;
	
	/**
	 * Debug window. Call Debug.init(host) first.
	 * Than trace debug messages by calling Debug.out(message)
	 * @author bav
	 */
	public class Debug extends Sprite 
	{
		private static var _out:TextField;
		private static var _host:DisplayObjectContainer;
		private static var _btn:Sprite;
		private static var _back:Sprite;
		private static const MARGIN:int = 0;
		
		public function Debug() 
		{
			
		}
		
		public static function init(host:DisplayObjectContainer):void
		{
			if (_out)
				return;
			_host = host;
			_out = new TextField();
			_out.background = false;
			_out.defaultTextFormat = new TextFormat("_typewriter", 12, 0xEDEDED);
			_out.wordWrap = true;
			_out.x = _out.y = MARGIN;
			_out.width = _host.stage.stageWidth - MARGIN * 2;
			_out.height = _host.stage.stageHeight - MARGIN * 2;
			
			_btn = new Sprite();
			var g:Graphics = _btn.graphics;
			g.beginFill(0xED3333);
			g.drawRect( -20, -20, 20, 20);
			g.endFill();
			_btn.addEventListener(MouseEvent.CLICK, btnClickHandler);
			_btn.x = _out.x + _out.width;
			_btn.y = _out.y + _out.height;
			
			_back = new Sprite();
			g = _back.graphics;
			g.beginFill(0, 0.8);
			g.drawRect(0, 0, _out.width, _out.height);
			g.endFill();
			_back.x = _out.x;
			_back.y = _out.y;
			
			_out.visible = _back.visible = false;
			
			_host.addChild(_back);
			_host.addChild(_out);
			_host.addChild(_btn);
			_host.stage.addEventListener(Event.RESIZE, resizeHandler);
		}
		
		private static function resizeHandler(e:Event):void 
		{
			_back.width = _out.width = _host.stage.stageWidth - MARGIN * 2;
			_back.height = _out.height = _host.stage.stageHeight - MARGIN * 2;
			_btn.x = _out.x + _out.width;
			_btn.y = _out.y + _out.height;
		}
		
		public static function out(mes:Object):void
		{
			if (!_out)
				return;
			_out.appendText(String(mes) + "\n");
			_out.scrollV = _out.maxScrollV;
			_host.addChild(_back);
			_host.addChild(_out);
			_host.addChild(_btn);
		}
		
		private static function btnClickHandler(e:MouseEvent):void 
		{
			_out.visible = _back.visible = !_out.visible;
		}
		
	}

}
