import logging
from functools import lru_cache

import b2sdk.v2 as b2
from app.config import config

logger = logging.getLogger(__name__)


@lru_cache()
def b2_api():
    """Returns a b2 api object"""
    logger.debug("Creating and authorizing B2 API.")
    info = b2.InMemoryAccountInfo()
    b2_api = b2.B2Api(info)

    b2_api.authorize_account(
        "production", config.BACKLBLAZE_B2_KEY_ID, config.BACKLBLAZE_B2_APPLICATION_KEY
    )
    return b2_api


@lru_cache()
def b2_get_bucket(api: b2.B2Api):
    """Returns a b2 bucket object"""
    bucket = api.get_bucket_by_name(config.BACKLBLAZE_B2_BUCKET_NAME)
    return bucket


def b2_upload_file(local_file: str, file_name: str) -> str:
    """Uploads a file to b2"""
    logger.debug("Uploading file to b2", extra={"file_name": file_name})
    api = b2_api()
    bucket = b2_get_bucket(api)
    uploaded_file = bucket.upload_local_file(local_file=local_file, file_name=file_name)
    logger.info(
        "Uploaded to b2", extra={"file_id": uploaded_file.id, "file_name": file_name}
    )
    download_url = api.get_download_url_for_file(uploaded_file.id)
    return download_url
