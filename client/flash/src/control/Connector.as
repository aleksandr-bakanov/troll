package control 
{
	import by.blooddy.crypto.MD5;
	import by.blooddy.crypto.serialization.JSON;
	import flash.events.*;
	import flash.geom.Point;
	import flash.net.*;
	import flash.utils.*;
	import model.*;
	import view.common.Debug;
	import view.MainView;
	import view.menu.FightWindow;

	/**
	 * Connector. It sends and receives the commands
	 * between client and server.
	 * @author bav
	 */
	public class Connector extends EventDispatcher 
	{
		// Константы команд
		// Server side
		public static const S_TRACE:int = 1;
		public static const S_LOGIN_FAILURE:int = 3;
		public static const S_REGISTER_SUCCESS:int = 5;
		public static const S_REGISTER_FAILURE:int = 7;
		public static const S_LOGIN_SUCCESS:int = 9;
		public static const S_FULL_PARAMS:int = 11;
		public static const S_ITEM_INFO:int = 13;
		public static const S_SHOP_ITEMS:int = 15;
		public static const S_ADD_ITEM:int = 17;
		public static const S_CLIENT_MONEY:int = 19;
		public static const S_NEW_BID:int = 21;
		public static const S_REMOVE_BID:int = 23;
		public static const S_UPDATE_BID:int = 25;
		public static const S_START_FIGHT_INFO:int = 27;
		public static const S_AREA_OPEN:int = 29;
		public static const S_KEYS_OPEN:int = 31;
		public static const S_CHAT_MESSAGE:int = 33;
		public static const S_FINISH_FIGHT:int = 35;
		public static const S_YOUR_MOVE:int = 37;
		public static const S_MOVE_UNIT:int = 39;
		public static const S_UNIT_CHANGE_WEAPON:int = 41;
		public static const S_UNIT_ATTACK:int = 43;
		public static const S_UNIT_DAMAGE:int = 45;
		public static const S_UNIT_ACTION:int = 47;
		public static const S_CHANGE_CELL:int = 49;
		public static const S_TELEPORT_UNIT:int = 51;

		// Client side
		public static const C_LOGIN:int = 2;
		public static const C_REGISTER:int = 4;
		public static const C_ITEM_INFO:int = 6;
		public static const C_WEAR_ITEM:int = 8;
		public static const C_DROP_ITEM:int = 10;
		public static const C_BUY_ITEM:int = 12;
		public static const C_SELL_ITEM:int = 14;
		public static const C_ADD_STAT:int = 16;
		public static const C_ENTER_BID:int = 18;
		public static const C_EXIT_BID:int = 20;
		public static const C_CREATE_BID:int = 22;
		public static const C_CHAT_MESSAGE:int = 24;
		public static const C_WANT_MOVE:int = 26;
		public static const C_CHANGE_WEAPON:int = 28;
		public static const C_ATTACK:int = 30;
		public static const C_ACTION:int = 32;
		
		private var _socket:Socket;
		private var _lastComSize:int;
		private var _model:MainModel;
		private var _host:String;
		private var _port:int;

		public function Connector(model:MainModel, host:String, port:int) 
		{
			_host = host;
			_port = port;
			_model = model;
			_lastComSize = 0;
			configureHandlers();
			configureSocket();
		}

		private function configureHandlers():void 
		{
			Dispatcher.instance.addEventListener(UserEvent.SEND_LOGIN, cLogin);
			Dispatcher.instance.addEventListener(UserEvent.SEND_REGISTER, cRegister);
			Dispatcher.instance.addEventListener(UserEvent.SEND_ITEM_INFO_REQUEST, cItemInfo);
			Dispatcher.instance.addEventListener(UserEvent.WEAR_ITEM, cWearItem);
			Dispatcher.instance.addEventListener(UserEvent.SEND_DROP_ITEM, cDropItem);
			Dispatcher.instance.addEventListener(UserEvent.SEND_SELL_ITEM, cSellItem);
			Dispatcher.instance.addEventListener(UserEvent.SEND_BUY_ITEM, cBuyItem);
			Dispatcher.instance.addEventListener(UserEvent.SEND_ADD_STAT, cAddStat);
			Dispatcher.instance.addEventListener(UserEvent.CREATE_BID, cCreateBid);
			Dispatcher.instance.addEventListener(UserEvent.EXIT_BID, cExitBid);
			Dispatcher.instance.addEventListener(UserEvent.ENTER_BID, cEnterBid);
			Dispatcher.instance.addEventListener(UserEvent.C_CHAT_MESSAGE, cChatMessage);
			Dispatcher.instance.addEventListener(UserEvent.C_WANT_MOVE, cWantMove);
			Dispatcher.instance.addEventListener(UserEvent.C_ACTION, cAction);
			Dispatcher.instance.addEventListener(UserEvent.CHANGE_WEAPON, cChangeWeapon);
			Dispatcher.instance.addEventListener(UserEvent.C_WANT_ATTACK, cAttack);
		}
		
		private function configureSocket():void
		{
			_socket = new Socket();
			_socket.endian = Endian.LITTLE_ENDIAN;
			_socket.addEventListener(Event.CONNECT, connectHandler);
			_socket.addEventListener(Event.CLOSE, closeHandler);
			_socket.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
			_socket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, securityErrorHandler);
			_socket.addEventListener(ProgressEvent.SOCKET_DATA, socketDataHandler);
		}
		
		public function connect():void
		{
			_socket.connect("localhost", 15856);
			//_socket.connect(_host, _port);
		}

		private function socketDataHandler(e:ProgressEvent):void 
		{
			// Пришли данные, рассматриваем три варианта:
			while (_socket.bytesAvailable)
			{
				// Вариант №1: мы ждали новый пакет, о чем свидетельствует
				// то, что нам не известен размер текущего (последнего)
				// пакета.
				if (!_lastComSize)
				{
					// Читаем размер в том случае если можем его прочитать.
					if (_socket.bytesAvailable >= 4) {
						_lastComSize = _socket.readInt();
					}
					// Если не можем, уходим из цикла и из функции,
					// до прихода следующих данных.
					else
						break;
					// Здесь оказываемся если длина пакета успешно считана.
					// Если нам повезло и пакет пришел целиком...
					if (_socket.bytesAvailable >= _lastComSize)
					{
						// ...парсим его. В конце функции parse() переменная
						// _lastComSize выставляется в ноль, что свидетельствует
						// об окончании парсинга одного пакета.
						parse();
						// После этого парсинга или того, что будет в Варианте №2,
						// благодаря циклу while, попытка обработки пришедших
						// данных запустится еще раз. На случай если нам
						// за один раз пришло более одного пакета.
					}
				}
				// Вариант №2: мы ждали окончания пакета, начало которого было
				// в одном из предыдущих вызовов функции socketDataHandler().
				// Если на этот раз байт пришло достаточно, начинаем парсить.
				else if (_socket.bytesAvailable >= _lastComSize)
				{
					parse();
				}
				// Вариант №3: мы также как и во втором варианте дожидаемся
				// окончания пакета, но даже с этой пачкой данных он все равно
				// пришел не полностью. В таком случае просто выходим из функции
				// и ждем еще байтов.
				else
					break;
			}
		}

		private function parse():void
		{
			var comId:int = _socket.readShort();
			switch(comId)
			{
				case S_TRACE: sTrace(); break;
				case S_LOGIN_FAILURE: sLoginFailure(); break;
				case S_REGISTER_SUCCESS: sRegisterSuccess(); break;
				case S_REGISTER_FAILURE: sRegisterFailure(); break;
				case S_LOGIN_SUCCESS: sLoginSuccess(); break;
				case S_FULL_PARAMS: sFullParams(); break;
				case S_ITEM_INFO: sItemInfo(); break;
				case S_SHOP_ITEMS: sShopItems(); break;
				case S_CLIENT_MONEY: sClientMoney(); break;
				case S_ADD_ITEM: sAddItem(); break;
				case S_NEW_BID: sNewBid(); break;
				case S_REMOVE_BID: sRemoveBid(); break;
				case S_UPDATE_BID: sUpdateBid(); break;
				case S_START_FIGHT_INFO: sStartFightInfo(); break;
				case S_AREA_OPEN: sAreaOpen(); break;
				case S_KEYS_OPEN: sKeysOpen(); break;
				case S_CHAT_MESSAGE: sChatMessage(); break;
				case S_MOVE_UNIT: sMoveUnit(); break;
				case S_CHANGE_CELL: sChangeCell(); break;
				case S_TELEPORT_UNIT: sTeleportUnit(); break;
				case S_YOUR_MOVE: sYourMove(); break;
				case S_UNIT_DAMAGE: sUnitDamage(); break;
				default: break;
			}
			_lastComSize = 0;
		}
		
		//=============================================================
		//
		//	Функции-обработчики серверных команд
		//
		//=============================================================
		
		private function sTrace():void
		{
			Debug.out(_socket.readUTF());
		}
		
		private function sLoginFailure():void
		{
			var reason:int = _socket.readByte();
			if (reason == 1)
				Debug.out("Неверный логин или пароль.");
			else
				Debug.out("Кто-то уже играет под этим ником.");
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.WRONG_LOGIN));
		}
		
		private function sRegisterSuccess():void 
		{
			Debug.out("Регистрация успешно завершена.");
		}
		
		private function sRegisterFailure():void 
		{
			var reason:int = _socket.readByte();
			if (reason == 1)
				Debug.out("Логин уже занят.");
			else
				Debug.out("Логин не прошел проверки регулярным выражением.");
		}
		
		private function sLoginSuccess():void 
		{
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.MAIN_WINDOW));
		}
		
		private function sFullParams():void 
		{
			_model.id = _socket.readInt();
			_model.name = _socket.readUTF();
			_model.params = JSON.decode(_socket.readUTF());
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.PARAMS_UPDATED, _model.params));
			// Инициализируем инвентарь
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.INIT_BACKPACK, _model.params.backpack));
		}
		
		private function sItemInfo():void 
		{
			var id:int = _socket.readShort();
			var json:String = _socket.readUTF();
			MainModel.items[String(id)] = JSON.decode(json);
		}
		
		private function sShopItems():void 
		{
			var data:Object = JSON.decode(_socket.readUTF());
			for (var id:String in data)
				MainModel.items[id] = JSON.decode(data[id]);
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.INIT_SHOP));
		}
		
		private function sClientMoney():void 
		{
			_model.params.money = _socket.readInt();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.PARAMS_UPDATED, _model.params));
		}
		
		private function sAddItem():void 
		{
			var id:int = _socket.readShort();
			var count:int = _socket.readByte();
			var idStr:String = String(id);
			if (_model.params.backpack[idStr])
				_model.params.backpack[idStr].count += count;
			else
			{
				_model.params.backpack[idStr] = MainModel.items[idStr];
				_model.params.backpack[idStr].count = count;
				_model.params.backpack[idStr].weared = 0;
			}
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.ADD_ITEM, id));
		}
		
		private function sNewBid():void 
		{
			var id:int = _socket.readShort();
			var op:int = _socket.readShort();
			var count:int = _socket.readByte();
			var curCount:int = _socket.readByte();
			var name:String = _socket.readUTF();
			_model.bids[id] = { id:id, op:op, count:count, curCount:curCount, name:name };
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.NEW_BID, id));
		}
		
		private function sRemoveBid():void 
		{
			var id:int = _socket.readShort();
			_model.bids[id] = null;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.REMOVE_BID, id));
		}
		
		private function sUpdateBid():void 
		{
			var id:int = _socket.readShort();
			var curCount:int = _socket.readByte();
			_model.bids[id].curCount = curCount;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.UPDATE_BID, id));
		}
		
		private function sStartFightInfo():void
		{
			_model.fInfo = { };
			var playersCount:int = _socket.readByte();
			_model.fInfo.players = { };
			var i:int;
			for (i = 0; i < playersCount; i++)
			{
				var id:int = _socket.readByte();
				if (id >= 0)
				{
					var o:Object = { };
					o.floorId = _socket.readByte();
					o.x = _socket.readShort();
					o.y = _socket.readShort();
					_model.fInfo.players[id] = o;
				}
			}
			_model.fInfo.moveOrder = [];
			for (i = 0; i < playersCount; i++)
				_model.fInfo.moveOrder.push(_socket.readByte());
			_model.fInfo.selfId = _socket.readByte();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.SHOW_WINDOW, MainView.FIGHT_WINDOW));
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.START_FIGHT));
		}
		
		private function sAreaOpen():void 
		{
			var cells:Object = { };
			var floorsCount:int = _socket.readByte();
			for (var i:int = 0; i < floorsCount; i++)
			{
				var floorId:int = _socket.readByte();
				if (!cells[floorId])
					cells[floorId] = [];
				var cellsCount:int = _socket.readShort();
				for (var j:int = 0; j < cellsCount; j++)
				{
					var cell:Object = { };
					cell.x = _socket.readShort();
					cell.y = _socket.readShort();
					cell.type = _socket.readByte();
					if (cell.type == FightWindow.CT_FLOOR)
					{
						cell.toFloor = _socket.readByte();
						if (cell.toFloor >= 0)
						{
							cell.toX = _socket.readShort();
							cell.toY = _socket.readShort();
						}
					}
					else if (cell.type == FightWindow.CT_WALL)
					{
						cell.hp = _socket.readByte();
						cell.key = _socket.readShort();
					}
					else if (cell.type == FightWindow.CT_DOOR)
					{
						var lockCount:int = _socket.readShort();
						if (lockCount)
						{
							cell.keys = [];
							for (var k:int = 0; k < lockCount; k++)
								cell.keys.push(_socket.readShort());
						}
					}
					cells[floorId].push(cell);
				}
			}
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.AREA_OPEN, cells));
		}
		
		// Сейчас функционал данной команды перенесен в S_AREA_OPEN
		// Возможно вдальнейшем функционал будет снова разведен для уменьшения трафика.
		private function sKeysOpen():void 
		{
			var cells:Object = { };
			var floorsCount:int = _socket.readByte();
			for (var i:int = 0; i < floorsCount; i++)
			{
				var floorId:int = _socket.readByte();
				if (!cells[floorId])
					cells[floorId] = [];
				var cellsCount:int = _socket.readShort();
				for (var j:int = 0; j < cellsCount; j++)
				{
					var cell:Object = { };
					cell.id = _socket.readShort();
					cell.x = _socket.readShort();
					cell.y = _socket.readShort();
					cells[floorId].push(cell);
				}
			}
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.KEYS_OPEN, cells));
		}
		
		private function sChatMessage():void 
		{
			var mes:String = _socket.readUTF();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.S_CHAT_MESSAGE, mes));
		}
		
		private function sMoveUnit():void 
		{
			var id:int = _socket.readByte();
			var steps:int = _socket.readByte();
			var path:Array = [];
			for (var i:int = 0; i < steps; i++)
			{
				var x:int = _socket.readShort();
				var y:int = _socket.readShort();
				path.push(new Point(x, y));
			}
			if (path.length)
				Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.MOVE_UNIT, { id:id, path:path } ));
		}
		
		private function sChangeCell():void 
		{
			var floor:int = _socket.readByte();
			var x:int = _socket.readShort();
			var y:int = _socket.readShort();
			var type:int = _socket.readByte();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.CHANGE_CELL, { floor:floor, x:x, y:y, type:type } ));
		}
		
		private function sTeleportUnit():void 
		{
			var unitId:int = _socket.readByte();
			var floor:int = _socket.readByte();
			var x:int = _socket.readShort();
			var y:int = _socket.readShort();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.TELEPORT_UNIT, { unitId:unitId, floor:floor, x:x, y:y } ));
		}
		
		private function sYourMove():void 
		{
			var unitId:int = _socket.readByte();
			var seconds:int = _socket.readByte();
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.YOUR_MOVE, { unitId:unitId, seconds:seconds } ));
		}
		
		private function sUnitDamage():void 
		{
			var unitId:int = _socket.readByte();
			if (unitId < 0)
			{
				var floor:int = _socket.readByte();
				var x:int = _socket.readShort();
				var y:int = _socket.readShort();
			}
			var damage:int = _socket.readByte();
			Debug.out("unitId = " + unitId + "; damage = " + damage);
		}


		//=============================================================
		//
		//	Функции, отправляющие команды клиента
		//
		//=============================================================

		private function cLogin(e:UserEvent):void 
		{
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_LOGIN);
			ba.writeUTF(e.data.login);
			var md5:String = MD5.hash(e.data.password);
			ba.writeUTF(md5);
			flushByteArray(ba);
		}

		private function cRegister(e:UserEvent):void 
		{
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_REGISTER);
			ba.writeUTF(e.data.login);
			var md5:String = MD5.hash(e.data.password);
			ba.writeUTF(md5);
			ba.writeByte(_model.params.strength);
			ba.writeByte(_model.params.dexterity);
			ba.writeByte(_model.params.intellect);
			ba.writeByte(_model.params.health);
			flushByteArray(ba);
		}
		
		private function cItemInfo(e:UserEvent):void 
		{
			_socket.writeInt(4);
			_socket.writeShort(C_ITEM_INFO);
			_socket.writeShort(e.data as int);
			_socket.flush();
		}
		
		private function cWearItem(e:UserEvent):void 
		{
			_socket.writeInt(6);
			_socket.writeShort(C_WEAR_ITEM);
			_socket.writeShort(e.data.id);
			_socket.writeBoolean(e.data.wear);
			_socket.writeByte(e.data.place);
			_socket.flush();
		}
		
		private function cDropItem(e:UserEvent):void 
		{
			_socket.writeInt(5);
			_socket.writeShort(C_DROP_ITEM);
			_socket.writeShort(e.data.id);
			_socket.writeByte(e.data.place);
			_socket.flush();
		}
		
		private function cSellItem(e:UserEvent):void 
		{
			_socket.writeInt(4);
			_socket.writeShort(C_SELL_ITEM);
			_socket.writeShort(e.data as int);
			_socket.flush();
		}
		
		private function cBuyItem(e:UserEvent):void 
		{
			_socket.writeInt(4);
			_socket.writeShort(C_BUY_ITEM);
			_socket.writeShort(e.data as int);
			_socket.flush();
		}
		
		private function cAddStat(e:UserEvent):void 
		{
			_socket.writeInt(3);
			_socket.writeShort(C_ADD_STAT);
			_socket.writeByte(e.data as int);
			_socket.flush();
		}
		
		private function cCreateBid(e:UserEvent):void 
		{
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_CREATE_BID);
			ba.writeByte(e.data.count as int);
			ba.writeUTF(e.data.name as String);
			flushByteArray(ba);
		}
		
		private function cExitBid(e:UserEvent):void 
		{
			_socket.writeInt(2);
			_socket.writeShort(C_EXIT_BID);
			_socket.flush();
		}
		
		private function cEnterBid(e:UserEvent):void 
		{
			_socket.writeInt(4);
			_socket.writeShort(C_ENTER_BID);
			_socket.writeShort(e.data as int);
			_socket.flush();
		}
		
		private function cChatMessage(e:UserEvent):void 
		{
			var mes:String = e.data as String;
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_CHAT_MESSAGE);
			ba.writeUTF(mes);
			_socket.writeInt(ba.length);
			_socket.writeBytes(ba);
			_socket.flush();
		}
		
		private function cWantMove(e:UserEvent):void 
		{
			var point:Point = e.data as Point;
			_socket.writeInt(6);
			_socket.writeShort(C_WANT_MOVE);
			_socket.writeShort(point.x);
			_socket.writeShort(point.y);
			_socket.flush();
		}
		
		private function cAction(e:UserEvent):void 
		{
			var point:Point = e.data as Point;
			_socket.writeInt(6);
			_socket.writeShort(C_ACTION);
			_socket.writeShort(point.x);
			_socket.writeShort(point.y);
			_socket.flush();
		}
		
		private function cChangeWeapon(e:UserEvent):void 
		{
			_socket.writeInt(2);
			_socket.writeShort(C_CHANGE_WEAPON);
			_socket.flush();
		}
		
		private function cAttack(e:UserEvent):void 
		{
			var point:Point = e.data as Point;
			_socket.writeInt(6);
			_socket.writeShort(C_ATTACK);
			_socket.writeShort(point.x);
			_socket.writeShort(point.y);
			_socket.flush();
		}

		//=============================================================
		//
		//	Обработчики разнообразных событий сокета
		//
		//=============================================================
		
		private function securityErrorHandler(e:SecurityErrorEvent):void 
		{
			Debug.out(e.toString());
		}

		private function ioErrorHandler(e:IOErrorEvent):void 
		{
			Debug.out(e.toString());
		}

		private function closeHandler(e:Event):void 
		{
			Debug.out("Connection closed.");
		}

		private function connectHandler(e:Event):void 
		{
			Debug.out("Connection established.");
		}
		
		//=============================================================
		//
		//	Util functions
		//
		//=============================================================
		
		private function flushByteArray(ba:ByteArray):void
		{
			_socket.writeInt(ba.length);
			_socket.writeBytes(ba);
			_socket.flush();
		}

	}

}
