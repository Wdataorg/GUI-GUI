"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@                           @
@ 作者：Rainwangpupil + 黑客零@
@ 日期：2023/1               @
@ 项目：GUI-GUI              @
@ 版本：v0.0.1               @
@                           @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

接口说明：

此为GUI-GUI项目的主文件，包含了项目绝大部分代码（GUI实现，项目创建打开保存，组件拖动，
以及所有组件的信息。

导入方式
import gui_main

使用方法：
导入即运行

依赖包：
ttkbootstrap (pip)
tkinter      (默认)
ctypes       (默认)
easygui      (pip)
"""


import ttkbootstrap as ttk
import tkinter as tk
import ctypes
from tkinter import *
from ctypes import *
import easygui as g
from tkinter import messagebox
from tkinter import filedialog
import gen_py
import os

__version__ = "0.0.1"
u32 = ctypes.windll.user32
FILESTATUS = r'未命名'

class _PointAPI(Structure):  
    "私有类型"
    _fields_ = [("x", c_ulong), ("y", c_ulong)]


def getpos():
    """获取坐标系"""
    po = _PointAPI()
    windll.user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)

def xpos(): return getpos()[0]
def ypos(): return getpos()[1]

bound = {}


def __add(wid, data):  # 添加绑定数据
    """私有类型"""
    bound[wid] = bound.get(wid, []) + [data]


def __remove(wid, key):  # 用于从bound中移除绑定
    """私有类型"""
    for i in range(len(bound[wid])):
        try:
            if bound[wid][i][0] == key:
                del bound[wid][i]
        except IndexError:
            pass


def __get(wid, key=''):  # 用于从bound中获取绑定数据
    """私有类型"""

    if not key: return bound[wid][0]
    if key == 'resize':
        for i in range(len(bound[wid])):
            for s in 'nwse':
                if s in bound[wid][i][0].lower():
                    return bound[wid][i]
    for i in range(len(bound[wid])):
        if bound[wid][i][0] == key:
            return bound[wid][i]


def move(widget, x=None, y=None, width=None, height=None):
    "移动控件或窗口widget, 参数皆可选。"
    x = x if x != None else widget.winfo_x()
    y = y if y != None else widget.winfo_y()
    width = width if width != None else widget.winfo_width()
    height = height if height != None else widget.winfo_height()
    if isinstance(widget, tk.Wm):
        widget.geometry("%dx%d+%d+%d" % (width, height, x, y))
    else:
        widget.place(x=x, y=y, width=width, height=height)
    return x, y, width, height


def _mousedown(event):
    """私有类型"""

    if event.widget not in bound: return
    lst = bound[event.widget]
    for data in lst:  # 开始拖动时, 在每一个控件记录位置和控件尺寸
        widget = data[1]
        widget.mousex, widget.mousey = getpos()
        widget.startx, widget.starty = widget.winfo_x(), widget.winfo_y()
        widget.start_w = widget.winfo_width()
        widget.start_h = widget.winfo_height()


def _drag(event):
    """私有类型"""

    if event.widget not in bound: return
    lst = bound[event.widget]
    for data in lst:  # 多个绑定
        if data[0] != 'drag': return
        widget = data[1]
        dx = xpos() - widget.mousex  
        dy = ypos() - widget.mousey
        move(widget, widget.startx + dx if data[2] else None,
             widget.starty + dy if data[3] else None)


def _resize(event):
    """私有类型"""

    data = __get(event.widget, 'resize')
    if data is None: return
    widget = data[1]
    dx = xpos() - widget.mousex  # 计算位置差
    dy = ypos() - widget.mousey

    type = data[0].lower()
    minw, minh = data[2:4]
    if 's' in type:
        move(widget, height=max(widget.start_h + dy, minh))
    elif 'n' in type:
        move(widget, y=min(widget.starty + dy, widget.starty + widget.start_h - minh),
             height=max(widget.start_h - dy, minh))

    __remove(event.widget, data[0])  # 取消绑定, 为防止widget.update()中产生新的事件, 避免_resize()被tkinter反复调用
    widget.update()  # 刷新控件, 使以下左右缩放时, winfo_height()返回的是新的控件坐标, 而不是旧的
    __add(event.widget, data)  # 重新绑定

    if 'e' in type:
        move(widget, width=max(widget.start_w + dx, minw))
    elif 'w' in type:
        move(widget, x=min(widget.startx + dx, widget.startx + widget.start_w - minw),
             width=max(widget.start_w - dx, minw))


def draggable(tkwidget, x=True, y=True):
    
    bind_drag(tkwidget, tkwidget, x, y)


def bind_drag(tkwidget, dragger, x=True, y=True):
    dragger.bind("<Button-1>", _mousedown, add='+')
    dragger.bind("<B1-Motion>", _drag, add='+')
    __add(dragger, ('drag', tkwidget, x, y))  # 在bound字典中记录数据


def bind_resize(tkwidget, dragger, anchor, min_w=0, min_h=0, move_dragger=True):
    dragger.bind("<Button-1>", _mousedown, add='+')
    dragger.bind("<B1-Motion>", _resize, add='+')
    data = (anchor, tkwidget, min_w, min_h, move_dragger)
    __add(dragger, data)


btns = []  # 用btns列表存储创建的按钮


def add_button(func, anchor):
    """添加拖动手柄"""

    # func的作用是计算按钮新坐标
    b = ttk.Button(win)
    b._func = func
    bind_resize(btn, b, anchor)
    x, y = func()
    b.place(x=x, y=y, width=size, height=size)
    b.bind('<B1-Motion>', adjust_button, add='+')
    btns.append(b)


def adjust_button(event=None):
    # 改变大小或拖动后,调整手柄位置
    for b in btns:
        x, y = b._func()
        b.place(x=x, y=y)

def go():
    b_back=u32.GetParent(win.winfo_id())
    a_back=u32.GetParent(win.winfo_id())
    u32.SetParent(b_back,root.winfo_id())

def handle(control):
    """
    用于消除拖动组件中的大量重复部分
    control: ttk(tk)组件对象
    返回值:   无
    """
    add_button(lambda: (control.winfo_x() - size, control.winfo_y() - size),
               'nw')
    add_button(lambda: (control.winfo_x() + control.winfo_width() // 2,
                        control.winfo_y() - size), 'n')
    add_button(lambda: (control.winfo_x() + control.winfo_width(), control.winfo_y() - size),
               'ne')
    add_button(lambda: (control.winfo_x() + control.winfo_width(),
                        control.winfo_y() + control.winfo_height() // 2), 'e')
    add_button(lambda: (control.winfo_x() + control.winfo_width(),
                        control.winfo_y() + control.winfo_height()), 'se')
    add_button(lambda: (control.winfo_x() + control.winfo_width() // 2,
                        control.winfo_y() + control.winfo_height()), 's')
    add_button(lambda: (control.winfo_x() - size, control.winfo_y() + control.winfo_height()),
               'sw')
    add_button(lambda: (control.winfo_x() - size,
                        control.winfo_y() + control.winfo_height() // 2), 'w')

    def dels():
        control.pack_forget()

    menu = tk.Menu(win, tearoff=0)
    menu.add_command(label="删除组件", command=dels)
    menubar = Menu(win)

    def popupmenu(event):
        menu.post(event.x_win, event.y_win)

    control.bind("<Button-3>", popupmenu)
    

def butn():
    lba = g.enterbox("显示的文字")
    if not lba:
        messagebox.showerror(title="提示", message='文字不可以为空！')
        return

    global btn
    global size
    btn = ttk.Button(win, text=lba)
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    handle(btn)

def labn():
    lba = g.enterbox("显示的文字")
    lbs = g.enterbox("文字的大小")
    if not lba:
        messagebox.showerror(title="提示", message='文字不可以为空！')
        return

    global btn
    global size
    if not lbs:
        btn = ttk.Label(win, text=lba)

    else:
        try:
            btn = ttk.Label(win, text=lba, font=('Arial', int(lbs)))
        except:
            messagebox.showerror(title='提示', message='输入信息不规范')
            return
    
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    handle(btn)

def entryn():
    global btn
    global size
    btn = ttk.Entry(win)
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    handle(btn)

def chocien():
    name = g.enterbox('选择框的名称')
    if not name:
        messagebox.showerror(title="提示", message='请输入完整！')
        return 
    
    global btn
    global size
    btn = ttk.Radiobutton(win, text=name)
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    handle(btn)

def alertn():
    name = g.enterbox('区域框的名称：')
    if not name:
        messagebox.showerror(title="提示", message='请输入完整！')
        return 
    
    global btn
    global size
    btn = ttk.LabelFrame(win, text=name)
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    handle(btn)

def nprn():
    global btn
    global size
    count = g.enterbox('请输入组合框条目数量：')
    try:
        count = eval(count)
    
    except:
        messagebox.showerror(title="提示", message="请输入数字！")
        return
    
    if not count:
        messagebox.showerror(title="提示", message="不可以为0！")
        return
    
    projects = []

    for i in range(count):
        tmp = g.enterbox('请输入条目{}'.format(i+1))
        if not tmp:
            messagebox.showerror(title="提示", message="条目不可以为空！")
            return
        
        projects.append(tmp)
    
    btn = ttk.Combobox(win, value=projects)
    draggable(btn)
    btn.bind('<B1-Motion>', adjust_button, add='+')
    x1 = 20;
    y1 = 20;
    x2 = 220;
    y2 = 170;
    size = 10
    btn.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
    win.update()
    """
    这里不要添加handle函数！
    handle函数应用在组合框类型上会出现bug!
    """
    add_button(lambda: (btn.winfo_x() - size, btn.winfo_y() - size),
               'nw')
    add_button(lambda: (btn.winfo_x() + btn.winfo_width() // 2,
                        btn.winfo_y() - size), 'n')
    add_button(lambda: (btn.winfo_x() + btn.winfo_width(), btn.winfo_y() - size),
               'ne')
    add_button(lambda: (btn.winfo_x() + btn.winfo_width(),
                        btn.winfo_y() + btn.winfo_height() // 2), 'e')
    add_button(lambda: (btn.winfo_x() + btn.winfo_width(),
                        btn.winfo_y() + btn.winfo_height()), 'se')
    add_button(lambda: (btn.winfo_x() + btn.winfo_width() // 2,
                        btn.winfo_y() + btn.winfo_height()), 's')
    add_button(lambda: (btn.winfo_x() - size, btn.winfo_y() + btn.winfo_height()),
               'sw')
    add_button(lambda: (btn.winfo_x() - size,
                        btn.winfo_y() + btn.winfo_height() // 2), 'w')

    def dels():
        btn.pack_forget()

    menu = tk.Menu(win, tearoff=0)
    menu.add_command(label="删除组件", command=dels)
    menubar = Menu(win)

    def popupmenu(event):
        menu.post(event.x_win, event.y_win)

    btn.bind("<Button-3>", popupmenu)
    # handle(btn)


# 初始化

root = ttk.Window(
    title="GUI-GUI",
    themename="darkly",
    alpha=0.9,
    position=(0, 0)
)

root.geometry("{}x{}".format(root.winfo_screenwidth(), root.winfo_screenheight()))
win = ttk.Toplevel(position=(200, 2))
win.title(FILESTATUS.split('.ggp')[0])
win.iconbitmap('./logo.ico')

root.after(100, go)
root.iconbitmap('./logo.ico')

# 后台

def projectcreate():
    """创建项目"""
    icopath = None     # 获取ico
    folderpath = None  # 获取路径
    THEME = ttk.StringVar()  # 获取主题
    xget = None        # 获取x坐标
    yget = None        # 获取y坐标
    alpha = tk.DoubleVar()  # 获取透明度


    askwindow = ttk.Toplevel()
    askwindow.title('创建项目')
    askwindow.iconbitmap('./logo.ico')
    projectname = ttk.Label(askwindow, text='项目名称：')
    projectask = ttk.Entry(askwindow)
    projectname.grid(padx=5, pady=5, row=1, column=1)
    projectask.grid(padx=5, pady=5, row=1, column=2)

    iconnname = ttk.Label(askwindow, text='项目图标地址（ico文件）：')
    def askico():
        icopath = filedialog.askopenfilename(title="请选择ico文件")
        if '.ico' not in icopath:
            messagebox.showerror(title="提示", message="请选择ico文件！")
            return
        iconask['text'] = icopath
        return icopath
    
    iconask = ttk.Button(askwindow, text='选择ico文件', command=askico)
    iconnname.grid(padx=5, pady=5, row=2, column=1)
    iconask.grid(padx=5, pady=5, row=2, column=2)
    posname = ttk.Label(askwindow, text='窗口起始位置')
    posx = ttk.Label(askwindow, text='x坐标：')
    posxaask = ttk.Entry(askwindow)
    posy = ttk.Label(askwindow, text='y坐标：')
    posyask = ttk.Entry(askwindow)
    posname.grid(pady=5, row=3, column=1)
    posx.grid(padx=3, pady=5, column=1, row=4)
    posxaask.grid(padx=3, pady=5, column=2, row=4)
    posy.grid(padx=3, pady=5, column=3, row=4)
    posyask.grid(padx=3, pady=5, column=4, row=4)

    alphaname = ttk.Label(askwindow, text="窗口透明度：")
    alphaask = tk.Scale(askwindow, from_=0.0, to=1.0, orient=ttk.HORIZONTAL, variable=alpha, length=300, 
            resolution=0.1, tickinterval=0.2)
    alphaname.grid(padx=5, pady=5, row=5, column=1)
    alphaask.grid(padx=5, pady=5, row=5, column=2)
    alertof = ttk.Label(askwindow, text="1.0表示不透明，0.0表示全透明")
    alertof.grid(padx=5, pady=5, row=6, column=1)

    themename = ttk.Label(askwindow, text="选择窗口风格：")
    alltheme = [
        'litera',
        'minty',
        'lumen',
        'sandstone',
        'yeti',
        'pulse',
        'united',
        'morph',
        'journal',
        'darkly',
        'superhero',
        'solar',
        'cyborg',
        'vapor',
        'simplex',
        'cerculean'
    ]
    themeask = ttk.Combobox(askwindow, value=alltheme, textvariable=THEME)
    themename.grid(padx=5, pady=5, row=7, column=1)
    themeask.grid(padx=5, pady=5, row=7, column=2)
    def fchoice():
        global folderpath
        folderpath = filedialog.askdirectory(title="请选择项目目录")
        fask['text'] = folderpath
    
    fask = ttk.Button(askwindow, text="选择项目目录：", command=fchoice)

    fask.grid(padx=5, pady=5, row=8, column=1)

    def ent(
        THEME,
        projectname,
        posxaask,
        posyask,
        alpha,
        folderpath,
        icopath
    ):
        global FILESTATUS
        THEME = THEME.get()
        projectname = projectname.get()
        try:
            xget = int(posxaask.get())
            yget = int(posyask.get())

        except:
            messagebox.showerror(title='提示', message='输入信息不规范')
            return
        
        alpha = alpha.get()

        if not (folderpath or THEME or xget or yget or alpha or projectname or folderpath == '选择项目目录：'):
            messagebox.showeerror(title='提示', message='输入信息不规范')
            return
        
        with open(folderpath + '/{}.ggp'.format(projectname), 'w', encoding='utf-8') as f:
            f.write('kase->0\n')
            f.write('Project Name->{}\n'.format(projectname))
            if icopath != '请选择ico文件':
                f.write('Icon Path->{}\n'.format(icopath))
            
            else:
                f.write('Icon Path->false\n')           
            f.write('Position->{}->{}\n'.format(xget, yget))
            f.write('Alpha->{}\n'.format(alpha))
            f.write('Theme->{}\n'.format(THEME))
            f.write('Menu->false')
        
        messagebox.showinfo(title="提示", message="成功创建项目！")
        FILESTATUS = folderpath + '/{}.ggp'.format(projectname)
        _openit()
        

    enter = ttk.Button(askwindow, text="提交", command=lambda : ent(
        THEME,
        projectask,
        posxaask,
        posyask, 
        alpha,
        fask['text'],
        iconask['text']
        ))
    enter.grid(padx=5, pady=5, row=9, column=1)
    
    askwindow.mainloop()
    


def filesave():
    """保存项目"""
    if FILESTATUS == '未命名':
        messagebox.showerror(title="提示", message='请先打开一个项目！')
        return
    """
    函数作用：获取bound字典中用户添加的组件，并记录到.ggp文件

    .ggp format:
    Line One ~ Line Eight: Basic Information
    Line One: kase->{}
    Line Two: Project Name->{}
    *Line Three: Icon Path->{}
    Line Four: Window title->{}
    *Line Five: Position->{}
    *Line Six: Alpha->{}
    *Line Seven: Theme->{}
    Line Eight: Menu->(false)->Menu1->Menu2->Menu3->Menu4->……

    Button Format:
    Button{KASE}->width->height->text->x->y

    Label Format:
    Label{KASE}->width->height->text->x->y->fontsize

    Entry Format:
    Entry{KASE}->width->height->x->y

    Choices Format:
    Choices{KASE}->text->x->y

    NPR Format:
    NPR{KASE}->width->height->x->y->Choice one->Choice two->Choice three->……

    LabelFrame Format:
    LabelFrame{KASE}->width->height->x->y->text


   """
   # 读取内容。
    with open(FILESTATUS, 'r', encoding='utf-8') as file:
        fi = list(file.readlines())
        kase = list(fi)[0].split('\n')[0].split('kase->')[1]
        kase = int(kase)
        print(fi)
    
    
    for i in bound:
        # print(isinstance(i, ttk.Combobox))
        # print(i['value'])
        if isinstance(i, ttk.Button) and i['text']:
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase = kase + 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                readcontent.append('\nButton{}->{}->{}->{}->{}->{}\n'.format(kase, i.winfo_width(), 
                i.winfo_height(), i['text'], i.winfo_x(), i.winfo_y()))
                print(i.winfo_width())
                print(readcontent)
                # with open(FILESTATUS, 'w', encoding='utf-8') as ff:
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()
        
        elif isinstance(i, ttk.Label) and i['text']:
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase = kase + 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                if i['font']:
                    size = ''
                    for j in str(i['font']):
                        if ord(j) >= 48 and ord(j) <= 57:
                            size += j

                    size = int(size) 
                    readcontent.append('\nLabel{}->{}->{}->{}->{}->{}->{}\n'.format(kase, i.winfo_width(), 
                    i.winfo_height(), i['text'], i.winfo_x(), i.winfo_y(), size))
                
                else:
                    readcontent.append('\nLabel{}->{}->{}->{}->{}->{}->{}\n'.format(kase, i.winfo_width(), 
                    i.winfo_height(), i['text'], i.winfo_x(), i.winfo_y(), 10))
                print(readcontent)
                # with open(FILESTATUS, 'w', encoding='utf-8') as ff:
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()
        
        elif isinstance(i, ttk.Radiobutton) and i['text']:
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase = kase + 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                readcontent.append('\nChoices{}->{}->{}->{}\n'.format(kase, i['text'], i.winfo_x(), 
                        i.winfo_y()))
                print(readcontent)
                # with open(FILESTATUS, 'w', encoding='utf-8') as ff:
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()

        elif type(i) is ttk.Entry:
            
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase = kase + 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                readcontent.append('\nEntry{}->{}->{}->{}->{}\n'.format(kase, 
                i.winfo_width(), i.winfo_height(), i.winfo_x(), i.winfo_y()))
                print(readcontent)
                # with open(FILESTATUS, 'w', encoding='utf-8') as ff:
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()
        
        elif isinstance(i, ttk.LabelFrame):
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase = kase + 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                readcontent.append('\nLabelFrame{}->{}->{}->{}->{}->{}\n'.format(kase, 
                i.winfo_width(), i.winfo_height(), i.winfo_x(), i.winfo_y(), i['text']))
                print(readcontent)
                # with open(FILESTATUS, 'w', encoding='utf-8') as ff:
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()
        
        elif type(i) is ttk.Combobox and i['value']:
            """
            不要修改此处判断代码
            因为作者经过测试，发现：
            >>> t = ttk.Combobox()
            >>> isinstance(t, ttk.Entry)
            True
            >>> type(i) is ttk.Entry
            False
            """
            with open(FILESTATUS, 'w', encoding='utf-8') as f:
                readcontent = list(fi)
                kase += 1
                readcontent[0] = 'kase->' + str(kase) + '\n'
                readcontent.append('\nNPR{}->{}->{}->{}->{}->'.format(kase, i.winfo_width(), i.winfo_height(),
                         i.winfo_x(), i.winfo_y()))
                readcontent[-1] = readcontent[-1] + '->'.join(i['value'])
                f.writelines(readcontent)
                fi = list(readcontent)
                f.flush()

def _openit():
    print(FILESTATUS)
    win.title(FILESTATUS.split('.ggp')[0])
    with open(FILESTATUS, 'r', encoding='utf-8') as r:
        rc = r.readlines()
        for i in rc:
            if i == '\n':
                rc.remove(i)
        
        for i in range(7, len(rc)):
            # 6是控件记录开始的地方
            if rc[i][-1:] == '\n':
                rc[i] = rc[i][:-1]
    
    tmp = None
    controltmp = None

    for i in rc:
        tmp = i.split('->')
        print(tmp)
        if len(tmp) > 1:
            if len(tmp) == 7 and tmp[0][0] == 'L':
                controltmp = ttk.Label(win, text=tmp[3], 
                        font=('Arial', int(tmp[6])))
                controltmp.place(x=int(tmp[4]), y=int(tmp[5]), width=int(tmp[1]), height=int(tmp[2]))
                draggable(controltmp)
                win.update()
            
            elif len(tmp) == 6 and tmp[0][0] == 'B':
                controltmp = ttk.Button(win, text=tmp[3])
                controltmp.place(x=int(tmp[4]), y=int(tmp[5]), width=int(tmp[1]), height=int(tmp[2]))
                # controltmp = ttk.Button(win, text="alpha")
                # controltmp.place(x=501, y=305, width=200, height=150)
                draggable(controltmp)
                win.update()
            
            elif len(tmp) == 5 and tmp[0][0] == 'E':
                controltmp = ttk.Entry(win)
                controltmp.place(height=int(tmp[2]), x=int(tmp[3]), y=int(tmp[4]), width=int(tmp[1]))
                draggable(controltmp)
                win.update()
            
            elif tmp[0][0] == 'L':
                controltmp = ttk.LabelFrame(win, text=tmp[5])
                controltmp.place(width=int(tmp[1]), height=int(tmp[2]), x=int(tmp[3]), y=int(tmp[4]))
                draggable(controltmp)
                win.update()
            
            elif tmp[0][0] == 'C':
                controltmp = ttk.Radiobutton(win, text=tmp[1])
                controltmp.place(x=int(tmp[2]), y=int(tmp[3]))
                draggable(controltmp)
                win.update()

            elif tmp[0][0] == 'N':
                listof = tmp[5:]
                controltmp = ttk.Combobox(win, value=listof)
                controltmp.place(x=int(tmp[3]), y=int(tmp[4]), width=int(tmp[1]), height=int(tmp[2]))
                draggable(controltmp)
                win.update()      



def openfile():
    """打开项目文件"""
    global FILESTATUS
    FILESTATUS = filedialog.askopenfilename()
    if '.ggp' not in FILESTATUS:
        messagebox.showerror(message="文件格式不规范！", title="提示")
        return
    
    try:
        # 测试文件是否存在
        with open(FILESTATUS, 'r', encoding='utf-8') as f:
            pass
    
    except:
        messagebox.showerror(title="提示", message="文件不存在!")
        return
    _openit()

def rundoc():
    """
    打开说明网页
    """
    os.system('README.html')



def rungen():
    """
    生成Python文件
    具体实现在gen_py.genPy
    """
    global FILESTATUS
    if FILESTATUS == '未命名':
        messagebox.showerror(title="提示", message="你没有打开项目！")
        return

    gen_py.genPy(FILESTATUS)
    messagebox.showinfo(title="提示", message="代码生成成功，目录位于{}，请继续前往代码完成后端部分！编写完成以后，请点击生成EXE生成可执行文件！".format(FILESTATUS.split('.ggp')[0] + '.py'))


# 菜单栏

menubar = ttk.Menu(root)
genmenu = ttk.Menu(menubar) # 生成竖条
filemenu = ttk.Menu(menubar) # 项目竖条
docmenu = ttk.Menu(menubar) # 文档竖条
aboutmenu = ttk.Menu(menubar) # 关于竖条
menubar.add_cascade(label="项目", menu=filemenu)
filemenu.add_cascade(label="创建项目", command=projectcreate)
filemenu.add_cascade(label="打开项目", command=openfile)
filemenu.add_cascade(label="保存项目", command=filesave)
filemenu.add_separator()
menubar.add_cascade(label="生成", menu=genmenu)
genmenu.add_cascade(label="生成Python程序", command=rungen)
menubar.add_cascade(label="文档", menu=docmenu)
docmenu.add_cascade(label="使用方法", command=rundoc)
root.config(menu=menubar)

import easygui as g
# 左侧组件
LABELWIDTH = 10
framelabel = ttk.Frame(root, width=200, height=root.winfo_screenheight())
framelabel.pack(anchor="w")
labellabel = ttk.Button(framelabel, text="文本", width=LABELWIDTH, command=labn)
buttonlabel = ttk.Button(framelabel, text="按钮", width=LABELWIDTH, command=butn)
entrylabel = ttk.Button(framelabel, width=LABELWIDTH, text="输入框", command=entryn)
choicelabel = ttk.Button(framelabel, width=LABELWIDTH, text="选择框", command=chocien)
nPrlabel = ttk.Button(framelabel, width=LABELWIDTH, text="组合框", command=nprn)
alertlabel = ttk.Button(framelabel, width=LABELWIDTH, text="区域框", command=alertn)

# 左侧组件布局
for i in [labellabel, buttonlabel, entrylabel, choicelabel, nPrlabel, alertlabel]:
    i.pack(anchor='nw', pady=5)

# 操作界面
OPERATESECTIONWIDTH = root.winfo_screenwidth() - 400
OPERATESECTIONHEIGHT = root.winfo_screenheight() * OPERATESECTIONWIDTH / root.winfo_screenwidth()
OPERATESECTIONHEIGHT = int(OPERATESECTIONHEIGHT)
win.geometry('{}x{}'.format(OPERATESECTIONWIDTH, OPERATESECTIONHEIGHT))

root.mainloop()