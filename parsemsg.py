from lib.douyin import *


def EncodeAck(aLogId: int):
    return PushFrame(log_id=aLogId, payload_type='ack').SerializeToString()


def ParseMatchAgainstScoreMessage(aPayload: bytes) -> MatchAgainstScoreMessage:
    return MatchAgainstScoreMessage().parse(aPayload)


# 点赞
def ParseLikeMessage(aPayload: bytes) -> LikeMessage:
    return LikeMessage().parse(aPayload)


# xx成员进入直播间消息
def ParseMemberMessage(aPayload: bytes) -> MemberMessage:
    return MemberMessage().parse(aPayload)


# 礼物消息
def ParseGiftMessage(aPayload: bytes) -> GiftMessage:
    return GiftMessage().parse(aPayload)


# 普通消息
def ParseChatMessage(aPayload: bytes) -> ChatMessage:
    return ChatMessage().parse(aPayload)


# 关注消息
def ParseSocialMessage(aPayload: bytes) -> SocialMessage:
    return SocialMessage().parse(aPayload)


# 直播间统计
def ParseRoomUserSeqMessage(aPayload: bytes) -> RoomUserSeqMessage:
    return RoomUserSeqMessage().parse(aPayload)


def ParseUpdateFanTicketMessage(aPayload: bytes) -> UpdateFanTicketMessage:
    return UpdateFanTicketMessage().parse(aPayload)


def ParseCommonTextMessage(aPayload: bytes) -> CommonTextMessage:
    return CommonTextMessage().parse(aPayload)


# 带货
def ParseProductChangeMessage(aPayload: bytes) -> ProductChangeMessage:
    return ProductChangeMessage().parse(aPayload)


# 直播间状态变更
def ParseControlMessage(aPayload: bytes) -> ControlMessage:
    return ControlMessage().parse(aPayload)


# 粉丝团消息
def ParseFansclubMessage(aPayload: bytes) -> FansclubMessage:
    return FansclubMessage().parse(aPayload)
