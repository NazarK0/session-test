import os
import chromadb
from chromadb import GetResult
from chromadb.errors import InvalidCollectionException
from fastapi import FastAPI, HTTPException
from pydantic import  UUID4
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# My modules
from data_models import Session
import tools
import const

host = os.getenv("CHROMA_HOST", "localhost")
port = os.getenv("CHROMA_PORT", 9000)

chroma_client = chromadb.HttpClient(host, port)
collection = chroma_client.get_or_create_collection(name="sessions")

app = FastAPI()

@app.get("/")
def get_root():
    return {const.ROOT_MSG}

@app.get("/session/{session_id}")
async def get_session_by_id(session_id: UUID4):
    session: GetResult

    try:
        session = collection.get(
        where={"session_id": session_id.hex},
    )
    except InvalidCollectionException:
        raise HTTPException(status_code=404, detail=const.DETAIL_404)
    except:
        raise HTTPException(status_code=500, detail=const.DETAIL_500)

    if not session["ids"]:
        raise HTTPException(status_code=404, detail=const.DETAIL_404)
    return JSONResponse(session)


@app.put("/session")
def create_or_update_session(session: Session):

    documents = list(map(lambda doc: doc.page_content, session.documents))
    metadatas = list(map(lambda item: dict(item, session_id=session.id.hex),
                         [session.documents[i].metadata for i in range(len(session.documents))]))


    for meta in metadatas:
        meta["created_at"] = meta["created_at"].timestamp()
        meta["readers"] = const.DELIMITER.join(meta["readers"])
        meta["data_source"] = const.DELIMITER.join(meta["data_source"])

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=list(tools.unique_id(len(documents)))
    )
    return JSONResponse(jsonable_encoder(session))

@app.delete("/session/all")
def delete_all_sessions():
    chroma_client.delete_collection("sessions")
    return {"message": "all sessions deleted"}


@app.delete("/session/{session_id}")
def delete_session_by_id(session_id: UUID4):
    session = collection.get(
        where={"session_id": session_id.hex},
    )

    if not session["ids"]:
        raise HTTPException(status_code=404, detail="Error 404. Session not found")

    collection.delete(ids=session["ids"])

    return {"message": f"session {session_id} successfully deleted"}



