


from http import HTTPStatus
from fastapi import HTTPException


unauthorized_url_part_exception = HTTPException(
    status_code= HTTPStatus.FORBIDDEN,
    detail = 'Url for part out of range for upload ticket.'
)