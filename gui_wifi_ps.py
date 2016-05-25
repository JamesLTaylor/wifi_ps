import Tkinter as tk
import tkMessageBox
import ttk
import sys
from PIL import ImageTk, Image
import wifi_readings

class Application(ttk.Frame):
    
    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.set_constants()
        self.setup()
        root.grid_columnconfigure(0,weight=1)        
        root.grid_rowconfigure(0,weight=1)
        self.point_selected = False
        self.lines = []
        self.dots = []
        self.set_new_image()
        
        
    def set_constants(self):
        self.images = {"Home":
                          {"Downstairs": "C:\\Dev\\wifi_ps\\floor_plans\\house_lower.gif",
                           "Upstairs": "C:\\Dev\\wifi_ps\\floor_plans\\house_upper.gif"},
                       "Greenstone":
                           {"Upper Level":"C:\\Dev\\wifi_ps\\floor_plans\\greenstone_upper.gif", 
                            "Lower Level":"C:\\Dev\\wifi_ps\\floor_plans\\greenstone_lower.gif"}
                      }        
        
    def setup(self):
        # Top frame
        top_frame = tk.Frame(self) 
        self.location_var = tk.StringVar(top_frame)
        values = self.images.keys() 
        self.location_var.set(values[1])
        self.location_option = tk.OptionMenu(top_frame, self.location_var, *values)
        self.location_option.grid(row = 0, column=0, padx=5, pady=10, sticky=tk.W)
        self.location_var.trace("w", self.location_change)
        
        self.level_var = tk.StringVar(top_frame)
        values = self.images[self.location_var.get()].keys()
        self.level_var.set(values[0])
        self.level_option = tk.OptionMenu(top_frame, self.level_var, *values)
        self.level_option.grid(row = 0, column=2, padx=5, pady=10, sticky=tk.W)
        self.level_var.trace("w", self.level_change)
        
        # Canvas frame
        canvas_frame = tk.Frame(self)
        self.xscrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.xscrollbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        
        self.yscrollbar = tk.Scrollbar(canvas_frame)
        self.yscrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        self.canvas = tk.Canvas(canvas_frame, bd=0, xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)                
        
        self.canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        
        #filename = "C:\\Dev\\wifi_ps\\floor_plans\\greenstone_lower.gif"        
        #self.img = ImageTk.PhotoImage(file=filename)        
        #self.img_width = self.img.width()
        #self.img_height = self.img.height()
        #self.image_on_canvas = self.canvas.create_image(0,0,image=self.img, anchor="nw", tags='img')
        self.image_on_canvas = self.canvas.create_image(0,0,image=None, anchor="nw", tags='img')
        #self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.bind("<Button-1>", self.canvas_btn_down)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_drag_end)
         
        self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar.config(command=self.canvas.yview)
        
        canvas_frame.grid_columnconfigure(0,weight=1)        
        canvas_frame.grid_rowconfigure(0,weight=1)
        
        # Bottom frame
        bottom_frame = tk.Frame(self)
        
        btn_rec= tk.Button(bottom_frame, text="Record", command=self.record)
        btn_rec.grid(row = 0, column=0, padx=5, pady=10, sticky=tk.W)
        btn_id = tk.Button(bottom_frame, text="Identifiy")
        btn_id.grid(row = 0, column=1, padx=5, pady=10, sticky=tk.W)
        btn_new_path = tk.Button(bottom_frame, text="New path",command=self.new_path)
        btn_new_path.grid(row = 0, column=2, padx=5, pady=10, sticky=tk.W)
        
        top_frame.grid(row=0, column=0, sticky=tk.W)
        canvas_frame.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        bottom_frame.grid(row=2, column=0, sticky=tk.W)
        
        self.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.grid_columnconfigure(0,weight=1)        
        self.grid_rowconfigure(1,weight=1)
        
    
    def location_change(self, *args):        
#        if self.location_var.get()=="Greenstone":
#            self.img_filename = "C:\\Dev\\wifi_ps\\floor_plans\\greenstone_lower.gif"
#        elif self.location_var.get()=="Home":
#            self.img_filename = "C:\\Dev\\wifi_ps\\floor_plans\\house_lower.gif"
#        else:
#            raise Exception("not a recognized location")
            
        values = self.images[self.location_var.get()].keys()        
        self.level_var.set(values[0])
        self.level_option['menu'].delete(0, 'end')
        for choice in values:
            self.level_option['menu'].add_command(label=choice, command=tk._setit(self.level_var, choice))
        
        self.set_new_image()
        
    def level_change(self, *args):
        self.set_new_image()

        
            
        
    def set_new_image(self):
        self.img_filename = self.images[self.location_var.get()][self.level_var.get()]
        self.img = ImageTk.PhotoImage(file=self.img_filename)        
        self.img_width = self.img.width()
        self.img_height = self.img.height()
        self.canvas.itemconfig(self.image_on_canvas, image = self.img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        
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
            if self.point_selected:
                self.lines.append(self.canvas.create_line(self.latest_x, self.latest_y, canvas.canvasx(event.x), canvas.canvasy(event.y), tag = "path"))
                
            self.point_selected = True
            self.latest_x = canvas.canvasx(event.x)
            self.latest_y = canvas.canvasy(event.y)
            self.latestpoint = self.canvas.create_oval(self.latest_x-4, self.latest_y-4, self.latest_x+4, self.latest_y+4, fill="red")                
            self.dots.append(self.latestpoint)
            #print("location set to: " + str((self.latest_x, self.latest_y)))            
            print("[" + str(self.latest_x) + "," + str(self.latest_y) + "],")            
            #else:
            #    tkMessageBox.showwarning("Duplicate point", 
            #    "A point is already selected for this floorplan.\nPlease record it before selecting another")

    def record(self, *args):  
        if self.point_selected:
            self.canvas.itemconfig(self.latestpoint, fill='orange')
            wifi_readings.make_readings('greenstone1.csv', self.location_var.get(), self.level_var.get(), self.latest_x, self.latest_y, 20)
            self.canvas.itemconfig(self.latestpoint, fill='green')
            self.point_selected = False
        else:
            tkMessageBox.showwarning("No point selected", 
            "No point is selected for this floorplan.\nPlease select one and then record.")
            
    def new_path(self, *args):
        self.point_selected = False
        for line in self.lines:
            self.canvas.delete(line)
        for dot in self.dots:
            self.canvas.delete(dot)
        self.lines =[]
        self.dots = []
        print("")
        print("")
        self.set_new_image()
        

if __name__ == "__main__":

                 
    #root = tk.Toplevel()
    root = tk.Tk()
    root.title("Wifi positioning system")
    
    app = Application(root)
    root.geometry("1000x700")
    root.update()
    
    root.mainloop() 