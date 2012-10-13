package view.fight 
{
	import com.greensock.TweenLite;
	import flash.display.Graphics;
	import flash.display.Sprite;
	import flash.geom.Point;
	import view.common.Debug;
	import view.menu.FightWindow;
	
	/**
	 * ...
	 * @author bav
	 */
	public class Unit extends Sprite 
	{
		public var module:Player_asset;
		public var path:Array = [];
		public var isMoving:Boolean = false;
		private var _tweenLite:TweenLite;
		
		public function Unit(name:String = "noname") 
		{
			module = new Player_asset();
			module.nameField.text = name;
			mouseChildren = mouseEnabled = false;
			addChild(module);
		}
		
		public function kill():void
		{
			stopMove();
			var g:Graphics = this.graphics;
			g.beginFill(0xFF0000);
			g.drawCircle(0, 0, 20);
			g.endFill();
		}
		
		public function move(path:Array):void
		{
			this.path = this.path.concat(path);
			if (!isMoving)
			{
				isMoving = true;
				goNextStep();
			}
		}
		
		public function stopMove():void
		{
			if (_tweenLite)
				_tweenLite.kill();
			path = [];
			isMoving = false;
		}
		
		private function goNextStep():void
		{
			if (!path.length)
			{
				isMoving = false;
				return;
			}
			var point:Point = path.shift() as Point;
			_tweenLite = TweenLite.to(this, FightWindow.UNIT_STEP_DURATION, { x:point.x * FightWindow.CELL_WIDTH + (point.y % 2 ? FightWindow.CELL_WIDTH / 2 : 0), y:point.y * FightWindow.CELL_HEIGHT * 0.75,
				onComplete:goNextStep } );
		}
		
	}

}