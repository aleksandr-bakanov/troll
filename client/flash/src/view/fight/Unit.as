package view.fight 
{
	import com.greensock.TweenLite;
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
		
		public function Unit() 
		{
			module = new Player_asset();
			addChild(module);
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
		
		private function goNextStep():void
		{
			if (!path.length)
			{
				isMoving = false;
				return;
			}
			var point:Point = path.shift() as Point;
			TweenLite.to(this, FightWindow.STEP_DURATION, { x:point.x * FightWindow.CELL_WIDTH + (point.y % 2 ? FightWindow.CELL_WIDTH / 2 : 0), y:point.y * FightWindow.CELL_HEIGHT * 0.75,
				onComplete:goNextStep } );
		}
		
	}

}