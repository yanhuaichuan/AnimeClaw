# SPDX-License-Identifier: Elastic-2.0
# Copyright (c) 2026 yanhuaichuan
import pytest
from fastapi import HTTPException

from novelvideo.api.deps import validate_project_name


@pytest.mark.parametrize("name", ["demo", "ep_01", "漫剧工厂", "苏璃十镜"])
def test_validate_project_name_allows_ascii_and_chinese(name: str) -> None:
    validate_project_name(name)


@pytest.mark.parametrize("name", ["", "has space", "foo/bar", "foo.bar", "../x", "a" * 65])
def test_validate_project_name_rejects_unsafe_values(name: str) -> None:
    with pytest.raises(HTTPException) as exc:
        validate_project_name(name)
    assert exc.value.status_code == 400
