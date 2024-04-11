from PIL import Image

im = Image.open("image/dog1.jpg")
px = im.load()
w = im.size[0]
h = im.size[1]
print(w, h)
for i in range(w):
    for j in range(h):
        px[i, j] = (int(px[i, j][0] / 9), int(px[i, j][1] / 9), int(px[i, j][2] / 9))
im.save("image/dog1_t.jpg")
