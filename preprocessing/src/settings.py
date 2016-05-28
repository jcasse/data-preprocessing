import os
import yaml
from pkg_resources import Requirement, resource_filename

def load_settings(name=None):
    '''
    Load settings dictionary.

    Returns a dict containing settings for data cleaning.

    Parameters
    ----------
    name : string, optional
        Specifies the settings to load. The default is None, which results in
        loading default settings. Alternative settings may be specified by name;
        run vppreprocess.show_available_settings() to get a list of available
        settings.
    '''
    if name is None:
        filename = resource_filename(Requirement.parse("vppreprocess"),
                                     "vppreprocess/data/settings_2015-11-06.yaml")
    else:
        settings_rel_path = os.path.join("vppreprocess/data", name)
        filename = resource_filename(Requirement.parse("vppreprocess"),
                                     settings_rel_path)
    settings = yaml.load(file(filename, 'r'))
    return(settings)

def show_available_settings():
    '''
    Load settings dictionary.

    Returns a dict containing settings for data cleaning.

    '''
    data_path = resource_filename(Requirement.parse("vppreprocess"),"vppreprocess/data/")
    available = subprocess.check_output(['ls', data_path]).split()
    return(available)
