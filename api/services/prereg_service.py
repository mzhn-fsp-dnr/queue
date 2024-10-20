from pydantic import UUID4
import requests

from api.conifg import conf_settings
from api.schemas.prereg import PreregResponse

URL = conf_settings.PREREG_URL


def get(office_id: UUID4, code: int) -> PreregResponse | None:
    fn = f"prereg({office_id, code})"
    endpoint = f"{URL}/office/{office_id}/{code}"

    print(f'[{fn}] requesting "{endpoint}"')
    try:
        response = requests.get(endpoint)

        if response.status_code != 200:
            print(
                f"[{fn}] status code - {response.status_code}, data - {response.content}"
            )
            return None

        j = response.json()

        schema = PreregResponse(**j)
        print(f"[{fn}] prereg executed, response({response.status_code})=", schema)

        return schema
    except Exception as e:
        print("ERROR: ", e)
        return None
