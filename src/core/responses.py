from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK


class DeleteResponse(JSONResponse):
    def __init__(self, file_id: int):
        content = {
            "msg": "Файл успешно удалён",
            "file_id": file_id
        }
        super().__init__(status_code=HTTP_200_OK, content=content)
