import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from rembg import remove
import io


class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("MacPhoto Editor - Advanced Photo Editing Tool")
        self.root.geometry("900x650")
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

        # Initialize variables
        self.image = None
        self.edited_image = None
        self.image_path = None
        self.crop_rectangle = None
        self.crop_start = None

        # Create UI Layout
        self.setup_ui()

    def setup_ui(self):
        # Main Canvas Area
        self.canvas = ctk.CTkCanvas(self.root, width=800, height=500, bg="#444444")
        self.canvas.pack(pady=20)

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_crop)

        # Buttons and Controls
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10)

        # Buttons
        ctk.CTkButton(button_frame, text="Open", command=self.open_image).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Save", command=self.save_image).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Grayscale", command=self.grayscale).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Rotate 90°", command=self.rotate_image).grid(row=0, column=3, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Reset", command=self.reset_image).grid(row=0, column=4, padx=10, pady=5)

        ctk.CTkButton(button_frame, text="Crop", command=self.start_crop_mode).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Remove Background", command=self.remove_background).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Change Background", command=self.change_background).grid(row=1, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Blur Filter", command=lambda: self.apply_filter("blur")).grid(row=1, column=3, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Sharpen Filter", command=lambda: self.apply_filter("sharpen")).grid(row=1, column=4, padx=10, pady=5)

        # Sliders for Brightness and Contrast
        ctk.CTkLabel(self.root, text="Brightness:").pack(pady=5)
        self.brightness_slider = ctk.CTkSlider(self.root, from_=0.5, to=2.0, command=self.adjust_brightness)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(fill="x", padx=20)

        ctk.CTkLabel(self.root, text="Contrast:").pack(pady=5)
        self.contrast_slider = ctk.CTkSlider(self.root, from_=0.5, to=2.0, command=self.adjust_contrast)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill="x", padx=20)

        # About Button
        ctk.CTkButton(self.root, text="About", command=self.show_about).pack(pady=10)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp *.tiff")])
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path).convert("RGBA")
            self.edited_image = self.image.copy()
            self.display_image()

    def save_image(self):
        if self.edited_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if file_path:
                self.edited_image.save(file_path)

    def display_image(self):
        if self.edited_image:
            image = self.edited_image.copy()
            image.thumbnail((800, 500))
            photo = ImageTk.PhotoImage(image)
            self.canvas.image = photo
            self.canvas.create_image(400, 250, image=photo)

    def grayscale(self):
        if self.edited_image:
            self.edited_image = self.edited_image.convert("L").convert("RGBA")
            self.display_image()

    def rotate_image(self):
        if self.edited_image:
            self.edited_image = self.edited_image.rotate(90, expand=True)
            self.display_image()

    def reset_image(self):
        if self.image:
            self.edited_image = self.image.copy()
            self.display_image()

    def adjust_brightness(self, value):
        if self.edited_image:
            enhancer = ImageEnhance.Brightness(self.image)
            self.edited_image = enhancer.enhance(float(value))
            self.display_image()

    def adjust_contrast(self, value):
        if self.edited_image:
            enhancer = ImageEnhance.Contrast(self.image)
            self.edited_image = enhancer.enhance(float(value))
            self.display_image()

    def start_crop_mode(self):
        self.crop_rectangle = None
        self.crop_start = None

    def start_crop(self, event):
        self.crop_start = (event.x, event.y)
        if self.crop_rectangle:
            self.canvas.delete(self.crop_rectangle)

    def draw_crop_rectangle(self, event):
        if self.crop_start:
            self.canvas.delete(self.crop_rectangle)
            self.crop_rectangle = self.canvas.create_rectangle(
                self.crop_start[0], self.crop_start[1], event.x, event.y, outline="red"
            )

    def finish_crop(self, event):
        if self.crop_start:
            x0, y0 = self.crop_start
            x1, y1 = event.x, event.y
            crop_box = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            if self.edited_image:
                crop_box_scaled = (
                    crop_box[0] * self.edited_image.width / 800,
                    crop_box[1] * self.edited_image.height / 500,
                    crop_box[2] * self.edited_image.width / 800,
                    crop_box[3] * self.edited_image.height / 500,
                )
                self.edited_image = self.edited_image.crop(crop_box_scaled)
                self.display_image()

    def remove_background(self):
        if self.edited_image:
            img_byte_arr = io.BytesIO()
            self.edited_image.save(img_byte_arr, format='PNG')
            img_data = remove(img_byte_arr.getvalue())
            self.edited_image = Image.open(io.BytesIO(img_data))
            self.display_image()

    def change_background(self):
        bg_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp *.tiff")])
        if bg_path:
            bg_image = Image.open(bg_path).resize(self.edited_image.size)
            self.edited_image = Image.alpha_composite(bg_image.convert("RGBA"), self.edited_image)
            self.display_image()

    def apply_filter(self, filter_type):
        if self.edited_image:
            if filter_type == "blur":
                self.edited_image = self.edited_image.filter(ImageFilter.BLUR)
            elif filter_type == "sharpen":
                self.edited_image = self.edited_image.filter(ImageFilter.SHARPEN)
            self.display_image()

    def show_about(self):
        about_window = Toplevel(self.root)
        about_window.title("About MacPhoto Editor")
        about_window.geometry("300x200")

        ctk.CTkLabel(
            about_window,
            text="MacPhoto Editor\n"
                 "Author: Shiboshree Roy\n"
                 "Version: 1.0.1"
        ).pack(pady=20)

        icon_path = "icon.png"  # Update with your icon file path
        try:
            icon_image = ImageTk.PhotoImage(file=icon_path)
            ctk.CTkLabel(about_window, image=icon_image).pack()
            about_window.iconphoto(False, icon_image)
        except Exception as e:
            print("Icon not found:", e)


if __name__ == "__main__":
    root = ctk.CTk()
    app = PhotoEditor(root)
    root.mainloop()
