import ipywidgets as widgets
from tkinter import messagebox
from tkinter import filedialog
from customtkinter import *
from PIL import Image, ImageTk
import cv2
import matplotlib.pyplot as plt
import pytesseract
import easyocr
import os
from PIL import Image
from groq import Groq
from paddleocr import PaddleOCR, draw_ocr

# Create the main window
root = CTk()
root.title("AutoGrader")
root.attributes('-fullscreen', True)

selected_regions = []  # Stores (question_box, answer_box) tuples
current_selection = []  # Temporary storage for question or answer box

# Mouse event variables
start_x, start_y = None, None
drawing = False
canvas = None
image_tk = None  # Store image for canvas
image_cv = None  # OpenCV image reference

def update_image(file_path):
    global canvas, image_tk, image_cv

    # Open the image and store it
    img = Image.open(file_path)

    a4_width, a4_height = 595, 842
    scale_factor = 0.8  # Scale image to 80% of A4 size
    width, height = int(a4_width * scale_factor), int(a4_height * scale_factor)

    # Resize the image to fit within the scaled-down A4 resolution
    img = img.resize((width, height))

    # Convert the image to a format usable by Tkinter
    image_tk = ImageTk.PhotoImage(img)  

    # Destroy previous canvas if it exists
    if canvas:
        canvas.destroy()

    # Create a new canvas with correct dimensions
    canvas = CTkCanvas(root, width=width, height=height)
    canvas.place(relx=0.5, rely=0.5, anchor="center")  # Adjusted position

    # Display the image properly
    canvas.create_image(width//2, height//2, anchor="center", image=image_tk)

    # Bind mouse events for rectangle selection
    canvas.bind("<ButtonPress-1>", start_drawing)
    canvas.bind("<B1-Motion>", draw_rectangle)
    canvas.bind("<ButtonRelease-1>", stop_drawing)

    # Create buttons again after the canvas is updated
    create_buttons()

def create_buttons():
    # Create the buttons after image is updated to avoid being covered
    print_btn = CTkButton(master=root, text="Print Q&A Boxes", command=print_selected_regions)
    print_btn.place(relx=0.40, rely=0.85, anchor="center")

    redo_btn = CTkButton(master=root, text="REDO", command=redo)
    redo_btn.place(relx=0.50, rely=0.85, anchor="center")

    finish_btn = CTkButton(master=root, text="Finish", command=finish)
    finish_btn.place(relx=0.60, rely=0.85, anchor="center")

    label_instruction = CTkLabel(master=root, text="Highlight the question then the area where its answer belong", text_color="white")
    label_instruction.place(relx=0.5, rely=0.15, anchor="center")

def upload_file():
    global image_cv, image_tk, canvas
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(title="Select a file")
    if file_path:
        print(f"File selected: {file_path}")
        btn.place_forget()  # Hide the upload button
        update_image(file_path)
    
def start_drawing(event):
    global start_x, start_y, drawing
    start_x, start_y = event.x, event.y
    drawing = True

def draw_rectangle(event):
    if not drawing:
        return
    canvas.delete("preview")
    canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red", tags="preview")

def stop_drawing(event):
    global current_selection, selected_regions, drawing

    if not drawing:
        return

    end_x, end_y = event.x, event.y
    selected_box = (start_x, start_y, end_x, end_y)
    current_selection.append(selected_box)

    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="blue", width=2, tags="highlight")

    if len(current_selection) == 2:
        selected_regions.append(tuple(current_selection))
        current_selection = []
    drawing = False

def print_selected_regions():
    print("Selected Q&A Boxes:")
    for i, (q_box, a_box) in enumerate(selected_regions):
        print(f"Q{i+1}: {q_box}, A{i+1}: {a_box}")

def redo():
    global selected_regions, current_selection, canvas
    if selected_regions:
        selected_regions = selected_regions[:-1]
        if current_selection:
            current_selection = []

        canvas.delete("highlight")
        for q_box, a_box in selected_regions:
            canvas.create_rectangle(q_box[0], q_box[1], q_box[2], q_box[3], outline="blue", width=2, tags="highlight")
            canvas.create_rectangle(a_box[0], a_box[1], a_box[2], a_box[3], outline="blue", width=2, tags="highlight")

        canvas.bind("<ButtonPress-1>", start_drawing)
        canvas.bind("<B1-Motion>", draw_rectangle)
        canvas.bind("<ButtonRelease-1>", stop_drawing)

def finish():
    pass

label = CTkLabel(master=root, text="No File has been chosen")
label.place(relx=0.5, rely=0.55, anchor="center")

btn = CTkButton(master=root, width=200, height=50, text="Upload Empty Worksheet", corner_radius=40, fg_color="#0080FE", hover_color="#FFFFFF", text_color="#000000", command=upload_file)
btn.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()
