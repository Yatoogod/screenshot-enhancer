import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image, ImageDraw, ImageFilter
import io

# Your updated Telegram bot token
TOKEN = '6264504776:AAFPKj38UwNcA_ARSk0ZlLfc2nlJtxfPbGU'

# Function to add curved corners to the image
def add_rounded_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)
    image.putalpha(mask)
    return image

# Function to add a thicker border around the image
def add_border(image, border_color=(0, 0, 0), border_thickness=5):  # Increased thickness to 5
    draw = ImageDraw.Draw(image)
    width, height = image.size
    draw.rounded_rectangle((border_thickness // 2, border_thickness // 2, width - border_thickness // 2, height - border_thickness // 2),
                           radius=15, outline=border_color, width=border_thickness)
    return image

# Function to create a smooth gradient background from red to pink to purple
def create_gradient_background(width, height):
    gradient = Image.new('RGB', (width, height), color=0)
    draw = ImageDraw.Draw(gradient)

    # Starting colors: Red to Pink to Purple
    start_color = (255, 0, 0)      # Red
    mid_color = (255, 105, 180)    # Pink
    end_color = (128, 0, 128)      # Purple

    # Draw gradient for each line (smooth transition)
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            # Red to Pink
            r = int(start_color[0] + ratio * 2 * (mid_color[0] - start_color[0]))
            g = int(start_color[1] + ratio * 2 * (mid_color[1] - start_color[1]))
            b = int(start_color[2] + ratio * 2 * (mid_color[2] - start_color[2]))
        else:
            # Pink to Purple
            ratio2 = (ratio - 0.5) * 2
            r = int(mid_color[0] + ratio2 * (end_color[0] - mid_color[0]))
            g = int(mid_color[1] + ratio2 * (end_color[1] - mid_color[1]))
            b = int(mid_color[2] + ratio2 * (end_color[2] - mid_color[2]))
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return gradient

# Function to enhance the screenshot by adding a colorful gradient background, curved corners, and a thick border
def enhance_image(screenshot):
    width, height = screenshot.size

    # Zoom the screenshot (scale up by 25%)
    zoom_factor = 1.25
    new_size = (int(width * zoom_factor), int(height * zoom_factor))
    screenshot = screenshot.resize(new_size, Image.LANCZOS)  # Use LANCZOS for high-quality resizing

    # Add rounded corners to the screenshot
    radius = 15  # Reduced the corner radius to make the corners less rounded
    screenshot = add_rounded_corners(screenshot, radius)

    # Add a thicker border around the screenshot
    border_thickness = 5  # Increased the border thickness to make it more noticeable
    border_color = (0, 0, 0)  # Black border, change to your desired color
    screenshot = add_border(screenshot, border_color=border_color, border_thickness=border_thickness)

    # Create the colorful gradient background
    background = create_gradient_background(new_size[0] + 200, new_size[1] + 200)

    # Create a new RGBA image to hold the combined result
    combined_image = Image.new("RGBA", background.size, (255, 255, 255, 0))

    # Calculate offset for centering the screenshot
    offset = ((background.width - screenshot.width) // 2, (background.height - screenshot.height) // 2)

    # Paste the screenshot with rounded corners and a thick border on the gradient background
    combined_image.paste(screenshot, offset, screenshot)

    # Merge the RGBA image with the gradient background
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
