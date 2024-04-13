import resizeImage
import Kernel

k = Kernel.Kernel()
resizeImage.ResizeImage("dog.jpg", "_id", k.getIdentity())
resizeImage.ResizeImage("dog.jpg", "_rid", k.getRidge())
