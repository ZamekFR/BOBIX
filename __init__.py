import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from math import cos, sin, radians, sqrt, atan2, degrees


class DraftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BOBIX building 360")

        # Canvas for drawing
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables to store start position and color
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.color = "black"
        self.fill_color = None
        self.grid_size = 20
        self.rotation_angle = 0
        self.ortho_mode = False
        self.snap_to_grid = True
        self.selected_tool = None
        self.show_grid = True
        self.shapes = []
        self.layers = {'default': []}
        self.current_layer = 'default'

        # Setting up the menu
        self.setup_menu()

        # Adding Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.draw_rectangle_button = ttk.Button(button_frame, text="Draw Rectangle", command=self.select_rectangle)
        self.draw_rectangle_button.pack(side=tk.LEFT)

        self.draw_line_button = ttk.Button(button_frame, text="Draw Line", command=self.select_line)
        self.draw_line_button.pack(side=tk.LEFT)

        self.color_button = ttk.Button(button_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT)

        self.fill_color_button = ttk.Button(button_frame, text="Choose Fill Color", command=self.choose_fill_color)
        self.fill_color_button.pack(side=tk.LEFT)

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT)

        self.grid_button = ttk.Button(button_frame, text="Toggle Grid", command=self.toggle_grid)
        self.grid_button.pack(side=tk.LEFT)

        self.rotate_button = ttk.Button(button_frame, text="Rotate 15°", command=self.rotate_shape)
        self.rotate_button.pack(side=tk.LEFT)

        self.ortho_button = ttk.Button(button_frame, text="Ortho Mode", command=self.toggle_ortho)
        self.ortho_button.pack(side=tk.LEFT)

        self.add_layer_button = ttk.Button(button_frame, text="Add Layer", command=self.add_layer)
        self.add_layer_button.pack(side=tk.LEFT)

        self.layer_menu = ttk.Combobox(button_frame, values=list(self.layers.keys()), state='readonly')
        self.layer_menu.set('default')
        self.layer_menu.pack(side=tk.LEFT)
        self.layer_menu.bind("<<ComboboxSelected>>", self.change_layer)

        # Binding keyboard shortcuts
        self.root.bind('<Control-r>', lambda event: self.select_rectangle())
        self.root.bind('<Control-l>', lambda event: self.select_line())
        self.root.bind('<Control-c>', lambda event: self.choose_color())
        self.root.bind('<Control-f>', lambda event: self.choose_fill_color())
        self.root.bind('<Control-g>', lambda event: self.toggle_grid())
        self.root.bind('<Control-x>', lambda event: self.clear_canvas())
        self.root.bind('<Control-o>', lambda event: self.toggle_ortho())
        self.root.bind('<Control-t>', lambda event: self.rotate_shape())
        self.root.bind('<Control-n>', lambda event: self.add_layer())

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.draw_grid()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Grid", command=self.toggle_grid, accelerator="Ctrl+G")
        view_menu.add_command(label="Ortho Mode", command=self.toggle_ortho, accelerator="Ctrl+O")
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menu_bar)

    def select_rectangle(self):
        self.selected_tool = "rectangle"

    def select_line(self):
        self.selected_tool = "line"

    def choose_color(self):
        self.color = colorchooser.askcolor()[1]

    def choose_fill_color(self):
        self.fill_color = colorchooser.askcolor()[1]

    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes = []
        self.layers = {'default': []}
        self.current_layer = 'default'
        self.layer_menu['values'] = list(self.layers.keys())
        self.layer_menu.set('default')
        if self.show_grid:
            self.draw_grid()

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.clear_canvas()
        if self.show_grid:
            self.draw_grid()

    def toggle_ortho(self):
        self.ortho_mode = not self.ortho_mode

    def add_layer(self):
        new_layer = f"layer_{len(self.layers) + 1}"
        self.layers[new_layer] = []
        self.layer_menu['values'] = list(self.layers.keys())
        self.layer_menu.set(new_layer)
        self.current_layer = new_layer

    def change_layer(self, event):
        self.current_layer = self.layer_menu.get()

    def draw_grid(self):
        if self.show_grid:
            for i in range(0, self.canvas.winfo_width(), self.grid_size):
                self.canvas.create_line([(i, 0), (i, self.canvas.winfo_height())], tag='grid_line', fill='gray', dash=(2, 2))
            for i in range(0, self.canvas.winfo_height(), self.grid_size):
                self.canvas.create_line([(0, i), (self.canvas.winfo_width(), i)], tag='grid_line', fill='gray', dash=(2, 2))

    def on_button_press(self, event):
        self.start_x = self.snap(event.x) if self.snap_to_grid else event.x
        self.start_y = self.snap(event.y) if self.snap_to_grid else event.y
        self.current_x = self.start_x
        self.current_y = self.start_y

    def snap(self, value):
        return round(value / self.grid_size) * self.grid_size

    def on_move_press(self, event):
        self.canvas.delete("preview")
        x, y = (self.snap(event.x), self.snap(event.y)) if self.snap_to_grid else (event.x, event.y)
        if self.ortho_mode and self.selected_tool == "line":
            if abs(x - self.start_x) > abs(y - self.start_y):
                y = self.start_y
            else:
                x = self.start_x
        self.current_x, self.current_y = x, y
        if self.selected_tool == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline=self.color, fill=self.fill_color, tag="preview")
        elif self.selected_tool == "line":
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.color, tag="preview")
            length = sqrt((x - self.start_x)**2 + (y - self.start_y)**2)
            self.canvas.create_text((self.start_x + x) // 2, (self.start_y + y) // 2, text=f"{length:.2f}", tag="preview")

    def on_button_release(self, event):
        self.canvas.delete("preview")
        if self.selected_tool == "rectangle":
            rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.current_x, self.current_y, outline=self.color, fill=self.fill_color)
            self.shapes.append((rect, "rectangle", self.start_x, self.start_y, self.current_x, self.current_y, self.color, self.fill_color, self.current_layer))
            self.layers[self.current_layer].append((rect, "rectangle", self.start_x, self.start_y, self.current_x, self.current_y, self.color, self.fill_color))
        elif self.selected_tool == "line":
            line = self.canvas.create_line(self.start_x, self.start_y, self.current_x, self.current_y, fill=self.color)
            self.shapes.append((line, "line", self.start_x, self.start_y, self.current_x, self.current_y, self.color, self.current_layer))
            self.layers[self.current_layer].append((line, "line", self.start_x, self.start_y, self.current_x, self.current_y, self.color))
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None

    def rotate_shape(self):
        if self.shapes:
            shape = self.shapes.pop()
            shape_id, shape_type, x1, y1, x2, y2, color, *fill_color, layer = shape
            self.rotation_angle += 15
            if shape_type == "rectangle":
                self.canvas.delete(shape_id)
                new_coords = self.rotate_rectangle(x1, y1, x2, y2, self.rotation_angle)
                rect = self.canvas.create_polygon(new_coords, outline=color, fill=fill_color[0] if fill_color else "")
                self.shapes.append((rect, shape_type, x1, y1, x2, y2, color, *fill_color, layer))
                self.layers[layer].append((rect, shape_type, x1, y1, x2, y2, color, *fill_color))
            elif shape_type == "line":
                self.canvas.delete(shape_id)
                new_coords = self.rotate_line(x1, y1, x2, y2, self.rotation_angle)
                line = self.canvas.create_line(new_coords, fill=color)
                self.shapes.append((line, shape_type, x1, y1, x2, y2, color, layer))
                self.layers[layer].append((line, shape_type, x1, y1, x2, y2, color))

    def rotate_rectangle(self, x1, y1, x2, y2, angle):
        angle = radians(angle)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        corners = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
        new_corners = []
        for x, y in corners:
            dx, dy = x - cx, y - cy
            new_x = cx + dx * cos(angle) - dy * sin(angle)
            new_y = cy + dx * sin(angle) + dy * cos(angle)
            new_corners.append((new_x, new_y))
        return new_corners

    def rotate_line(self, x1, y1, x2, y2, angle):
        angle = radians(angle)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx1, dy1 = x1 - cx, y1 - cy
        dx2, dy2 = x2 - cx, y2 - cy
        new_x1 = cx + dx1 * cos(angle) - dy1 * sin(angle)
        new_y1 = cy + dx1 * sin(angle) + dy1 * cos(angle)
        new_x2 = cx + dx2 * cos(angle) - dy2 * sin(angle)
        new_y2 = cy + dx2 * sin(angle) + dy2 * cos(angle)
        return new_x1, new_y1, new_x2, new_y2

    def undo(self):
        if self.shapes:
            shape = self.shapes.pop()
            self.canvas.delete(shape[0])

    def redo(self):
        # Placeholder for redo functionality
        pass

    def save_file(self):
        # Placeholder for save file functionality
        pass

    def open_file(self):
        # Placeholder for open file functionality
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DraftApp(root)
    root.mainloop()
