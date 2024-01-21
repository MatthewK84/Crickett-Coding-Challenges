import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, font
from PIL import Image, ImageTk, ImageEnhance
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Initialize the main window
root = tk.Tk()
root.title("LinkedIn Carousel Generator")
root.geometry("1200x800")

# Slide structure
class Slide:
    def __init__(self, text="", image=None, bg_image=None):
        self.text = text
        self.image = image
        self.bg_image = bg_image

# List to store slides
slides = [Slide()]

# Current slide index
current_slide_index = 0

# Function to update the slide preview
def update_preview():
    if slides:
        slide = slides[current_slide_index]
        slide.text = text_entry.get("1.0", "end-1c")
        preview_canvas.delete("all")
        preview_canvas.config(bg=bg_color)
        if slide.bg_image:
            tk_bg_image = ImageTk.PhotoImage(slide.bg_image)
            preview_canvas.create_image(270, 270, image=tk_bg_image)
        preview_canvas.create_text(270, 270, text=slide.text, font=(font_family.get(), int(font_size.get())), fill=fg_color, width=500)
        if slide.image:
            preview_canvas.create_image(50, 50, image=slide.image, anchor="nw")

# Function to switch slides
def switch_slide(index):
    global current_slide_index
    current_slide_index = index
    slide = slides[index]
    text_entry.delete("1.0", tk.END)
    text_entry.insert(tk.END, slide.text)
    update_preview()

# Function to add a new slide
def add_slide():
    slides.append(Slide())
    slide_selector['values'] = list(range(len(slides)))
    switch_slide(len(slides) - 1)

# Function to upload and display the profile image
# Use a frame for better organization of widgets
control_frame = tk.Frame(root)
control_frame.pack(pady=20)

def upload_image():
    global profile_photo
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image = Image.open(file_path)
        image = image.resize((150, 150), Image.ANTIALIAS)
        profile_photo = ImageTk.PhotoImage(image)
        update_preview()

# Add a slide selector dropdown
slide_selector = ttk.Combobox(control_frame, values=list(range(len(slides))))
slide_selector.set("0")
slide_selector.grid(row=3, column=0, padx=5, pady=5)

# Add button to add new slide
add_slide_button = tk.Button(control_frame, text="Add Slide", command=add_slide)
add_slide_button.grid(row=3, column=1, padx=5, pady=5)

# Function to choose background color
def choose_bg_color():
    global bg_color
    color_code = colorchooser.askcolor(title="Choose background color")
    bg_color = color_code[1]
    update_preview()

# Function to choose foreground color
def choose_fg_color():
    global fg_color
    color_code = colorchooser.askcolor(title="Choose text color")
    fg_color = color_code[1]
    update_preview()

# Use a frame for better organization of widgets
control_frame = tk.Frame(root)
control_frame.pack(pady=20)

# Add a text box for user input
text_entry = tk.Text(control_frame, height=5, width=60)
text_entry.grid(row=0, column=0, columnspan=3, pady=5)

# Add a button to upload the profile image
upload_button = tk.Button(control_frame, text="Upload Profile Image", command=upload_image)
upload_button.grid(row=1, column=0, padx=5, pady=5)

# Add color picker buttons
bg_color_button = tk.Button(control_frame, text="Background Color", command=choose_bg_color)
bg_color_button.grid(row=1, column=1, padx=5, pady=5)

fg_color_button = tk.Button(control_frame, text="Text Color", command=choose_fg_color)
fg_color_button.grid(row=1, column=2, padx=5, pady=5)

# Dropdown for font selection
font_family = ttk.Combobox(control_frame, values=font.families())
font_family.set("Arial")
font_family.grid(row=2, column=0, padx=5, pady=5)

# Dropdown for font size selection
font_size = ttk.Combobox(control_frame, values=list(range(8, 60)))
font_size.set("24")
font_size.grid(row=2, column=1, padx=5, pady=5)

# Add button to add new slide
# Function to export slides as PDF
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def export_as_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, "wb") as f:
            pdf = canvas.Canvas(f)
            for slide in slides:
                if slide.bg_image:
                    pdf.drawImage(slide.bg_image.filename, 0, 0, width=pdf._pagesize[0], height=pdf._pagesize[1])
                pdf.setFont(font_family.get(), int(font_size.get()))
                pdf.setFillColorRGB(*hex_to_rgb(bg_color))
                pdf.drawString(50, 50, slide.text)
                if profile_photo:
                    pdf.drawImage(profile_photo.filename, 400, 50, width=100, height=100)
                pdf.showPage()
            pdf.save()
global bg_color
bg_color = 'white'

preview_canvas = tk.Canvas(root, width=540, height=540, bg=bg_color)
preview_canvas.pack(pady=20)

# Initialize the profile photo, background color, and foreground color
profile_photo = None
bg_color = 'white'
fg_color = 'black'

# Run the application
root.mainloop()