from pydantic import BaseModel, model_validator, field_validator
from pydantic.types import UUID4
from typing import Literal, Self
from datetime import time


def set_domains(domains: list[str]):
	pass


def get_domains():
	pass


def get_schedules(id: UUID4 | str | None = None):
	pass


def get_presets(id: UUID4 | str | None = None):
	pass


class CreateSchedule(BaseModel):
	preset: UUID4 | str
	days: list[Literal['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']]
	name: str
	from_time: time
	to_time: time

	@model_validator(mode='after')
	def validate_time_range(self) -> Self:
		if self.from_time >= self.to_time:
			raise ValueError('from_time must be before to_time')
		return self


def create_schedule(data: CreateSchedule):
	pass


class CreatePreset(BaseModel):
	name: str
	domains: list[str]

	@field_validator('name', mode='after')
	@classmethod
	def validate_name(cls, name: str) -> str:
		# TODO: Get presets
		# presets = get_presets()

		if len(name) > 32:
			raise ValueError(
				'Name must be less than 32 characters because why would you make it longer than that'
			)
		# TODO: Check if name already exists
		return name


def create_preset(data: CreatePreset):
	pass
