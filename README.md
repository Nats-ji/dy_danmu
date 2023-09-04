# dy_danmu

A python library for fetching the chat data from the douyin livestream. Rewrote from [douyin-live](https://github.com/YunzhiYike/douyin-live).

## Install requirements

python 3.10 and above

### (Recommanded) Set up a virtual environment
```sh
# set up the venv
python -m venv .venv
```

Activate the venv, one of the following:
```sh
# activate the venv

# linux and macos
.venv/Scripts/activate

# windows cmd
.venv/Scripts/activate.bat

# windows powershell
.venv/Scripts/Activate.ps1
```

### pip install
```sh
pip install -r requirements.txt
```

## Run the demo
You may want to edit the channel id and the cookies first.
```sh
python ./demo/main.py
```

## Usage
```py
import dy_danmu as DYDM

def OnChatMessage(data: DYDM.ChatMessage):
    print(f"User:\t{data.user.nick_name}")
    print(f"Msg:\t{data.content}")

cookies: str = "__ac_nonce=PutYourCookiesStringHere"
channelId: str = "1234567890"

myChannel = DYDM.Channel(channelId, cookies)
myChannel.OnChatMessage = OnChatMessage
myChannel.Connect()
```

Threading
```py
from threading import Thread
import dy_danmu as DYDM

def OnChatMessage(data: DYDM.ChatMessage):
    print(f"Channel:\t{data.common.room_id}")
    print(f"User:\t{data.user.nick_name}")
    print(f"Msg:\t{data.content}")

cookies: str = "__ac_nonce=PutYourCookiesStringHere"
channelId1: str = "1234567890"
channelId2: str = "2345678901"

myChannel1 = DYDM.Channel(channelId1, cookies)
myChannel2 = DYDM.Channel(channelId2, cookies)
myChannel1.OnChatMessage = OnChatMessage
myChannel2.OnChatMessage = OnChatMessage

Thread(target=myChannel1.Connect).start()
Thread(target=myChannel2.Connect).start()

input("Press Enter to disconnect..")
myChannel1.Disconnect()
myChannel2.Disconnect()

```

## Compile the Protocol Buffers

This project use [python-betterproto](https://github.com/danielgtaylor/python-betterproto) to compile the proto file.

To compile the proto file, run the following commands.

```sh
# install the compiler
pip install "betterproto[compiler]"
# invoke protoc directly
protoc -I ./proto --python_betterproto_out=dy_danmu/lib dy.proto

# or invoke protoc via grpcio-tools
pip install grpcio-tools
python -m grpc_tools.protoc -I ./proto --python_betterproto_out=dy_danmu/lib douyin.proto
```

# Contribute to the code

Feel free to make pull requests.

# Credits

[YunzhiYike/douyin-live](https://github.com/YunzhiYike/douyin-live) for all the reverse engineering works and `douyin.proto`.

[HaoDong108/DouyinBarrageGrab](https://github.com/HaoDong108/DouyinBarrageGrab) for some of the message classes in `douyin.proto`.
