import yaml
import Jetson.GPIO as GPIO



def read_yaml(file_path: str) -> dict:
    """
    Safely reads a yaml-file.
    
    Parameters
    ----------
    file_path : str
        File path to YAML-file.
    
    Returns
    -------
    dict
        Loaded YAML-file.
    """
    with open(file_path, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return {}
