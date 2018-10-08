# PythonXatBot

A Xat bot in Python that does not require the (bot) power.

## Requirements
python 2.7

## How to use

1. open the file bot.py and edit these variables: botID, botK1, botK2 to your bot settings (you can generate these parameters on [https://xat.com/web_gear/chat/auser3.php](https://xat.com/web_gear/chat/auser3.php)

2. (optional) edit the botDisplayName, botAvatar and botHomepage

3. open the file ```chatNames.txt``` and edit the name of the xats you want your bot to join ( one per line)


## Update (2018-10-07)

I will deprecate the API for getting Xat chat's info _very_ soon. I have long since considered Xat to be dead, but I kept the API up in hope that Xat would eventually make changes. [They didn't](https://trends.google.com/trends/explore?date=today%205-y&q=Xat,Discord) - [Xat still uses Flash](https://trends.google.com/trends/explore?date=all&geo=US&q=Adobe%20Flash)


Here's a quick Java implementation, if somebody wants to make their own API:

```java
	private List<Integer> chatPorts = List.of(10007, 10008, 10019, 10038);
	private List<String> chatIps = List.of(
		"fwdelb00-1964376362.us-east-1.elb.amazonaws.com", "fwdelb01-1365137239.us-east-1.elb.amazonaws.com",
		"fwdelb02-53956973.us-east-1.elb.amazonaws.com", "fwdelb03-1789285345.us-east-1.elb.amazonaws.com"
	);
	
	
	public String generateXatData(String chatName) throws IOException {
		return chatName + ":" + getXatChatId(chatName) + ":" + getRandomXatChatIP() + ":" + getRandomXatChatPort();
	}
	
	
	private String getRandomXatChatIP() {
		return chatIps.get((int)(Math.ceil(Math.random() * (chatIps.size())))-1);
	}
	
	
	private Integer getRandomXatChatPort() {
		return chatPorts.get((int)(Math.ceil(Math.random() * (chatPorts.size())))-1);
	}
	
	
	public String getXatChatId(String chatName) throws IOException {
		String chatId = "";
		URL siteUrl = new URL("https://xat.com/" + chatName);
		URLConnection connection = siteUrl.openConnection();
		try (BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
			String line = "";
			while ((line = bufferedReader.readLine()) != null) {
				if (line.toLowerCase().contains("name=\"chat\" flashvars=\"id=")) {
					chatId = StringUtils.getBetween(line.toLowerCase(), "id=", "&");
					break;
				}
			}
		} catch (IOException e) {
			throw new RuntimeException("Failed to fetch chat id");
		}
		return chatId;
}
```

## Update (2018-07-27)

This project is now maintained by [x00x90](https://github.com/x00x90)

## Update (2018-07-22)

This project is no longer actively maintained.

-------------------------

## Changelogs

**2018-07-27**: This bot now supports multiple xats at the same time

**2016-12-18**: Fixed bot not connecting issue. Reason: Xat servers have new ips. No modification was made on the bot script itself because the API on my website was the one that needed to be updated to give the right ips. ( https://twinnation.org/api/xat?chat=ring0 )


## Compatibility and Python version

This bot was made using **Python 2.7.10**, meaning it *most likely* works for 2.7.x. As for those of you who **absolutely** want to use 3.x, then you can learn about how to convert it easily by looking up *lib2to3* online.
