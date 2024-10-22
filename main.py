import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image, ImageDraw
import io

# Your updated Telegram bot token
TOKEN = '6454133526:AAFMG9qJUO1RziEY4s_DzursYY4351dOnD8'

# Function to add curved corners to the image
def add_rounded_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)
    image.putalpha(mask)
    return image

# Function to create a smooth gradient background from red to purple
def create_gradient_background(width, height):
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)

    # Colors for gradient (Red to Purple)
    start_color = (255, 0, 0)  # Red
    end_color = (128, 0, 128)  # Purple

    # Generate gradient
    for y in range(height):
        ratio = y / height
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return gradient

# Function to enhance the screenshot by adding a red-to-purple gradient background and curved corners (no border)
def enhance_image(screenshot):
    width, height = screenshot.size

    # Zoom the screenshot (scale up by 25%)
    zoom_factor = 1.25
    new_size = (int(width * zoom_factor), int(height * zoom_factor))
    screenshot = screenshot.resize(new_size, Image.LANCZOS)  # Use LANCZOS for high-quality resizing

    # Add rounded corners to the screenshot
    radius = 15  # Reduced the corner radius to make the corners less rounded
    screenshot = add_rounded_corners(screenshot, radius)

    # Create the red-to-purple gradient background
    background = create_gradient_background(new_size[0] + 200, new_size[1] + 200)

    # Calculate offset for centering the screenshot
    offset = ((background.width - screenshot.width) // 2, (background.height - screenshot.height) // 2)

    # Paste the screenshot with rounded corners on the gradient background
    background.paste(screenshot, offset, screenshot)

    return background

# Handle images (screenshots)
def handle_image(update, context):
    photo_file = update.message.photo[-1].get_file()  # Get the largest available photo
    photo_stream = io.BytesIO()
    photo_file.download(out=photo_stream)

    # Open the image
    photo_stream.seek(0)
    screenshot = Image.open(photo_stream)

    # Enhance the screenshot
    enhanced_image = enhance_image(screenshot)

    # Save the image to a BytesIO stream
    output_stream = io.BytesIO()
    enhanced_image.save(output_stream, format='PNG')
    output_stream.seek(0)

    # Send the enhanced image back to the user
    update.message.reply_photo(photo=InputFile(output_stream, filename="enhanced_image.png"))

# Main function to run the bot
def main():
    # Create the Updater and pass your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
