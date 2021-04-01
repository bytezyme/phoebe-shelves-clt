import configparser


def read_configs(config_path):
    configs = configparser.ConfigParser()
    configs.read(config_path)
    return(configs)


def update_configs(config_path, update_dict):

    configs = configparser.ConfigParser()
    for section, key_value_dict in update_dict.items():
        configs[section] = key_value_dict

    with open(config_path, 'w') as config_file:
        configs.write(config_file)
