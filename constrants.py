from enum import Enum


class NotificationTitle(Enum):
    Order = '注文'
    OrderCancel = '注文キャンセル'
    Position = '約定'
    Settlement = '清算'
    Info = '情報'
    Error = 'エラー'
