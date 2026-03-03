import warnings
from abc import ABC, abstractmethod

import torch
from ben2 import AutoModel
from PIL import Image
from s3od import BackgroundRemoval as S3ODModel
from torch.nn import Module
from torchvision import transforms
from transformers import AutoModelForImageSegmentation


class BackgroundRemover(ABC):
    @abstractmethod
    def remove_background(self, image: Image.Image) -> Image.Image:
        pass


class S3OD(BackgroundRemover):
    def __init__(self, device: torch.device):
        self.model = S3ODModel(device=str(device))

    def remove_background(self, image: Image.Image) -> Image.Image:
        result = self.model.remove_background(image)
        return result.rgba_image


class BEN2(BackgroundRemover):
    def __init__(self, device: torch.device):
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            module="torch",
            message=r"torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument.",
        )
        model = AutoModel.from_pretrained("PramaLLC/BEN2")
        assert model is not None
        self.model = model
        self.model.to(device)
        self.model.eval()

    def remove_background(self, image: Image.Image) -> Image.Image:
        foreground = self.model.inference(image, refine_foreground=True)
        assert isinstance(foreground, Image.Image)
        return foreground


class BiRefNet(BackgroundRemover):
    def __init__(self, device: torch.device):
        self.model: Module = AutoModelForImageSegmentation.from_pretrained(
            "briaai/RMBG-2.0",
            trust_remote_code=True,
        )
        self.device = device
        self.model.to(device)
        self.model.eval()
        self.to_pil_image = transforms.ToPILImage()
        self.resize = transforms.Resize((1024, 1024))
        self.to_tensor = transforms.ToTensor()
        self.normalize = transforms.Normalize(
            (0.485, 0.456, 0.406),
            (0.229, 0.224, 0.225),
        )

    def remove_background(self, image: Image.Image) -> Image.Image:
        input_images = self.resize.forward(image)
        input_images = self.to_tensor(input_images)
        input_images = self.normalize.forward(input_images)
        input_images = input_images.unsqueeze(0).to(self.device)

        with torch.no_grad():
            preds: torch.Tensor = self.model.forward(input_images)
            preds = preds[-1].sigmoid().cpu()

        pred = preds[0].squeeze()
        pred_pil: Image.Image = self.to_pil_image(pred)
        mask = pred_pil.resize(image.size)
        image.putalpha(mask)

        return image


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    background_remover = S3OD(device)
    image = Image.open("./sample/input.jpg")
    no_bg_image = background_remover.remove_background(image)
    no_bg_image.save("./sample/out.webp")
