<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8"/>
	<title>TrollControl</title>
	<meta name="description" content="" />
	
	<script src="js/swfobject.js"></script>
	<script>
		var flashvars = {
			host: 'localhost',
			port: 15856<?php
				if (isset($_REQUEST["login"]) && isset($_REQUEST["password"]))
				{
					$log = $_REQUEST["login"];
					$pas = $_REQUEST["password"];
					echo ",\n\t\t\tlogin: '$log',\n";
					echo "\t\t\tpassword: '$pas'\n";
				}?>
		};
		var params = {
			menu: "false",
			scale: "noScale",
			allowFullscreen: "true",
			allowScriptAccess: "always",
			bgcolor: "",
			wmode: "direct" // can cause issues with FP settings & webcam
		};
		var attributes = {
			id:"TrollControl"
		};
		swfobject.embedSWF(
			"TrollControl.swf", 
			"altContent", "100%", "100%", "10.0.0", 
			"expressInstall.swf", 
			flashvars, params, attributes);
	</script>
	<style>
		html, body { height:100%; overflow:hidden; }
		body { margin:0; }
	</style>
</head>
<body>
	<div id="altContent">
		<h1>TrollControl</h1>
		<p><a href="http://www.adobe.com/go/getflashplayer">Get Adobe Flash player</a></p>
	</div>
</body>
</html>
