
from pyrogram import filters
from ufsbotz import SUDOERS

SUPPORT_USERS = SUDOERS


# class CustomFilters(object):
#     class _Supporters(filters):
#         def filter(self, message):
#             return bool(message.from_user and message.from_user.id in SUPPORT_USERS)
#
#     support_filter = _Supporters()
#
#     class _Sudoers(filters):
#         def filter(self, message):
#             return bool(message.from_user and message.from_user.id in SUDOERS)
#
#     sudo_filter = _Sudoers()
#
#     class _MimeType(filters):
#         def __init__(self, mimetype):
#             self.mime_type = mimetype
#             self.name = "CustomFilters.mime_type({})".format(self.mime_type)
#
#         def filter(self, message):
#             return bool(message.document and message.document.mime_type == self.mime_type)
#
#     mime_type = _MimeType
#
#     class _HasText(filters):
#         def filter(self, message):
#             return bool(message.text or message.sticker or message.photo or message.document or message.video)
#
#     has_text = _HasText()


def _Supporters(filt, client, message):
    return bool(message.from_user and message.from_user.id in SUPPORT_USERS)


support_filter = filters.create(
    func=_Supporters,
    name="support_filter"
)


def _Sudoers(filt, client, message):
    return bool(message.from_user and message.from_user.id in SUDOERS)


sudo_filter = filters.create(
    func=_Sudoers,
    name="sudo_filter"
)


def _MimeType(filt, client, message):
    return bool(message.document and message.document.mime_type in client.types.mime_type)


mime_type = filters.create(
    func=_MimeType,
    name="mime_type"
)


def _HasText(filt, client, message):
    return bool(message.text or message.sticker or message.photo or message.document or message.video)


has_text = filters.create(
    func=_HasText,
    name="has_text"
)
