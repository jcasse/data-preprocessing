"""
Data preprocessing functions.
"""

# This __init__.py
#   Gives access to functions at the package level,
#   i.e. preprocessing.code.load_settings isn't required
#   That's nice because later we can refactor into separate files,
#   and not break others' code.
#   Only makes the specified functions available.
#   (Can also prefix _ in the name to do that.)
#   Still makes the 'code' submodule available, which I don't like.

from .src.settings import load_settings
from .src.settings import show_available_settings

from .src.remove_rows import remove_null
from .src.remove_rows import remove_nonnumeric
from .src.remove_rows import remove_nondatetime
from .src.remove_rows import remove_nondate
from .src.remove_rows import remove_episodes

from .src.remove_rows_by_variable import remove_alpha_by_variable
from .src.remove_rows_by_variable import remove_nonnumeric_by_variable
from .src.remove_rows_by_variable import remove_extreme_by_variable
from .src.remove_rows_by_variable import remove_vars
from .src.remove_rows_by_variable import remove_unmapped_text_value_by_variable

from .src.convert import select_cols
from .src.convert import rename_cols

from .src.convert_rows import convert_to_epoch_time
from .src.convert_rows import convert_bad_times_to_empty_string
from .src.convert_rows import convert_flagged_to_NaN

from .src.convert_by_variable import age_normalize_by_variable
from .src.convert_by_variable import convert_units_by_variable
from .src.convert_by_variable import convert_dict_values_by_variable
from .src.convert_by_variable import encode_text_values_by_variable
from .src.convert_by_variable import convert_weird_numeric_by_variable
from .src.convert_by_variable import clip_values_by_variable

from .src.utils import condition_var_names
from .src.utils import flag_numeric
from .src.utils import flag_datetime
from .src.utils import flag_date
from .src.utils import is_numeric_variable
from .src.utils import read_data
