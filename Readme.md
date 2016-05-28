# Data preprocessing for statistical analysis.

This is a Python module.

## Functionality

Remove rows from a data frame:

* Unused variables
* Null values in the 'Value' column
* Non-numeric values in the 'Value' column
* Numeric values in the 'Value' column that are outside a specified range

Modify values in the 'Value' column of a data frame:

* Apply units conversions
* Encode textual variables
* Strip certain characters from otherwise-numeric values (e.g. '>')
* Remove numeric values outside specified range

## Installation

To install from a UNIX shell, run

```
pip install git+ssh://git@github.com:jcasse/data-preprocessing.git
```

To uninstall, run

```
pip uninstall preprocessing
```
