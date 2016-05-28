import vppreprocess

def select_cols(dataDF, varInfo):
    '''
    Returns a data frame containing only the columns specified in varInfo.
    If no columns are specified, the function returns dataDF unchanged.
    '''
    resultDF = dataDF.copy()
    if 'columns' in varInfo:
        cols = ordered_intersection(resultDF.columns.tolist(), varInfo['columns']['include'])
        resultDF = dataDF[cols]
    return resultDF

def rename_cols(dataDF, varInfo):
    '''
    Renames the columns specified in varInfo. Leaves the other column names
    unchanged.
    Returns a data frame, which is a copy of the input dataDF with the
    corresponding column names changed.
    '''
    resultDF = dataDF.copy()
    if 'columns' in varInfo:
        mapping = make_mapping(dataDF.columns.tolist(), varInfo['columns']['renaming'])
        resultDF.rename(columns = mapping, inplace = True)
    return resultDF

# Helper functions

def ordered_intersection(inputlist, sourcelist):
    '''
    Returns a list representing the intersection, maintaining the order in
    inputlist.
    '''
    return [x for x in inputlist if x in set(sourcelist)]

def make_mapping(inputlist, mapping):
    '''
    Returns a mapping (dictionary) for every item in list.
    '''
    ret = {}
    for i in range(len(inputlist)):
        key = inputlist[i]
        if key in mapping: ret[key] = mapping[key]
        else: ret[key] = key
    return ret
