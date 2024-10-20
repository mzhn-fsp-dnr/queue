from pydantic import UUID4
import requests

from api.conifg import conf_settings
from api.schemas.office import OfficeResponse

URL = conf_settings.OFFICES_URL


def get(office_id: UUID4) -> OfficeResponse | None:
    fn = f"office({office_id})"
    endpoint = f"{URL}/offices/{office_id}"

    print(f'[{fn}] requesting "{endpoint}"')
    try:
        response = requests.get(endpoint)

        if response.status_code != 200:
            print(
                f"[{fn}] status code - {response.status_code}, data - {response.content}"
            )
            return None

        j = response.json()

        schema = OfficeResponse(**j)
        print(f"[{fn}] prereg executed, response({response.status_code})=", schema)

        return schema
    except Exception as e:
        print("ERROR: ", e)
        return None
