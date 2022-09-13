import re
from typing import List
import uuid

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from db.DbContext import DbContext


class ImportItem(BaseModel):
    items: List
    updateDate: str


app = FastAPI()
dbContext = DbContext()


@app.post("/imports", status_code=200)
async def import_data(data: ImportItem):
    used_ids = []
    is_valid_request = True
    validation_failed = JSONResponse(content={
        "code": 400,
        "message": "Validation Failed"
    }, status_code=400)

    for item in data.items:
        id_in_folders = dbContext.contains_item_in_folders(item['id'])
        id_in_files = dbContext.contains_item_in_files(item['id'])
        if (item["type"] == "FILE" and id_in_folders) \
                or (item["type"] == "FOLDER" and id_in_files) \
                or item["id"] is None \
                or dbContext.contains_item_in_files(item["parentId"]) \
                or (item["type"] == "FOLDER" and "url" in item) \
                or (item["type"] == "FOLDER" and "size" in item) \
                or (item["type"] == "FILE" and (item["size"] is None or item["size"] < 0)) \
                or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', data.updateDate) \
                or item["id"] in used_ids \
                or not (item["type"] == "FOLDER" or item["type"] == "FILE"):
            is_valid_request = False
            break
        else:
            try:
                uuid.UUID(item["id"])
            except:
                is_valid_request = False
                break
            used_ids.append(item["id"])

    if is_valid_request:
        for item in data.items:
            if dbContext.contains_item_in_folders(item['id']) or dbContext.contains_item_in_files(item['id']):
                pass
            else:
                dbContext.insert_data(
                    id=item["id"],
                    url=item["url"] if "url" in item else None,
                    parent_id=item["parentId"],
                    size=item["size"] if "size" in item else None,
                    type=item["type"],
                    date=data.updateDate
                )

        return
    else:
        return validation_failed


@app.delete("/delete/{id}", status_code=200)
async def delete_item(id: str):
    try:
        uuid.UUID(id)
    except:
        return JSONResponse(content={
            "code": 400,
            "message": "Validation Failed"
        }, status_code=400)

    if dbContext.delete_item(id):
        return
    else:
        return JSONResponse(content={
            "code": 404,
            "message": "Item not found"
        }, status_code=404)


@app.get("/nodes/{id}", status_code=200)
async def get_node(id: str):
    try:
        uuid.UUID(id)
    except:
        return JSONResponse(content={
            "code": 400,
            "message": "Validation Failed"
        }, status_code=400)
    item_in_files = dbContext.contains_item_in_files(id)
    item_in_folders = dbContext.contains_item_in_folders(id)
    if not (item_in_files or item_in_folders):
        return JSONResponse(content={
            "code": 404,
            "message": "Item not found"
        }, status_code=404)
    else:
        response = getNextTree(id, type="file" if item_in_files else "folder")
        return JSONResponse(content=response, status_code=200)


def getNextTree(id, type):
    curr_object = dbContext.get_item_by_id(id, type)
    dict_object = object_to_dict(curr_object, type)
    if type == "folder":
        all_children = dbContext.get_children_by_id(dict_object["id"])
        for child in all_children:
            if child["type"] == "folder":
                dict_object["children"].append(getNextTree(id=child["data"][0], type="folder"))
            else:
                dict_object["children"].append(object_to_dict(child["data"], child["type"]))
    return dict_object


def object_to_dict(curr_object: tuple, type: str, with_children=True):
    model_dict = {
        "id": curr_object[0],
        "url": curr_object[1],
        "date": curr_object[2].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parentId": curr_object[3],
        "size": curr_object[4],
        "type": type.upper(),
    }
    if with_children:
        model_dict["children"] = [] if type == "folder" else None
    return model_dict


@app.get("/updates", status_code=200)
async def get_updates(date: str):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', date):
        return JSONResponse(content={
            "code": 400,
            "message": "Validation Failed"
        }, status_code=400)

    data = dbContext.get_files_by_date(date)
    return JSONResponse(content={
        "items": [object_to_dict(item, type="file", with_children=False) for item in data]
    }, status_code=200)


@app.get("/node/{id}/history", status_code=200)
async def get_history(id: str, dateStart: str, dateEnd: str):
    validation_failed = JSONResponse(content={
        "code": 400,
        "message": "Validation Failed"
    }, status_code=400)
    try:
        uuid.UUID(id)
    except:
        return validation_failed

    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', dateStart) or \
            not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', dateEnd):
        return validation_failed

    data, is_contains = dbContext.get_history_by_id(id, dateStart, dateEnd)
    if is_contains:
        return JSONResponse(content={
            "items": [object_to_dict_history(item) for item in data]
        }, status_code=200)
    else:
        return JSONResponse(content={
            "code": 404,
            "message": "Item not found"
        }, status_code=404)


def object_to_dict_history(curr_object):
    return {
        "id": curr_object[1],
        "url": curr_object[2],
        "date": curr_object[3].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parentId": curr_object[4],
        "size": curr_object[5],
        "type": curr_object[6],
    }
