# dataframe-validation
It is a library to validate pandas DataFrames at once.
The `DataFrameValidator` is used as a context manager. In the context you may run multiple validations/checks.
All occurred errors are gathered and printed in the end of process.
The `DataFrameValidator` raises `ValidationErrorsGroup` exception.

```python
import pandas as pd
import datetime
from dataframe_validation.validator import DataFrameValidator

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
Error occurred: (<class 'dataframe_validation.exceptions.ValidationError'>) The dataframe has missing columns: ['E']
Error occurred: (<class 'dataframe_validation.exceptions.ValidationError'>) The dataframe has redundant columns: ['D']
Error occurred: (<class 'dataframe_validation.exceptions.ValidationError'>) Column 'A' has invalid data-type: 'int64'
Error occurred: (<class 'dataframe_validation.exceptions.ValidationError'>) Found 1 missing values: [{'index': 1, 'column': 'B', 'value': None}]
  + Exception Group Traceback (most recent call last):
  |   File "/home/user/projects/pydata-validator/run.py", line 21, in <module>
  |     with DataFrameValidator(df) as validator:
  |   File "/home/user/projects/pydata-validator/src/dataframe_validation/abstract.py", line 33, in __exit__
  |     raise ValidationErrorsGroup(
  | dataframe_validation.exceptions.ValidationErrorsGroup: Validation errors found: 4. (4 sub-exceptions)
  +-+---------------- 1 ----------------
    | dataframe_validation.exceptions.ValidationError: The dataframe has missing columns: ['E']
    +---------------- 2 ----------------
    | dataframe_validation.exceptions.ValidationError: The dataframe has redundant columns: ['D']
    +---------------- 3 ----------------
    | dataframe_validation.exceptions.ValidationError: Column 'A' has invalid data-type: 'int64'
    +---------------- 4 ----------------
    | dataframe_validation.exceptions.ValidationError: Found 1 missing values: [{'index': 1, 'column': 'B', 'value': None}]
    +------------------------------------
```
