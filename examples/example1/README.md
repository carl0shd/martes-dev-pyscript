
## Example 1 - Image manipulation and processing

This example is a basic demonstration of how Pyscript works. Is a Python script that takes an image as input and uses the Pillow library to apply various pre-defined filters to it. The modified image is then sent back to the HTML to be displayed on the frontend.

## Step 1 - Create a new python file

Create a new Python file, e.g., main.py, and open it in a text editor or an integrated development environment (IDE) of your choice.

Import the necessary modules and libraries at the beginning of the file:

```python
from js import document, console, Uint8Array, window, File

from pyodide import create_proxy

import io

from PIL import Image, ImageFilter

```

## Step 2 - Adding code
Declare global variables to store the current filter name and uploaded image path:

```python
current_filter_name = "EMBOSS"
current_uploaded_image = ""
```

Define an asynchronous function to handle the filter selection and display:

```python
async def select_filter_and_display(e):
    global current_filter_name
    current_filter_name = e.target.value
    await upload_change_and_show(current_uploaded_image)
```

Create a helper function to remove all children from a specified parent element:

```python
def remove_all_children(parent_id: str):
    parent = document.getElementById(parent_id)

    while parent.firstChild is not None:
        parent.removeChild(parent.firstChild)
```

Implement a helper function to convert a Pillow image object into a File type:

```python
def convert_image_to_file(image, filename):
    my_stream = io.BytesIO()
    image.save(my_stream, format="PNG")
    return File.new([Uint8Array.new(my_stream.getvalue())], filename, {type: "image/png"})

```

Create another helper function to insert the image into the HTML page:

```python
def insert_image_into_page(image_file, element_id):
    new_image = document.createElement('img')
    new_image.src = window.URL.createObjectURL(image_file)
    new_image.className = 'output_image'
    document.getElementById(element_id).appendChild(new_image)

```

## Step 3 - Adding the main logic to apply the filters
Define another asynchronous function to handle the image upload, change, and display:

```python
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
    console.log(f"{my_image.format= } {my_image.width= } {my_image.height= }")

    # Apply chosen filter to the image
    my_image = my_image.filter(getattr(ImageFilter, current_filter_name)).resize((width, height))

    # Resize the original image
    my_original_image = my_original_image.resize((width, height))

    # Convert Pillow image objects back into File type that createObjectURL will take
    image_file = convert_image_to_file(my_image, "new_image_file.png")
    original_image_file = convert_image_to_file(my_original_image, "new_original_image_file.png")

    # Remove all children from divs
    remove_all_children("output_upload_pillow")
    remove_all_children("original_image")

    # Create new tags and insert into page
    insert_image_into_page(image_file, "output_upload_pillow")
    insert_image_into_page(original_image_file, "original_image")

```

## Step 4 - Adding the HTML listeners to call functions
Bind the event handlers to the respective elements in the HTML file:

```python
document.getElementById("filter-selector").addEventListener("change", create_proxy(select_filter_and_display))
document.getElementById("file-upload-pillow").addEventListener("change", create_proxy(upload_change_and_show))

```

## Step 5 - Try the code with your best photo :)
Now the last step is to try the code running the command to start the HTTP server:

```sh
python3 -m http.server
```