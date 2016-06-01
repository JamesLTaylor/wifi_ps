import Tkinter as tk
import tkMessageBox
import ttk
import sys
from PIL import ImageTk, Image
import wifi_readings
import datetime
import json

class Application(ttk.Frame):
    
    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.set_constants()
        self.setup()
        root.grid_columnconfigure(0,weight=1)        
        root.grid_rowconfigure(0,weight=1)
        self.point_selected = False
        self.selected_node = None
        self.lines = {}
        self.nodes = {}
        self.dots = []
        self.set_new_image()
        self.last_press = datetime.datetime.now()
        self.node_top = 0
        self.line_top = 0
        self.circle_dragging = False
        
        
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
        btn_new_path = tk.Button(bottom_frame, text="Load JSON",command=self.dump_json)
        btn_new_path.grid(row = 0, column=3, padx=5, pady=10, sticky=tk.W)
        btn_new_path = tk.Button(bottom_frame, text="Dump JSON",command=self.dump_json)
        btn_new_path.grid(row = 0, column=4, padx=5, pady=10, sticky=tk.W)
        
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
        print("canvas clicked")
        print(event.widget)
        self.dragging = False        
        self.start_x = event.x
        self.start_y = event.y
        self.start_scroll_x = self.xscrollbar.get()[0]
        self.start_scroll_y = self.yscrollbar.get()[0]
        
    def canvas_drag(self, event):
        if self.circle_dragging:
            return            
        self.dragging = True        
        new_x = self.start_scroll_x + (self.start_x - event.x)/float(self.img_width)
        new_y = self.start_scroll_y + (self.start_y - event.y)/float(self.img_height)
        self.canvas.xview('moveto',new_x)
        self.canvas.yview('moveto',new_y)  
        
    def add_node(self, x, y):
        new_node_num = self.node_top
        self.node_top += 1
            
        self.point_selected = True
        
        new_node = {"x":x,"y":y, "to":[]}
        self.nodes[new_node_num] = new_node
        self.selected_node = new_node_num
        
        circle_item = self.canvas.create_oval(new_node["x"]-4, new_node["y"]-4, new_node["x"]+4, new_node["y"]+4, fill="red")
        
        self.canvas.tag_bind(circle_item, '<ButtonPress-1>', 
                             lambda event, i=new_node_num : self.circle_btn_down(event, i))
        self.canvas.tag_bind(circle_item, "<B1-Motion>", 
                             self.circle_drag)                                 
        self.canvas.tag_bind(circle_item, '<ButtonRelease-1>', 
                             lambda event, i=new_node_num : self.circle_btn_up(event, i))
        self.canvas.tag_bind(circle_item, '<Button-3>', 
                             lambda event, i=new_node_num : self.circle_right_click(event, i))
        new_node["circle_item"]=circle_item
        
        return new_node_num
        
        
    def canvas_drag_end(self, event):
        if (datetime.datetime.now()-self.last_press).total_seconds()<0.2:
            print("Too soon, don't process")
            return
        self.last_press = datetime.datetime.now()
        canvas = event.widget
        if self.dragging:
            self.dragging = False
            new_x = self.start_scroll_x + (self.start_x - event.x)/float(self.img_width)
            new_y = self.start_scroll_y + (self.start_y - event.y)/float(self.img_height)
            self.canvas.xview('moveto',new_x)
            self.canvas.yview('moveto',new_y)
        else:
            old_node_num = self.selected_node
            new_node_num = self.add_node(canvas.canvasx(event.x),canvas.canvasy(event.y))            
            
            if not old_node_num is None:
                self.nodes[old_node_num]["to"].append(new_node_num)
                self.nodes[new_node_num]["to"].append(old_node_num)
                last_circle = self.nodes[old_node_num]
                self.canvas.itemconfig(last_circle["circle_item"], fill='gray')
                self.add_line_between(old_node_num, new_node_num)
                
            
            """           
            
            self.latest_x = canvas.canvasx(event.x)
            self.latest_y = canvas.canvasy(event.y)
            self.latestpoint = self.canvas.create_oval(self.latest_x-4, self.latest_y-4, self.latest_x+4, self.latest_y+4, fill="red")                
            self.dots.append(self.latestpoint)
            #print("location set to: " + str((self.latest_x, self.latest_y)))            
            print("[" + str(self.latest_x) + "," + str(self.latest_y) + "],")            
            #else:
            #    tkMessageBox.showwarning("Duplicate point", 
            #    "A point is already selected for this floorplan.\nPlease record it before selecting another")
            """
            
    def add_line_between(self, node_from, node_to):
        
        line_num = self.line_top
        self.line_top += 1
        
        x1 = self.nodes[node_from]["x"]
        y1 = self.nodes[node_from]["y"]
        x2 = self.nodes[node_to]["x"]
        y2 = self.nodes[node_to]["y"]
        
        new_x1 = x1 + 0.1*(x2-x1)
        new_y1 = y1 + 0.1*(y2-y1)
        new_x2 = x1 + 0.9*(x2-x1)
        new_y2 = y1 + 0.9*(y2-y1)
        
        line_item = self.canvas.create_line(new_x1, new_y1, new_x2, new_y2, width=3)
        self.canvas.tag_bind(line_item, '<Button-1>', 
                             lambda event, i=line_num : self.line_btn(event, i))
        
        new_line = {"node1":node_from, "node2":node_to, "line_item":line_item}
        self.lines[line_num] = new_line
        
            
    def circle_btn_down(self, event, i):
        print("circle btn down:" + str(i))  
        self.circle_dragging_ind = i
        
        return "break"
        
    def circle_drag(self, event):
        self.circle_dragging = True
        self.dragging = False
        
        this_circle = self.nodes[self.circle_dragging_ind]["circle_item"]
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.coords(this_circle, x-3, y-3, x+3, y+3)
        self.nodes[self.circle_dragging_ind]["x"] = x
        self.nodes[self.circle_dragging_ind]["y"] = y
        
        for (num, line) in self.lines.iteritems():
            if self.circle_dragging_ind == line["node1"]:
                x2 = self.nodes[line["node2"]]["x"]
                y2 = self.nodes[line["node2"]]["y"]
                new_x1 = x + 0.1*(x2-x)
                new_y1 = y + 0.1*(y2-y)
                new_x2 = x + 0.9*(x2-x)
                new_y2 = y + 0.9*(y2-y)                
                self.canvas.coords(line["line_item"], new_x1, new_y1, new_x2, new_y2)
                
            elif self.circle_dragging_ind == line["node2"]:
                x2 = self.nodes[line["node1"]]["x"]
                y2 = self.nodes[line["node1"]]["y"]
                new_x1 = x + 0.1*(x2-x)
                new_y1 = y + 0.1*(y2-y)
                new_x2 = x + 0.9*(x2-x)
                new_y2 = y + 0.9*(y2-y)                
                self.canvas.coords(line["line_item"], new_x1, new_y1, new_x2, new_y2)
        
        
    def circle_btn_up(self, event, i):
        self.last_press = datetime.datetime.now()
        if self.circle_dragging:            
            self.circle_dragging = False
            return
            
        print("circle btn up:" + str(i))
        print(self.selected_node)
        
        if self.selected_node==None:
            self.selected_node = i
            last_circle = self.nodes[self.selected_node]["circle_item"]
            self.canvas.itemconfig(last_circle, fill='red')
        else:
            if i==self.selected_node:            
                last_circle = self.nodes[self.selected_node]["circle_item"]
                self.canvas.itemconfig(last_circle, fill='gray')
                self.selected_node = None
            else:
                # add a line connection
                self.add_line_between(self.selected_node, i)
                last_circle = self.nodes[self.selected_node]
                self.canvas.itemconfig(last_circle["circle_item"], fill='gray')
                self.selected_node = i
                last_circle = self.nodes[self.selected_node]["circle_item"]
                self.canvas.itemconfig(last_circle, fill='red')
            
        return "break"     
        
        
    
    def circle_right_click(self, event, i):
        last_circle = self.nodes[i]["circle_item"]
        if i==self.selected_node:
           self.selected_node=None 
        
        self.canvas.delete(last_circle)
        self.nodes.pop(i)
        
        for (num, node) in self.nodes.iteritems():
            if i in node["to"]:
                node["to"].remove(i)

        outer_nodes = []
        delete_lines = []
        
        for (num, line) in self.lines.iteritems():
            if i == line["node1"]:
                outer_nodes.append(line["node2"])
                self.canvas.delete(line["line_item"])
                delete_lines.append(num)
            elif i == line["node2"]:
                outer_nodes.append(line["node1"])
                self.canvas.delete(line["line_item"])
                delete_lines.append(num)
                
        for num in delete_lines:
            self.lines.pop(num)
        if len(outer_nodes)==2:
            self.add_line_between(*outer_nodes)
                
               
                
    """ Add a node, delete the old line, add lines to the new node
    """
    def line_btn(self, event, i):        
        print("line clicked:" + str(i))
        print(event.widget)
        self.last_press = datetime.datetime.now()

        last_circle = self.nodes[self.selected_node]["circle_item"]
        self.canvas.itemconfig(last_circle, fill='gray')
        self.selected_node = None        
        
        new_node_num = self.add_node(self.canvas.canvasx(event.x),self.canvas.canvasy(event.y))
        line = self.lines[i]
        self.add_line_between(line["node1"], new_node_num)
        self.add_line_between(line["node2"], new_node_num)
        self.canvas.delete(line["line_item"])
        self.lines.pop(i)
        
        last_circle = self.nodes[self.selected_node]["circle_item"]
        self.canvas.itemconfig(last_circle, fill='gray')
        self.selected_node = None  
        
                
        return "break"

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
        self.set_new_image()
        
    def load_json(self):
        pass        
        
    def dump_json(self):
        print("##########################################")
        print(json.dumps(self.nodes))
        print("##########################################")
        

if __name__ == "__main__":

                 
    #root = tk.Toplevel()
    root = tk.Tk()
    root.title("Wifi positioning system")
    
    app = Application(root)
    root.geometry("1000x700")
    root.update()
    
    root.mainloop() 