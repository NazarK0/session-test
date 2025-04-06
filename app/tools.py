import uuid

def unique_id(length):
    for idx in range(length):
       yield  str(uuid.uuid4().fields[-1])[:8]