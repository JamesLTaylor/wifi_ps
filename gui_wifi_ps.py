import Tkinter as tk
import ttk
import sys
from PIL import ImageTk, Image

class Application(ttk.Frame):
    
    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup()
        root.grid_columnconfigure(0,weight=1)        
        root.grid_rowconfigure(0,weight=1)
        
    def setup(self):
        # Top frame
        top_frame = tk.Frame(self) 
        variable = tk.StringVar(top_frame)
        variable.set("one") # default value
        
        w = tk.OptionMenu(top_frame, variable, "one", "two", "three")
        w.grid(row = 0, column=0, padx=5, pady=10, sticky=tk.W)
        
        # Canvas frame
        canvas_frame = tk.Frame(self)
        self.xscrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.xscrollbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        
        self.yscrollbar = tk.Scrollbar(canvas_frame)
        self.yscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        self.canvas = tk.Canvas(canvas_frame, bd=0, xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)                
        
        self.canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        filename = "C:\\Dev\\wifi_ps\\floor_plans\\greenstone_lower.gif"        
        self.img = ImageTk.PhotoImage(file=filename)        
        self.img_width = self.img.width()
        self.img_height = self.img.height()
        self.canvas.create_image(0,0,image=self.img, anchor="nw", tags='img')
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.bind("<Button-1>", self.canvas_btn_down)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_drag_end)
         
        self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar.config(command=self.canvas.yview)
        
        canvas_frame.grid_columnconfigure(0,weight=1)        
        canvas_frame.grid_rowconfigure(0,weight=1)
        
        # Bottom frame
        bottom_frame = tk.Frame(self)
        
        btn_rec= tk.Button(bottom_frame, text="Record")
        btn_rec.grid(row = 0, column=0, padx=5, pady=10, sticky=tk.W)
        btn_id = tk.Button(bottom_frame, text="Identifiy")
        btn_id.grid(row = 0, column=1, padx=5, pady=10, sticky=tk.W)
        
        top_frame.grid(row=0, column=0, sticky=tk.W)
        canvas_frame.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        bottom_frame.grid(row=2, column=0, sticky=tk.W)
        
        self.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.grid_columnconfigure(0,weight=1)        
        self.grid_rowconfigure(1,weight=1)
        
        
    def on_closing(self):
        root.destroy()
        #sys.exit()
        
    def canvas_btn_down(self, event):
        self.dragging = False        
        self.start_x = event.x
        self.start_y = event.y
        self.start_scroll_x = self.xscrollbar.get()[0]
        self.start_scroll_y = self.yscrollbar.get()[0]
        
    def canvas_drag(self, event):
        self.dragging = True        
        new_x = self.start_scroll_x + (self.start_x - event.x)/float(self.img_width)
        new_y = self.start_scroll_y + (self.start_y - event.y)/float(self.img_height)
        self.canvas.xview('moveto',new_x)
        self.canvas.yview('moveto',new_y)
        
    def canvas_drag_end(self, event):
        canvas = event.widget
        if self.dragging:
            self.dragging = False
            new_x = self.start_scroll_x + (self.start_x - event.x)/float(self.img_width)
            new_y = self.start_scroll_y + (self.start_y - event.y)/float(self.img_height)
            self.canvas.xview('moveto',new_x)
            self.canvas.yview('moveto',new_y)
        else:
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="red")
            print("location set to: " + str((x, y)))            
        

if __name__ == "__main__":
    #root = tk.Toplevel()
    root = tk.Tk()
    root.title("Wifi positioning system")
    
    app = Application(root)
    root.update()
    
    root.mainloop() 