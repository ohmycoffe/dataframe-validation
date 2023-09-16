import pandas as pd
import pytest

from pandas_validity.data_type_registry import DataTypeValidatorsRegistry
from pandas_validity.exceptions import RegistryError


@pytest.fixture
def mocked_registry():
    reg = DataTypeValidatorsRegistry()
    reg.register(_callable=pd.api.types.is_string_dtype, alias=str)
    reg.register(_callable=pd.api.types.is_integer_dtype, alias=int)
    reg.register(_callable=pd.api.types.is_float_dtype, alias=float)
    reg.register(_callable=pd.api.types.is_string_dtype, alias=str)
    yield reg


def test_should_raise_error_if_not_registered(
    mocked_registry: DataTypeValidatorsRegistry,
):
    missing_key = "missing_key"
    with pytest.raises(RegistryError) as excinfo:
        mocked_registry[missing_key]
    tested_msg = excinfo.value.args[0]
    assert tested_msg == f"'{missing_key}' is not registered as a valid callable."


def test_register_as_decorator(mocked_registry: DataTypeValidatorsRegistry):
    key1 = "tested"

    @mocked_registry.register_decorator(alias=key1)
    def custom_validator1(dtype):
        return True

    assert key1 in mocked_registry
    assert custom_validator1 in mocked_registry

    @mocked_registry.register_decorator
    def custom_validator2(dtype):
        return False

    assert custom_validator2 in mocked_registry


def test_should_raise_error_on_invalid_callable(
    mocked_registry: DataTypeValidatorsRegistry,
):
    invalid_ret = "invalid return type"
    alias = "key"

    assert not isinstance(invalid_ret, bool)

    def invalid_validator(dtype):
        return invalid_ret

    with pytest.raises(RegistryError) as excinfo:
        mocked_registry.register(_callable=invalid_validator, alias=alias)
    tested_msg = excinfo.value.args[0]
    assert (
        tested_msg
        == "Callable `invalid_validator` should return a boolean value - returned"
        f" `{invalid_ret}`."
    )


def test_should_raise_error_if_not_callable(
    mocked_registry: DataTypeValidatorsRegistry,
):
    not_a_callable = None

    with pytest.raises(RegistryError) as excinfo:
        mocked_registry.register(_callable=not_a_callable)  # type: ignore
    tested_msg = excinfo.value.args[0]
    assert tested_msg == f"`{not_a_callable}` should be a callable"


def test_should_raise_error_if_error_occured_in_callabe(
    mocked_registry: DataTypeValidatorsRegistry,
):
    expected_error_msg = "Error"
    expected_error = Exception(expected_error_msg)

    def callable_with_error(dtype):
        raise expected_error

    with pytest.raises(RegistryError) as excinfo:
        mocked_registry.register(_callable=callable_with_error)
    tested_msg = excinfo.value.args[0]
    assert (
        tested_msg == "Callable failed for the sanity check:"
        f" `{callable_with_error.__name__}(int)`:"
        f" '{expected_error}'"
    )
