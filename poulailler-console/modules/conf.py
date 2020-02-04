import yaml

def read_conf(fic_name):
    with open("conf/" + fic_name + ".conf", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader = yaml.Loader)
    return cfg

def write_conf(fic_name,content):
    with open("conf/" + fic_name + ".conf", 'w') as ymlfile:
        yaml.dump(content, ymlfile, Dumper = yaml.Dumper)
