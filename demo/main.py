import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import __init__ as DYDM

def OnChatMessage(data: DYDM.ChatMessage):
    print(f"User:\t{data.user.nick_name}")
    print(f"Msg:\t{data.content}")

def OnGiftMessage(data: DYDM.GiftMessage):
    print(f"User:\t{data.user.nick_name}")
    print(f"Gift:\t{data.gift.name}")

if __name__ == '__main__':
    # Create a channel
    # The first paramater is the id from the channel url
    # The econd once is your cookies, only requires the "__ac_nonce" field.
    myChannel = DYDM.Channel("288148724178", "__ac_nonce=asadja121029109122")

    # Register callbacks to the messages you want to listen to.
    myChannel.OnChatMessage = OnChatMessage
    myChannel.OnGiftMessage = OnGiftMessage

    # Connect the websocket
    myChannel.Connect()

    # check the source code for more information about the Channel class
