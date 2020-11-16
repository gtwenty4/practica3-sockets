import yaml

# Obtiene la configuración del archivo config_client.yml
def getConfig():
    with open("config_client.yml", "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config