import logging
from typing import Dict, List, Union

from ufsbotz.database import notedb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_notes_count() -> dict:
    chats = notedb.find({"chat_id": {"$exists": 1}})
    if not chats:
        return {}
    chats_count = 0
    notes_count = 0
    for chat in chats.to_list(length=1000000000):
        notes_name = get_note_names(chat["chat_id"])
        notes_count += len(notes_name)
        chats_count += 1
    return {"chats_count": chats_count, "notes_count": notes_count}


async def _get_notes(chat_id: int) -> Dict[str, int]:
    _notes = notedb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_note_names(chat_id: int) -> List[str]:
    _notes = []
    for note in _get_notes(chat_id):
        _notes.append(note)
    return _notes


async def get_note(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _notes = _get_notes(chat_id)
    if name in _notes:
        return _notes[name]
    return False


async def save_note(chat_id: int, name: str, note: dict):
    name = name.lower().strip()
    _notes = _get_notes(chat_id)
    _notes[name] = note

    notedb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_note(chat_id: int, name: str) -> bool:
    notesd = _get_notes(chat_id)
    name = name.lower().strip()
    if name in notesd:
        del notesd[name]
        notedb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False
