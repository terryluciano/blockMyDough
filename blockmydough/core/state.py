import json
from typing import Literal

from pydantic import BaseModel
from pydantic.types import UUID4

from blockmydough.constants import STATE_FILE


class ScheduleState(BaseModel):
	schedule_id: UUID4


def read_state():
	try:
		with open(STATE_FILE, encoding='utf-8') as f:
			return json.load(f)
	except FileNotFoundError:
		return None
	except json.JSONDecodeError as e:
		raise json.JSONDecodeError(f'Invalid JSON in {STATE_FILE}: {e.msg}', e.doc, e.pos)
	except PermissionError:
		raise PermissionError(f'Cannot read {STATE_FILE}: Permission denied')


# TODO: do this
class WriteState(BaseModel):
	blocking_type: Literal['schedule', 'timer']
	schedule_id: ScheduleState | None = None
	timer_id: str | None = None


# def write_state(data: WriteState):
# 	try:
# 		test = WriteState.model_validate(data)
# 	except ValidationError as e:
# 		print(e)
