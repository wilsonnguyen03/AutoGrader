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
from tkinter import simpledialog
from PIL import Image
from groq import Groq
from paddleocr import PaddleOCR, draw_ocr

# Create the main window
root = CTk()
root.title("AutoGrader")
root.attributes('-fullscreen', True)

selected_regions = []  # Stores (question_box, answer_box) tuples
current_selection = []  # Temporary storage for question or answer box
answers = {}
s_answers = {}
mark = {}

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
    global finish_btn, print_btn, redo_btn
    # Create the buttons after image is updated to avoid being covered
    print_btn = CTkButton(master=root, text="Print Q&A Boxes", command=print_selected_regions)
    print_btn.place(relx=0.40, rely=0.85, anchor="center")

    redo_btn = CTkButton(master=root, text="REDO", command=redo)
    redo_btn.place(relx=0.5, rely=0.85, anchor="center")

    finish_btn = CTkButton(master=root, text="Provide answers for each Questions", command=finish)
    finish_btn.place(relx=0.6, rely=0.85, anchor="center")

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

def upload_file_student():
    global image_cv, image_tk, canvas
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(title="Select a file")
    if file_path:
        print(f"File selected: {file_path}")
        btn.place_forget()
    scan_answer(file_path)
    
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
    global selected_regions, current_selection, canvas, image_tk, image_cv, student_upload_btn, answer, finish_btn, print_btn, redo_btn
    finish_btn.configure(text = "Next")

    # Loop through the selected regions and ask for answers
    for index, (q, a) in enumerate(selected_regions):
        question = f"Question {index + 1}: Please provide key words or answers for the selected region"
        answer = simpledialog.askstring("Question", question)
        if answer:
            answers[f"answer{index + 1}"] = answer
        else:
            answers[f"answer{index + 1}"] = "Instantly wrong"

    for widget in root.winfo_children(): 
            widget.place_forget()

    student_upload_btn = CTkButton(master=root, width=200, height=50, text="Upload Student's Worksheet", corner_radius=40, fg_color="#0080FE", hover_color="#FFFFFF", text_color="#000000", command=upload_file_student)
    student_upload_btn.place(relx=0.5, rely=0.5, anchor="center")

def save_canvas():
    # Get the canvas dimensions
    canvas.postscript(file="temp_canvas.eps")  # Save as EPS (Encapsulated PostScript)
    
    # Convert EPS to PNG using Pillow
    img = Image.open("temp_canvas.eps")
    
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"),("JPEG files", "*.jpg"),("All Files", "*.*")])
    
    if file_path:
        img.save(file_path)  # Save as chosen format
        print("Image saved successfully:", file_path)

def marker(file_path):
    global canvas, image_tk, image_cv, tick_tk, cross_tk  # Store images globally


    # Load and resize overlay images
    tick = Image.open("tick.png").convert("RGBA")
    tick = tick.resize((15, 15))
    tick_tk = ImageTk.PhotoImage(tick)  # Store globally

    cross = Image.open("cross.png").convert("RGBA")
    cross = cross.resize((15, 15))
    cross_tk = ImageTk.PhotoImage(cross)  # Store globally

    # Load and resize the main image
    img = Image.open(file_path)
    a4_width, a4_height = 595, 842
    scale_factor = 0.8  
    width, height = int(a4_width * scale_factor), int(a4_height * scale_factor)
    img = img.resize((width, height))
    image_tk = ImageTk.PhotoImage(img)  

    # Destroy old canvas if it exists
    if 'canvas' in globals() and canvas.winfo_exists():
        canvas.destroy()

    # Create new canvas
    canvas = CTkCanvas(root, width=width, height=height)
    canvas.place(relx=0.5, rely=0.5, anchor="center")

    # Display the main image
    canvas.create_image(0, 0, anchor="nw", image=image_tk)

    # Iterate over answers and place markers
    for index, answer in enumerate(s_answers):
        x, y = 450, (selected_regions[index][1][1] + selected_regions[index][1][3])//2
        #print(answer, "student answer: ", s_answers[answer], " correct answer:", answers[answer])
        if s_answers[answer] == "Instantly wrong":
            mark[answer] = 'X'
            canvas.create_image(x, y, anchor="center", image=cross_tk)
        else:
            client = Groq(api_key="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")

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"I want you to compare the provided answer: {answers[answer]} with student answer: {s_answers[answer]}. If the answers meaning are the same or similar then return 'C' else return 'X' nothing else just C or X"
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            #print("chat: ", chat_completion.choices[0].message.content )
            if chat_completion.choices[0].message.content == "C":
                mark[answer] = "C"
                canvas.create_image(x, y, anchor="center", image=tick_tk)
            else:
                mark[answer] = "X"
                canvas.create_image(x, y, anchor="center", image=cross_tk)

    #print(answers)
    #print(s_answers)
    #print(mark)
    #print(selected_regions)
    download_btn = CTkButton(master=root,  height=50, text="Download Marked Version", corner_radius=40, fg_color="#0080FE", hover_color="#FFFFFF", text_color="#000000", command =save_canvas)
    download_btn.place(relx=0.425, rely=0.85, anchor="center")

    next_btn = CTkButton(master=root,height =50,  text="Upload another students work", corner_radius=40, fg_color="#0080FE", hover_color="#FFFFFF", text_color="#000000", command = upload_file_student)
    next_btn.place(relx=0.575, rely=0.85, anchor="center")

