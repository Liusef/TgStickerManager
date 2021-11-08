# TgStickerManager
A program to deal with @stickers on telegram so you don't have to

# A Stupid Abstract Issue that I cannot explain
This program will **only run properly on *Python 3.10.0*** (the latest version as of writing this).
While the code is technically still valid down to Python 3.7, for some godforsaken reason
Network requests will all time out when being called from a PySide6 button. 

Why does it do this? *I don't know*.
Can I fix it? *I don't know*.

Do I hate it? *Yes*. 
Am I in severe pain and agony? *Always*.

I hate Python.

## Setting up the project
To download the code and run on your local machine, you need to do a couple things
1. Install the required packages from requirements.txt
2. Create a `apikeys.py` file in the src package to store your API keys
   1. The contents of `apikeys.py` should look like this:
   ```py
   api_id: int =  # put your API App ID here
   api_hash: str =  # put your API App Hash here 
   
## Pain
Agony even skjgfdnhlksjhfguedhlkauhfrlgu
