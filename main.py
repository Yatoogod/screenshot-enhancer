import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image, ImageDraw, ImageFilter
import io

# Your Telegram bot token
TOKEN = '6264504776:AAFPKj38UwNcA_ARSk0ZlLfc2nlJtxfPbGU'

# Function to add curved corners to the image
def add_rounded_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)
    image.putalpha(mask)
    return image

# Function to create a plain white background
def create_white_background(width, height):
    return Image.new("RGB", (width, height), (255, 255, 255))  # White background

# Function to create shadow that follows the curved corners
def create_curved_shadow(image, radius, blur_radius=100, offset=(20, 20), shadow_color=(0, 0, 0, 128)):
    # Create a shadow by copying the shape of the rounded image and applying the blur
    shadow_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=shadow_color)

    # Apply a Gaussian blur to the shadow for the blur effect
    shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(blur_radius))

    # Create a new image to hold the shadow with the correct offset
    shadow_with_offset = Image.new("RGBA", (image.size[0] + offset[0], image.size[1] + offset[1]), (0, 0, 0, 0))
    shadow_with_offset.paste(shadow_image, offset, shadow_image)

    return shadow_with_offset

# Function to enhance the screenshot by adding a white background, curved corners, zoom, and realistic shadow
def enhance_image(screenshot):
    width, height = screenshot.size

    # Zoom the screenshot (scale up by 25%)
    zoom_factor = 1.25
    new_size = (int(width * zoom_factor), int(height * zoom_factor))
    screenshot = screenshot.resize(new_size, Image.LANCZOS)  # Use LANCZOS for high-quality resizing

    # Add rounded corners to the screenshot
    radius = 50
    screenshot = add_rounded_corners(screenshot, radius)

    # Create the white background
    background = create_white_background(new_size[0] + 200, new_size[1] + 200)

    # Create a shadow with pure black and 50% opacity
    shadow = create_curved_shadow(screenshot, radius, blur_radius=80, offset=(30, 30), shadow_color=(0, 0, 0, 128))

    # Create a new RGBA image to hold the combined result
    combined_image = Image.new("RGBA", background.size, (255, 255, 255, 0))

    # Calculate offset for centering the screenshot
    offset = ((background.width - screenshot.width) // 2, (background.height - screenshot.height) // 2)

    # Paste the shadow behind the screenshot
    shadow_offset = (offset[0] - 30, offset[1] - 30)  # Shadow offset for more visibility
    combined_image.paste(shadow, shadow_offset, shadow)

    # Paste the screenshot with rounded corners on top of the shadow
    combined_image.paste(screenshot, offset, screenshot)

    # Combine the RGBA image with the white background
    final_image = Image.alpha_composite(Image.new("RGBA", background.size, (255, 255, 255, 255)), combined_image).convert("RGB")

    return final_image

# Start command handler
def start(update, context):
    update.message.reply_text("Send me a screenshot to enhance!")

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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
