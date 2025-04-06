import os
from pprint import pprint

import chromadb
from chromadb.types import Collection
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import  UUID4
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

import tools
# My modules
from data_models import Session
import const

host = os.getenv("CHROMA_HOST", "localhost")
port = os.getenv("CHROMA_PORT", 9000)

chroma_client = chromadb.HttpClient(host, port)

app = FastAPI()

@app.get("/health-check")
def get_health_check():
    return JSONResponse({"status": 200, "message": const.HEALTH_CHECK_MSG})

@app.get("/session/{session_id}")
async def get_session_by_id(session_id: UUID4, text: str = None):
    session: Collection = chroma_client.get_collection(
        name= session_id.hex,
    )

    if text:
        documents  = session.query(query_texts=text)

        return JSONResponse(documents)
    else:
        return JSONResponse(session)
        # raise HTTPException(status_code=404, detail=const.DETAIL_404_DOC)

@app.put("/session")
def create_or_update_session(session: Session):
    new_documents = list(map(lambda doc: doc.page_content, session.documents))
    new_metadatas = list(map(lambda doc: doc.metadata.model_dump(), session.documents))

    for meta in new_metadatas:
        meta["created_at"] = meta["created_at"].timestamp()
        meta["readers"] = const.DELIMITER.join(meta["readers"])
        meta["datasource"] = const.DELIMITER.join(meta["datasource"])

    # Check if session already exists
    # If it exists, we can update it
    # But first we need to check if the collection has the same documents
    # If the collection has the same documents, we can skip the update
    # If the collection has different documents, we need to update it
    # Get the documents in the collection
    session_collection = chroma_client.get_collection(session.id.hex)

    if session_collection:
        # If the collection exists, we can check if the documents are the same
        # Get the documents in the collection
        db_documents = session_collection.get()

        # Check if the documents in the collection are the same as the documents in the session
        for idx, doc in enumerate(new_documents):
            print(new_documents[idx] in db_documents["documents"] and new_metadatas[idx] in db_documents["metadatas"])
            if new_documents[idx] in db_documents["documents"] and new_metadatas[idx] in db_documents["metadatas"]:
                new_documents.remove(new_documents[idx])
                new_metadatas.remove(new_metadatas[idx])

        # If the documents are the same, we can skip the update
        if len(new_documents) == 0:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Session already exists"})
        else:
            # If the documents are different, we need to update the collection
            session_collection.upsert(
                documents=new_documents,
                metadatas=new_metadatas,
                ids=list(tools.unique_id(len(new_documents)))
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully updated session"})
    else:
        # If the collection does not exist, we need to create it
        session_collection = chroma_client.create_collection(
            name=session.id.hex
        )

        session_collection.add(
            documents=new_documents,
            metadatas=new_metadatas,
            ids=list(tools.unique_id(len(new_documents)))
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully created session"})

@app.delete("/session/all")
def delete_all_sessions():
    if chroma_client.reset():
        return {"message": "all sessions deleted"}
    else:
        raise HTTPException(status_code=500, detail=const.DETAIL_500)


@app.delete("/session/{session_id}")
def delete_session_by_id(session_id: UUID4):
    try:
        chroma_client.delete_collection(session_id.hex)
    except ValueError:
        raise HTTPException(status_code=404, detail=const.DETAIL_404_SESSION)

    return {"message": f"session {session_id} successfully deleted"}



