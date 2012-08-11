package control 
{
	import by.blooddy.crypto.MD5;
	import by.blooddy.crypto.serialization.JSON;
	import flash.events.*;
	import flash.net.*;
	import flash.utils.*;
	import model.*;
	import view.common.Debug;
	import view.MainView;

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
			Debug.out("sRemoveBid(" + id + ")");
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.REMOVE_BID, id));
		}
		
		private function sUpdateBid():void 
		{
			var id:int = _socket.readShort();
			var curCount:int = _socket.readByte();
			_model.bids[id].curCount = curCount;
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.UPDATE_BID, id));
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
