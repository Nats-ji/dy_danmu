import requests
import re
import json
import websocket
import gzip
from urllib.parse import unquote
from typing import Callable

from exceptions import *
from parsemsg import *


class Channel:
    def __init__(self, aChannelId: str, aCookie: str) -> None:
        if not aChannelId:
            raise InvalidChannelId("Channel Id cannot be empty.")
        if not aCookie:
            raise InvalidCookie("Cookie cannot be empty.")
        self.id: str = aChannelId
        self.status: int = -1  # 2 = live, 4 = not live, not sure about other codes.
        self.title: str = ""
        self.onwerUid: str = ""
        self.onwerNick: str = ""
        self.catagory: str = ""
        self.subCatagory: str = ""

        self.__wssId: str = ""
        self.__hasInfo: bool = False
        self.__ttwid: str = ""
        self.__cookie: str = aCookie
        self.__isRunning: bool = False

        # callbacks
        # OnOpen(clsObj: Channel, ws: WebsocketApp)
        # OnClose(clsObj: Channel, ws: WebsocketApp, closeStatusCode: int, closeMsg: str)
        # OnError(clsObj: Channel, ws: WebsocketApp, excption: Excption)
        self.OnOpen: Callable | None = None
        self.OnClose: Callable | None = None
        self.OnError: Callable | None = None

        # the following callbacks all have 1 arguments:
        # OnXXXXMessage(data: XXXXMessage)
        self.OnMatchAgainstScoreMessage: Callable | None = None
        self.OnLikeMessage: Callable | None = None
        self.OnMemberMessage: Callable | None = None
        self.OnGiftMessage: Callable | None = None
        self.OnChatMessage: Callable | None = None
        self.OnSocialMessage: Callable | None = None
        self.OnRoomUserSeqMessage: Callable | None = None
        self.OnUpdateFanTicketMessage: Callable | None = None
        self.OnCommonTextMessage: Callable | None = None
        self.OnProductChangeMessage: Callable | None = None
        self.OnControlMessage: Callable | None = None
        self.OnFansclubMessage: Callable | None = None

    def FetchInfo(self) -> None:
        URL = f"https://live.douyin.com/{self.id}"
        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Cookie": self.__cookie,
        }

        try:
            res: requests.Response = requests.get(url=URL, headers=HEADERS, timeout=5)
            res.raise_for_status()
        except Exception as err:
            raise Exception(f"Failed to fetch channel info. Error: {err}")

        try:
            self.__ttwid = res.cookies.get_dict()["ttwid"]
            if not self.__ttwid:
                raise Exception("ttwid is empty.")

            matches = re.search(
                r'<script id="RENDER_DATA" type="application/json">(.*?)</script>',
                res.text,
            )
            if not matches:
                raise Exception("Failed to find the embeded data.")

            dataRaw: str = matches.group(1)
            data: dict = json.loads(unquote(dataRaw))
            channelInfo = data["app"]["initialState"]["roomStore"]["roomInfo"]
            # check if the channel id valid
            if channelInfo.get("roomId") is None:
                raise InvalidChannelId("Invalid Channel Id.")

            self.__wssId = channelInfo.get("roomId")
            self.status = int(channelInfo["room"]["status"])
            self.title = channelInfo["room"]["title"]
            self.onwerUid = channelInfo["anchor"]["id_str"]
            self.onwerNick = channelInfo["anchor"]["nickname"]

            catagories: dict = channelInfo["partition_road_map"]
            if catagories.get("partition"):
                self.catagory = catagories.get("partition").get("title")
            if catagories.get("sub_partition"):
                self.subCatagory = catagories.get("sub_partition").get("title")

            self.__hasInfo = True
        except Exception as err:
            raise Exception(f"Failed to parse channel info. Error: {err}")

    def Connect(self) -> None:
        if not self.__hasInfo:
            self.FetchInfo()

        if self.status != 2:
            raise ChannelNotLive("Channel is not live.")

        WEBSOCKETURL = f"wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim|wss_push_room_id:{self.__wssId}|wss_push_did:7188358506633528844|dim_log_id:20230521093022204E5B327EF20D5CDFC6|fetch_time:1684632622323|seq:1|wss_info:0-1684632622323-0-0|wrds_kvs:WebcastRoomRankMessage-1684632106402346965_WebcastRoomStatsMessage-1684632616357153318&cursor=t-1684632622323_r-1_d-1_u-1_h-1&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&maxCacheMessageNumber=20&endpoint=live_pc&support_wrds=1&im_path=/webcast/im/fetch/&user_unique_id=7188358506633528844&device_platform=web&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name=Mozilla&browser_version=5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai&identity=audience&room_id={self.__wssId}&heartbeatDuration=0&signature=00000000"
        HEADER = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Cookie": f"ttwid={self.__ttwid}",
        }
        self.__ws = websocket.WebSocketApp(
            WEBSOCKETURL,
            on_message=self.__onMessage,
            on_error=self.__onError,
            on_close=self.__onClose,
            on_open=self.__onOpen,
            header=HEADER,
        )

        pingPayload = PushFrame(payload_type="hb").SerializeToString()
        self.__ws.run_forever(ping_interval=15, ping_payload=pingPayload, reconnect=5)
        self.__isRunning = False

    def Disconnect(self) -> None:
        self.__ws.close()
        self.__isRunning = False

    def IsRunning(self) -> bool:
        return self.__isRunning

    def __callback(self, aCallback: Callable | None, *aArgs) -> None:
        if aCallback:
            try:
                aCallback(self, *aArgs)
            except Exception as err:
                raise CallbackError(f"Error from callback {aCallback}: {err}")

    def __onOpen(self, aWs: websocket.WebSocketApp):
        self.__isRunning = True
        self.__callback(self.OnOpen, aWs)

    def __onClose(self, aWs: websocket.WebSocketApp, aCloseStatusCode: int | None, aCloseMsg: str | None):
        self.__isRunning = False
        self.__callback(self.OnOpen, aWs, aCloseStatusCode, aCloseMsg)

    def __onError(self, aWs: websocket.WebSocketApp, aException: Exception):
        self.__callback(self.OnError, aWs, aException)

    def __onMessage(self, aWs: websocket.WebSocketApp, aData: bytes):
        wssPackage = PushFrame().parse(aData)
        payloadPackage = Response().parse(gzip.decompress(wssPackage.payload))
        if payloadPackage.need_ack:
            ack = EncodeAck(wssPackage.log_id)
            aWs.send(ack, websocket.ABNF.OPCODE_BINARY)

        for msg in payloadPackage.messages_list:
            match msg.method:
                case "WebcastMatchAgainstScoreMessage":
                    if self.OnMatchAgainstScoreMessage:
                        self.OnMatchAgainstScoreMessage(ParseMatchAgainstScoreMessage(msg.payload))

                case "WebcastLikeMessage":
                    if self.OnLikeMessage:
                        self.OnLikeMessage(ParseLikeMessage(msg.payload))

                case "WebcastMemberMessage":
                    if self.OnMemberMessage:
                        self.OnMemberMessage(ParseMemberMessage(msg.payload))

                case "WebcastGiftMessage":
                    if self.OnGiftMessage:
                        self.OnGiftMessage(ParseGiftMessage(msg.payload))

                case "WebcastChatMessage":
                    if self.OnChatMessage:
                        self.OnChatMessage(ParseChatMessage(msg.payload))

                case "WebcastSocialMessage":
                    if self.OnSocialMessage:
                        self.OnSocialMessage(ParseSocialMessage(msg.payload))

                case "WebcastRoomUserSeqMessage":
                    if self.OnRoomUserSeqMessage:
                        self.OnRoomUserSeqMessage(ParseSocialMessage(msg.payload))

                case "WebcastUpdateFanTicketMessage":
                    if self.OnUpdateFanTicketMessage:
                        self.OnUpdateFanTicketMessage(ParseUpdateFanTicketMessage(msg.payload))

                case "WebcastCommonTextMessage":
                    if self.OnCommonTextMessage:
                        self.OnCommonTextMessage(ParseCommonTextMessage(msg.payload))

                case "WebcastProductChangeMessage":
                    if self.OnProductChangeMessage:
                        self.OnProductChangeMessage(ParseProductChangeMessage(msg.payload))

                case "WebcastControlMessage":
                    controlMessage = ParseControlMessage(msg.payload)

                    if self.OnControlMessage:
                        self.OnControlMessage(controlMessage)

                    # Live stream ended
                    if controlMessage.status == 3:
                        self.status = controlMessage.status
                        self.Disconnect()

                case "WebcastFansclubMessage":
                    if self.OnFansclubMessage:
                        self.OnFansclubMessage(ParseFansclubMessage(msg.payload))
