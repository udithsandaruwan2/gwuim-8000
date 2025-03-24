from PIL import Image

# Open the .png file
img = Image.open("app_icon.png")

# Save as .ico file
img.save("app_icon.ico")