def scan_answer(file_path):
    global s_answers, answers
    s_answers = {}

    img = Image.open(file_path)
    a4_width, a4_height = 595, 842
    scale_factor = 0.8  # Scale image to 80% of A4 size
    width, height = int(a4_width * scale_factor), int(a4_height * scale_factor)
    # Resize the image to fit within the scaled-down A4 resolution
    img = img.resize((width, height))

    # Define the base folder name
    base_folder = 'student'
    # Get a list of existing folders that match the pattern "studentX"
    existing_folders = [f for f in os.listdir() if f.startswith(base_folder)]
    # Find the highest number used and increment it
    folder_numbers = [int(f.replace(base_folder, '')) for f in existing_folders if f[len(base_folder):].isdigit()]
    next_number = max(folder_numbers, default=0) + 1  # default=0 to handle the case where no folder exists
    # Create the new folder
    new_folder = f'{base_folder}{next_number}'
    os.makedirs(new_folder, exist_ok=True)
    #print(f"Folder '{new_folder}' created successfully.")

    answer_counter = 1
    for index, (q, a) in enumerate(selected_regions):
        cropped_image = img.crop((a[0], a[1], a[2], a[3]))
        image_path = os.path.join(new_folder, f"answer{answer_counter}.jpg")  # Change the extension if needed
        cropped_image.save(image_path)

        """
        Recognition model
        """
        image = cv2.imread(image_path)

        # Using Tesseract OCR
        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
        extracted_text1 = pytesseract.image_to_string(image, config="--psm 6")

        # Using EasyOCR
        reader = easyocr.Reader(["en"])
        results = reader.readtext(image)  # Extracted text from EasyOCR
        extracted_text2 = [text for (_, text, _) in results]

        # Using PaddleOCR
        ocr = PaddleOCR(use_angle_cls=False, lang='en')
        image = cv2.imread(image_path)
        result = ocr.ocr(image, cls=True)
        extracted_text3 = ''
        for line in result[0]:
            extracted_text3 += line[1][0] + '\n'

        # Groq API to process and combine the extracted texts
        client = Groq(api_key="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")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"I have three handwriting recognition texts, 1: {extracted_text1}, 2: {extracted_text2} and 3:{extracted_text3} . I want you to decypher these two text without changing its meaning or any words. Keep its originality. These two text are handwriting recognition from the same text so I want you to only output the outcome only nothing else, no extra prompts and only output it once",
                }
            ],
            model="llama-3.3-70b-versatile",    
        )

        #Save the chat completion response as a text file
        text_file_path = os.path.join(new_folder, f"answer{answer_counter}.txt")
        with open(text_file_path, "w") as text_file:
            text_file.write(chat_completion.choices[0].message.content)
        
        s_answers[f"answer{index + 1}"] = chat_completion.choices[0].message.content

        # Increment the answer counter
        answer_counter += 1

    student_upload_btn.place_forget()  # Assuming this is a GUI element to hide the button after scan
    #print("Answers:" , answers)
    #print("Student Answers:" , s_answers)
    marker(file_path)

label = CTkLabel(master=root, text= "Please upload a A4 scan of the blank worksheet")
label.place(relx=0.5, rely=0.55, anchor="center")

btn = CTkButton(master=root, width=200, height=50, text="Upload Empty Worksheet", corner_radius=40, fg_color="#0080FE", hover_color="#FFFFFF", text_color="#000000", command=upload_file)
btn.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()
