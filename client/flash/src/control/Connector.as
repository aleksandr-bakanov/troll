package control 
{
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
			_socket.connect(_host, _port);
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
					if (_socket.bytesAvailable >= 2)
						_lastComSize = _socket.readShort();
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
				default: break;
			}
			_lastComSize = 0;
		}

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

	}

}
