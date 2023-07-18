from js import document, console, Uint8Array, window, File
from pyodide import create_proxy
import io
from PIL import Image, ImageFilter

current_filter_name = "EMBOSS"
current_uploaded_image = ""

async def select_filter_and_display(e):
    global current_filter_name
    current_filter_name = e.target.value
    await upload_change_and_show(current_uploaded_image)

def remove_all_children(parent_id: str):
    parent = document.getElementById(parent_id)

    while parent.firstChild is not None:
        parent.removeChild(parent.firstChild)

async def upload_change_and_show(e):
    global current_uploaded_image
    current_uploaded_image = e

    # Get the first file from upload
    file = e.target.files.item(0)

    # Get the data from the files arrayBuffer as an array of unsigned bytes
    array_buf = Uint8Array.new(await file.arrayBuffer())
    my_bytes = io.BytesIO(bytearray(array_buf))

    # Create PIL image from byte stream
    my_image = Image.open(my_bytes)

    # Duplicate original image
    my_original_image = my_image.copy()

    # Print the width and height
    width, height = my_image.size

    # Log some of the image data for testing
    console.log(f"{my_image.format= } {my_image.width= } {my_image.height= }")

    # Now that we have the image loaded with PIL, we can use all the tools it makes available. 
    # Apply chosen filter to the image, rotate 45 degrees, fill with dark green
    my_image = my_image.filter(getattr(ImageFilter, current_filter_name)).resize((width,height))

    # Resize the original image
    my_original_image = my_original_image.resize((width,height))

    # Convert Pillow image objects back into File type that createObjectURL will take
    image_file = convert_image_to_file(my_image, "new_image_file.png")
    original_image_file = convert_image_to_file(my_original_image, "new_original_image_file.png")

    #remove all children from divs
    remove_all_children("output_upload_pillow")
    remove_all_children("original_image")

    # Create new tags and insert into page
    insert_image_into_page(image_file, "output_upload_pillow")
    insert_image_into_page(original_image_file, "original_image")

def convert_image_to_file(image, filename):
    my_stream = io.BytesIO()
    image.save(my_stream, format="PNG")
    return File.new([Uint8Array.new(my_stream.getvalue())], filename, {type: "image/png"})

def insert_image_into_page(image_file, element_id):
    new_image = document.createElement('img')
    new_image.src = window.URL.createObjectURL(image_file)
    new_image.className = 'output_image'
    document.getElementById(element_id).appendChild(new_image)


# Bind event handlers
document.getElementById("filter-selector").addEventListener("change", create_proxy(select_filter_and_display))
document.getElementById("file-upload-pillow").addEventListener("change", create_proxy(upload_change_and_show))
