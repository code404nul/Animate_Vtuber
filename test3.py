from utils.manage_model import ModelManager

model = ModelManager("mao")

print([i["Name"] for i in model.expressions])