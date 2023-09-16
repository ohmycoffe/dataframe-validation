# pandas-validity
It is a library to validate pandas DataFrames at once.
The `DataFrameValidator` is used as a context manager. In the context you may run multiple validations/checks.
All occurred errors are gathered and printed in the end of process.
The `DataFrameValidator` raises `ValidationErrorsGroup` exception.

```python
import pandas as pd
import datetime
from pandas_validity.validator import DataFrameValidator

df = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": ["a", None, "c"],
            "C": [2.3, 4.5, 9.2],
            "D": [
                datetime.datetime(2023, 1, 1, 1),
                datetime.datetime(2023, 1, 1, 2),
                datetime.datetime(2023, 1, 1, 3),
            ],
        }
    )
expected_columns= ['A', 'B', 'C', 'E']
data_types_mapping={
            "A": 'float',
            "D": 'datetime'
        }
with DataFrameValidator(df) as validator:
    validator.is_empty()
    validator.has_required_columns(expected_columns)
    validator.has_no_redundant_columns(expected_columns)
    validator.has_valid_data_types(data_types_mapping)
    validator.has_no_missing_data()
```
Output:
```
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) The dataframe has missing columns: ['E']
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) The dataframe has redundant columns: ['D']
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) Column 'A' has invalid data-type: 'int64'
Error occurred: (<class 'pandas_validity.exceptions.ValidationError'>) Found 1 missing values: [{'index': 1, 'column': 'B', 'value': None}]
  + Exception Group Traceback (most recent call last):
...
  | pandas_validity.exceptions.ValidationErrorsGroup: Validation errors found: 4. (4 sub-exceptions)
  +-+---------------- 1 ----------------
    | pandas_validity.exceptions.ValidationError: The dataframe has missing columns: ['E']
    +---------------- 2 ----------------
    | pandas_validity.exceptions.ValidationError: The dataframe has redundant columns: ['D']
    +---------------- 3 ----------------
    | pandas_validity.exceptions.ValidationError: Column 'A' has invalid data-type: 'int64'
    +---------------- 4 ----------------
    | pandas_validity.exceptions.ValidationError: Found 1 missing values: [{'index': 1, 'column': 'B', 'value': None}]
    +------------------------------------
```
