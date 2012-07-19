package control 
{
	import by.blooddy.crypto.MD5;
	import flash.events.*;
	import flash.net.*;
	import flash.utils.*;
	import model.*;
	import view.common.Debug;

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
		public static const S_WRONG_LOGIN:int = 3;
		// Client side
		public static const C_LOGIN:int = 2;
		public static const C_REGISTER:int = 4;
		
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
			Dispatcher.instance.addEventListener(UserEvent.SEND_LOGIN, sLogin);
			Dispatcher.instance.addEventListener(UserEvent.SEND_REGISTER, sRegister);
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
					if (_socket.bytesAvailable >= 4)
						_lastComSize = _socket.readInt();
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
				case S_WRONG_LOGIN: sWrongLogin(); break;
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
		
		private function sWrongLogin():void
		{
			var reason:int = _socket.readByte();
			if (reason == 1)
				Debug.out("Неверный логин или пароль.");
			else
				Debug.out("Кто-то уже играет под этим ником.");
			Dispatcher.instance.dispatchEvent(new UserEvent(UserEvent.WRONG_LOGIN));
		}


		//=============================================================
		//
		//	Функции, отправляющие команды клиента
		//
		//=============================================================

		private function sLogin(e:UserEvent):void 
		{
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_LOGIN);
			ba.writeUTF(e.data.login);
			var md5:String = MD5.hash(e.data.password);
			ba.writeUTF(md5);
			flushByteArray(ba);
		}

		private function sRegister(e:UserEvent):void 
		{
			var ba:ByteArray = new ByteArray();
			ba.endian = Endian.LITTLE_ENDIAN;
			ba.writeShort(C_LOGIN);
			ba.writeUTF(e.data.login);
			var md5:String = MD5.hash(e.data.password);
			ba.writeUTF(md5);
			ba.writeByte(_model.params.strength);
			ba.writeByte(_model.params.dexterity);
			ba.writeByte(_model.params.intellect);
			ba.writeByte(_model.params.health);
			flushByteArray(ba);
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
			Debug.out("Close handler");
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
