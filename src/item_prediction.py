from fastapi import FastAPI, File, UploadFile
import io
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms


def get_class_names_dict(filename):
    class_names = {}
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            class_idx = int(line.split(':')[0])
            name = line.split(':')[1]
            name = name[2:-3]
            class_names[class_idx] = name
    return class_names


def get_class_prices_list(filename):
    pass


def preprocessing(img):
    transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    img = transform(img)
    img = img.unsqueeze(0)
    return img


def predict(img):
    out = model(img)
    _, class_idx = torch.max(out, 1)
    class_idx = class_idx[0].item()

    softmax = nn.Softmax(dim=1)
    out = softmax(out)
    class_name = class_names[class_idx]
    percentage = out[0, class_idx].item() * 100

    return {
        'class name': class_name,
        'percentage': percentage
    }


class_names = get_class_names_dict('class_names.txt')

model = models.resnet101(pretrained=False)
model.load_state_dict(torch.load('resnet101.pt'))
model.eval()

app = FastAPI()

@app.post('/')
async def get_info(file: UploadFile = File(...)):
    print(file.filename)

    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))
    img.show()

    img = preprocessing(img)

    out = predict(img)

    return out

# @app.get('/')
# def read_root():
#     return {'Hello': 'World'}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id + 10}


# if __name__ == '__main__':

#     img = Image.open('sample0.jpg').convert('RGB')
#     img = preprocessing(img)
#     out = predict(img)
#     print(out)
