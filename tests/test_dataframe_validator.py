import datetime
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pandas_validity.exceptions import ValidationError, ValidationErrorsGroup
from pandas_validity.validator import DataFrameValidator


@pytest.fixture
def valid_df():
    df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": ["a", "b", "c"],
            "C": [2.3, 4.5, 9.2],
            "D": [
                datetime.datetime(2023, 1, 1, 1),
                datetime.datetime(2023, 1, 1, 2),
                datetime.datetime(2023, 1, 1, 3),
            ],
            "E": ["A", "B", "C"],
        }
    )
    yield df


def test_should_pass_if_valid_dataframe(valid_df: pd.DataFrame):
    expected_columns = list(valid_df.columns)
    expected_data_types = {"A": "int", "B": "str", "C": "float", "D": "datetime"}
    with DataFrameValidator(valid_df) as validator:
        validator.is_empty()
        validator.has_required_columns(expected_columns)
        validator.has_no_redundant_columns(expected_columns)
        validator.has_valid_data_types(expected_data_types)
        validator.has_no_missing_data()


def test_should_raise_error_if_df_is_empty(valid_df: pd.DataFrame):
    invalid_df = valid_df.drop(index=valid_df.index)
    assert invalid_df.empty

    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(invalid_df) as validator:
            validator.is_empty()

    reasons = excinfo.value.args[1]
    assert 1 == len(reasons)
    err = reasons[0]
    assert isinstance(err, ValidationError)
    assert "The dataframe is empty." == str(err)


def test_should_raise_error_if_2_missing_columns(valid_df: pd.DataFrame):
    missing_columns = ["A", "C"]
    invalid_df = valid_df.drop(columns=missing_columns)
    assert "A" not in invalid_df.columns
    assert "C" not in invalid_df.columns

    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(invalid_df) as validator:
            validator.has_required_columns(list(valid_df.columns))

    reasons = excinfo.value.args[1]
    assert 1 == len(reasons)
    err = reasons[0]
    assert isinstance(err, ValidationError)
    assert str(f"The dataframe has missing columns: {missing_columns}") == str(
        err.args[0]
    )


def test_should_raise_error_if_redundan_column_exist(valid_df: pd.DataFrame):
    redundant_column = "redundant_column"
    invalid_df = valid_df.assign(**{redundant_column: [1] * valid_df.shape[0]})
    assert redundant_column in invalid_df.columns

    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(invalid_df) as validator:
            validator.has_no_redundant_columns(expected_columns=list(valid_df.columns))

    reasons = excinfo.value.args[1]
    assert 1 == len(reasons)
    err = reasons[0]
    assert isinstance(err, ValidationError)
    assert str(f"The dataframe has redundant columns: {[redundant_column]}") == str(
        err.args[0]
    )


def test_should_raise_error_if_wrong_datatypes(valid_df: pd.DataFrame):
    wrong_validators = {
        "A": pd.api.types.is_string_dtype,
        "B": pd.api.types.is_integer_dtype,
    }
    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(valid_df) as validator:
            validator.has_valid_data_types(expected_data_types=wrong_validators)

    reasons = excinfo.value.args[1]
    assert len(wrong_validators) == len(reasons)

    assert isinstance(reasons[0], ValidationError)
    assert "Column 'A' has invalid data-type: 'int64'" == str(reasons[0])

    assert isinstance(reasons[1], ValidationError)
    assert "Column 'B' has invalid data-type: 'object'" == str(reasons[1])


def test_should_raise_error_if_missing_data(valid_df: pd.DataFrame):
    missing_values = [
        {"index": 0, "column": "D", "value": pd.NaT},
        {"index": 1, "column": "B", "value": None},
        {"index": 2, "column": "C", "value": np.nan},
    ]
    invalid_df = valid_df.copy()

    for val in missing_values:
        invalid_df.loc[val["index"], val["column"]] = val["value"]  # type: ignore

    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(invalid_df) as validator:
            validator.has_no_missing_data()

    reasons = excinfo.value.args[1]
    assert 1 == len(reasons)

    assert isinstance(reasons[0], ValidationError)
    assert f"Found 3 missing values: {missing_values}" == str(reasons[0])


def test_should_raise_expected_and_unexpected_error(
    valid_df: pd.DataFrame, mocker: MockerFixture
) -> None:
    unexpected_exception = Exception("Unexpected exception")
    mocker.patch.object(
        DataFrameValidator,
        "has_no_redundant_columns",
        MagicMock(side_effect=unexpected_exception),
    )
    invalid_df = valid_df.drop(index=valid_df.index)
    assert invalid_df.empty

    with pytest.raises(ValidationErrorsGroup) as excinfo:
        with DataFrameValidator(invalid_df) as validator:
            validator.is_empty()
            validator.has_no_redundant_columns(expected_columns=["missing"])
            validator.has_required_columns(expected_columns=["missing"])

    reasons = excinfo.value.args[1]
    assert 2 == len(reasons)
    assert isinstance(reasons[0], ValidationError)
    assert "The dataframe is empty." == str(reasons[0])
    assert isinstance(reasons[1], type(unexpected_exception))
    assert str(unexpected_exception) == str(reasons[1])
