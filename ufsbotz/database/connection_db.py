import logging

from ufsbotz.database import conndb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def add_connection(group_id, user_id):
    query = conndb.find_one(
        {"_id": str(user_id)},
        {"_id": 0, "active_group": 0}
    )
    if query is not None:
        group_ids = [x["group_id"] for x in query["group_details"]]
        if group_id in group_ids:
            return False

    group_details = {
        "group_id": group_id
    }

    data = {
        '_id': str(user_id),
        'group_details': [group_details],
        'active_group': group_id,
    }

    if conndb.count_documents({"_id": str(user_id)}) == 0:
        try:
            conndb.insert_one(data)
            return True
        except:
            logger.exception('Some error occured!', exc_info=True)

    else:
        try:
            conndb.update_one(
                {'_id': str(user_id)},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group": group_id}
                }
            )
            return True
        except:
            logger.exception('Some error occured!', exc_info=True)


async def active_connection(user_id):
    query = conndb.find_one(
        {"_id": str(user_id)},
        {"_id": 0, "group_details": 0}
    )
    if not query:
        return None

    group_id = query['active_group']
    if group_id is not None:
        return int(group_id)
    else:
        return None


async def all_connections(user_id):
    query = conndb.find_one(
        {"_id": str(user_id)},
        {"_id": 0, "active_group": 0}
    )
    if query is not None:
        return [x["group_id"] for x in query["group_details"]]
    else:
        return None


async def if_active(user_id, group_id):
    query = conndb.find_one(
        {"_id": str(user_id)},
        {"_id": 0, "group_details": 0}
    )
    return query is not None and query['active_group'] == group_id


async def make_active(user_id, group_id):
    update = conndb.update_one(
        {'_id': str(user_id)},
        {"$set": {"active_group": group_id}}
    )
    return update.modified_count != 0


async def make_inactive(user_id):
    update = conndb.update_one(
        {'_id': str(user_id)},
        {"$set": {"active_group": None}}
    )
    return update.modified_count != 0


async def delete_connection(user_id, group_id):
    try:
        update = conndb.update_one(
            {"_id": str(user_id)},
            {"$pull": {"group_details": {"group_id": group_id}}}
        )
        if update.modified_count == 0:
            return False
        query = conndb.find_one(
            {"_id": str(user_id)},
            {"_id": 0}
        )
        if len(query["group_details"]) >= 1:
            if query['active_group'] == group_id:
                prvs_group_id = query["group_details"][len(query["group_details"]) - 1]["group_id"]

                conndb.update_one(
                    {'_id': str(user_id)},
                    {"$set": {"active_group": prvs_group_id}}
                )
        else:
            conndb.update_one(
                {'_id': str(user_id)},
                {"$set": {"active_group": None}}
            )
        return True
    except Exception as e:
        logger.exception(f'Some error occured! {e}', exc_info=True)
        return False
