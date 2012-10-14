<?php
	session_start();
	header("Content-Type: text/html; charset=utf-8");
	$host = "localhost";
	$user = "root";
	$password = "1";
	$db = "troll";
	
	if (isset($_REQUEST["login"]) && isset($_REQUEST["password"]))
	{
		if (!mysql_connect($host, $user, $password))
		{
			echo "<h2>MySQL Error.</h2>";
			exit;
		}
		
		mysql_select_db($db);
		
		$log = $_REQUEST["login"];
		// Если длина имени более 16 символов, то уходим
		$loginLen = mb_strlen($log, 'utf-8');
		if ($loginLen < 1 || $loginLen > 16)
		{
			echo "Error on login length ($loginLen)<br>";
			exit;
		}
		$log = mysql_real_escape_string($_REQUEST["login"]);
		$pass = mysql_real_escape_string($_REQUEST["password"]);
		$passMD5 = md5($_REQUEST["password"]);
		$query = "SELECT `is_playing` FROM `user` WHERE `login` = '" . $log . "' AND `password` = '". $passMD5 . "'";
		$q = mysql_query($query);
		if (!$q)
		{
			echo mysql_error();
			exit;
		}
		// Если такого пользователя нет в базе, создадим на него запись
		if (mysql_num_rows($q) == 0)
		{
			// Проверим совпадение имени
			$query = "SELECT `is_playing` FROM `user` WHERE `login` = '" . $log . "'";
			$q = mysql_query($query);
			if (!$q)
			{
				echo mysql_error();
				exit;
			}
			if (mysql_num_rows($q) != 0)
			{
				echo "Этот логин уже занят.";
				exit;
			}
			
			if(isset($_SESSION['captcha_keystring']) && $_SESSION['captcha_keystring'] === $_POST['keystring'])
			{
				
			}
			else
			{
				echo "И про капчу не забудь.";
				exit;
			}
			// Проверка соответствия логина регулярному выражению.
			$matches = array();
			preg_match_all("/[a-zA-Zа-яА-ЯЁё]+[a-zA-Zа-яА-Я0-9Ёё]*/u", $log, $matches, PREG_PATTERN_ORDER);
			$countMathes = count($matches[0]);
			if ($countMathes != 1)
			{
				echo "Error on regexp length.<br>";
				exit;
			}
			// Создаем объект для params
			$params = array();
			$params["strength"] = 10;
			$params["dexterity"] = 10;
			$params["intellect"] = 10;
			$params["health"] = 10;
			$params["usedOP"] = 0;
			$params["unusedOP"] = 50;
			$params["speed"] = ($params["dexterity"] + $params["health"]) / 4.0;
			$params["hitPoints"] = $params["health"];
			$params["deviation"] = (int)($params["speed"]) + 3;
			$params["maxLoad"] = (int)(($params["strength"] * $params["strength"]) / 5.0);
			$params["energy"] = 100;
			$params["handWeapon"] = 0;
			$params["beltWeapon"] = 0;
			$params["armour"] = 0;
			$params["pants"] = 0;
			$params["money"] = 50;
			$params["actPoints"] = (int)($params["speed"]);
			$params["resistance"] = 0;
			$params["perks"] = 0;
			$params["backpack"] = array("1" => 1, "2" => 1, "3" => 1);
			$paramsJSON = json_encode($params);
			$query = "INSERT INTO user (id, login, password, is_playing, params) VALUES (NULL, '$log', '$passMD5', 0, '$paramsJSON')";
			$q = mysql_query($query);
			header("Location: http://troll/game.php?login=$log&password=$passMD5");
		}
		// Если такой пользователь уже есть
		else
		{
			$row = mysql_fetch_assoc($q);
			if ($row["is_playing"] == 1)
				echo "Ты уже где-то играешь.";
			else
			{
				header("Location: http://troll/game.php?login=$log&password=$passMD5");
				exit;
			}
		}
	}
	else
	{
		echo "Если еще нет аккаунта, просто введите логин, пароль и буквы с картинки.<br>";
		echo "Будет создан аккаунт (если такой логин еще не занят) и запустится игра.<br>";
		echo "Если аккаунт у вас уже есть, вводите только логин и пароль.";
		echo "<form action='/index.php' method='post' name='frm'>";
		echo "Логин: <input type='text' name='login'><br>";
		echo "Пароль: <input type='text' name='password'><br>";
		echo "<p><img src=./kcaptcha_create.php?" . session_name() . "=" . session_id() . "></p>";
		echo '<p><input type="text" name="keystring"></p>';
		echo "<input type='submit' value='Go!'>";
		echo "</form>";
	}
?>