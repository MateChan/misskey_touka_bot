import torch
from PIL import Image
from torch.nn import Module
from torchvision import transforms
from transformers import AutoModelForImageSegmentation


class BackgroundRemover:
    def __init__(self):
        self.model: Module = AutoModelForImageSegmentation.from_pretrained(
            "briaai/RMBG-2.0",
            trust_remote_code=True,
        )
        self.model.cuda()
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
        input_images = input_images.unsqueeze(0).cuda()

        with torch.no_grad():
            preds: torch.Tensor = self.model.forward(input_images)
            preds = preds[-1].sigmoid().cpu()

        pred = preds[0].squeeze()
        pred_pil: Image.Image = self.to_pil_image(pred)
        mask = pred_pil.resize(image.size)
        image.putalpha(mask)

        return image


if __name__ == "__main__":
    background_remover = BackgroundRemover()
    image = Image.open("./sample/input.jpg")
    no_bg_image = background_remover.remove_background(image)
    no_bg_image.save("./sample/out.webp")
