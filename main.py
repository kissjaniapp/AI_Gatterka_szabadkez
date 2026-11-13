"""AI Gatterka Szabadkéz – első önálló prototípus."""
import csv
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class Gatterka(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Gatterka – Szabadkéz 0.1")
        self.geometry("1080x720")
        self.parts=[]
        self.tabs=ttk.Notebook(self)
        self.tabs.pack(fill="both",expand=True,padx=15,pady=15)
        self.frames=[ttk.Frame(self.tabs) for _ in range(4)]
        for f,name in zip(self.frames,("Bútorszerkesztő","3MF import","Alkatrészek","Szabásterv és mentés")):
            self.tabs.add(f,text=name)
        self.fields={}
        for index,(key,label,value) in enumerate([("name","Bútor neve","Szekrény"),("w","Szélesség",800),("h","Magasság",720),("d","Mélység",560),("t","Vastagság",18),("s","Polcok száma",2)]):
            ttk.Label(self.frames[0],text=label).grid(row=index,column=0,padx=16,pady=9,sticky="w")
            var=tk.StringVar(value=str(value));self.fields[key]=var
            ttk.Entry(self.frames[0],textvariable=var).grid(row=index,column=1,pady=9)
        ttk.Button(self.frames[0],text="Bútor létrehozása",command=self.cabinet).grid(row=7,column=0,columnspan=2,pady=15)
        ttk.Label(self.frames[1],text="3MF import – az objektumok befoglaló méreteinek kiolvasása").pack(pady=20)
        ttk.Button(self.frames[1],text="3MF kiválasztása",command=self.import3mf).pack()
        menu=ttk.Frame(self.frames[2]);menu.pack(fill="x")
        ttk.Button(menu,text="Alkatrész hozzáadása",command=self.add).pack(side="left")
        ttk.Button(menu,text="Kijelölt törlése",command=self.delete).pack(side="left")
        self.tree=ttk.Treeview(self.frames[2],columns=("name","l","w","t","qty"),show="headings")
        for col,title in zip(("name","l","w","t","qty"),("Név","Hossz","Szélesség","Vastagság","Darab")):
            self.tree.heading(col,text=title)
        self.tree.pack(fill="both",expand=True)
        ttk.Label(self.frames[3],text="Szabászati előkészítés – alkatrészlista export").pack(pady=20)
        ttk.Button(self.frames[3],text="Projekt mentése JSON",command=self.save).pack(pady=8)
        ttk.Button(self.frames[3],text="Projekt megnyitása",command=self.open).pack(pady=8)
        ttk.Button(self.frames[3],text="Alkatrészlista CSV export",command=self.export_csv).pack(pady=8)
        ttk.Label(self.frames[3],text="A CNC és szabásgép kimenete csak ellenőrzött gépi logika után aktiválható.",foreground="red").pack(pady=20)
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i,p in enumerate(self.parts):
            self.tree.insert("","end",iid=str(i),values=(p["name"],p["l"],p["w"],p["t"],p["qty"]))
    def cabinet(self):
        try:
            name=self.fields["name"].get()
            w,h,d,t=[float(self.fields[k].get()) for k in ("w","h","d","t")]
            shelves=int(self.fields["s"].get())
            if min(w,h,d,t)<=0 or min(w,h)<=2*t or not 0<=shelves<=100: raise ValueError()
            self.parts.extend([{"name":name+" oldallap","l":h,"w":d,"t":t,"qty":2},
             {"name":name+" tető","l":w-2*t,"w":d,"t":t,"qty":1},
             {"name":name+" fenék","l":w-2*t,"w":d,"t":t,"qty":1}])
            if shelves:self.parts.append({"name":name+" polc","l":w-2*t,"w":d,"t":t,"qty":shelves})
            self.refresh();self.tabs.select(self.frames[2])
        except (ValueError,OverflowError):messagebox.showerror("Hiba","Hibás méretek.")
    def add(self):
        window=tk.Toplevel(self);window.title("Alkatrész")
        values={}
        for i,(k,label,default) in enumerate([("name","Név","Alkatrész"),("l","Hossz",600),("w","Szélesség",400),("t","Vastagság",18),("qty","Darab",1)]):
            ttk.Label(window,text=label).grid(row=i,column=0,padx=8,pady=8)
            v=tk.StringVar(value=str(default));values[k]=v
            ttk.Entry(window,textvariable=v).grid(row=i,column=1,padx=8)
        def commit():
            try:
                p={"name":values["name"].get(),"l":float(values["l"].get()),"w":float(values["w"].get()),"t":float(values["t"].get()),"qty":int(values["qty"].get())}
                if not p["name"] or min(p["l"],p["w"],p["t"],p["qty"])<=0:raise ValueError()
                self.parts.append(p);self.refresh();window.destroy()
            except ValueError:messagebox.showerror("Hiba","Hibás alkatrész.")
        ttk.Button(window,text="Mentés",command=commit).grid(row=6,column=1,pady=10)
    def delete(self):
        selected=self.tree.selection()
        if selected:self.parts.pop(int(selected[0]));self.refresh()
    def import3mf(self):
        import zipfile,xml.etree.ElementTree as ET
        path=filedialog.askopenfilename(filetypes=[("3MF","*.3mf")])
        if not path:return
        try:
            with zipfile.ZipFile(path) as archive:
                count=0
                for member in archive.namelist():
                    if not member.endswith(".model"):continue
                    root=ET.fromstring(archive.read(member))
                    ns={"m":"http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
                    if root.get("unit","millimeter")!="millimeter":raise ValueError("Nem mm a mértékegység.")
                    for obj in root.findall(".//m:resources/m:object",ns):
                        pts=[[float(v.get(a)) for a in ("x","y","z")] for v in obj.findall("./m:mesh/m:vertices/m:vertex",ns)]
                        if not pts:continue
                        size=sorted((max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)),reverse=True)
                        if size[2]<=0:continue
                        self.parts.append({"name":Path(path).stem+" test "+str(obj.get("id")),"l":round(size[0],2),"w":round(size[1],2),"t":round(size[2],2),"qty":1});count+=1
            self.refresh();messagebox.showinfo("Import",str(count)+" test beolvasva. Ellenőrizd a méreteket!")
        except Exception as e:messagebox.showerror("3MF hiba",str(e))
    def save(self):
        path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("Gatterka projekt","*.json")])
        if path:Path(path).write_text(json.dumps({"version":1,"parts":self.parts},ensure_ascii=False,indent=2),encoding="utf-8")
    def open(self):
        path=filedialog.askopenfilename(filetypes=[("Gatterka projekt","*.json")])
        if path:
            try:
                data=json.loads(Path(path).read_text(encoding="utf-8"))
                if data["version"]!=1:raise ValueError("Más projektverzió")
                self.parts=data["parts"];self.refresh()
            except Exception as e:messagebox.showerror("Projekt hiba",str(e))
    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if path:
            with open(path,"w",encoding="utf-8-sig",newline="") as file:
                writer=csv.writer(file,delimiter=";")
                writer.writerow(("Név","Hossz","Szélesség","Vastagság","Darab"))
                for p in self.parts:writer.writerow((p[k] for k in ("name","l","w","t","qty")))
if __name__=="__main__":
    Gatterka().mainloop()
