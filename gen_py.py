"""
@@@@@@@@@@@@@@@@@@@@@@@@
@                      @
@ 作者：Wdataorg        @
@ 日期：2023/1          @
@ 项目：GUI-GUI         @
@ 版本：v0.0.1          @
@                      @
@@@@@@@@@@@@@@@@@@@@@@@@

接口说明：

此接口用于GUI-GUI的项目.ggp文件的Python源代码生成，可以在接口gui_main运行时使用。

导入方式：
import gen_py

使用方法：
gen_py.genPy(FILESTATUS)
@FILESTATUS: FILESTATUS要求为绝对路径，为.ggp文件地址

依赖包：
无
"""

def _write(FILESTATUS, writecontent):
    """私有类型"""
    openf = FILESTATUS.split('.ggp')[0] +'.py'
    with open(openf, 'a+', encoding='utf-8') as f:
        f.write(writecontent)

def genPy(FILESTATUS):
    """
    生成python文件
    @FILESTATUS: 输入一个绝对路径，表示原项目文件的地址
    动作：打开同目录同名的py文件，并且格式化写入python源代码
    返回：无
    """

    with open(FILESTATUS, 'r', encoding='utf-8') as file:
        rc = file.readlines()
    
    with open(FILESTATUS.split('.ggp')[0] + '.py', 'w', encoding='utf-8') as f:
        pass
    
    for i in rc:
        if i == '\n':
            rc.remove(i)
    
    new_write = lambda content : _write(FILESTATUS, content)
    new_write('import ttkbootstrap as ttk\n\n')
    new_write("root = ttk.Window(position=({}, {}), alpha={}, themename='{}', title='{}')\n\n"
    .format(rc[3].split('->')[1], rc[3].split('->')[2].split('\n')[0], 
    rc[4].split('->')[1], rc[5].split('->')[1].split('\n')[0], rc[1].split('->')[1].split('\n')[0]))
    new_write("root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))\n")
    if rc[2].split('Icon Path->')[1] != 'false\n':
        new_write("root.iconbitmap(r'{}')\n".format(rc[2].split('Icon Path->')[1].split('\n')[0]))

    for i in range(6, len(rc)):
        typkase = rc[i].split('->')[0]
        if rc[i][0] == 'B':
            width = rc[i].split('->')[1]
            height = rc[i].split('->')[2]
            text = rc[i].split('->')[3]
            x = rc[i].split('->')[4]
            y = rc[i].split('->')[5].split('\n')[0]
            new_write('{} = ttk.Button(root, text="{}")\n'.format(typkase, text))
            new_write('{}.place(width={}, height={}, x={}, y={})\n'.format(typkase, width, height, x, y))
        
        elif rc[i][0] == 'E':
            width = rc[i].split('->')[1]
            height = rc[i].split('->')[2]
            x = rc[i].split('->')[3]
            y = rc[i].split('->')[4].split('\n')[0]
            new_write('{} = ttk.Entry(root)\n'.format(typkase))
            new_write('{}.place(width={}, height={}, x={}, y={})\n'.format(typkase, width, height, x, y))
        
        elif rc[i][0] == 'C':
            text = rc[i].split('->')[1]
            x = rc[i].split('->')[2]
            y = rc[i].split('->')[3].split('\n')[0]
            new_write('{} = ttk.Radiobutton(root, text="{}")\n'.format(typkase, text))
            new_write('{}.place(x={}, y={})\n'.format(typkase, x, y))

        elif rc[i][0] == 'N':
            width = rc[i].split('->')[1]
            height = rc[i].split('->')[2]
            x = rc[i].split('->')[3]
            y = rc[i].split('->')[4]
            choicesall = rc[i].split('->')[5:]
            choicesall[-1] = choicesall[-1].split('\n')[0]
            new_write('{} = ttk.Combobox(root, value={})'.format(typkase, choicesall))
            new_write('\n{}.place(width={}, height={}, x={}, y={})\n'.format(typkase, width, height, x, y))
        
        elif  'LabelFrame' in rc[i].split('->')[0]:
            width = rc[i].split('->')[1]
            height = rc[i].split('->')[2]
            text = rc[i].split('->')[5].split('\n')[0]
            x = rc[i].split('->')[3]
            y = rc[i].split('->')[4].split('\n')[0]
            new_write('{} = ttk.LabelFrame(root, text="{}")\n'.format(typkase, text))
            new_write('{}.place(width={}, height={}, x={}, y={})\n'.format(typkase, width, height, x, y))
        
        


        elif  'Label' in rc[i].split('->')[0] :
            """这里不要写rc[i][0] == 'L'，因为LabelFrame组件开头也是L"""
            width = rc[i].split('->')[1]
            height = rc[i].split('->')[2]
            text = rc[i].split('->')[3]
            x = rc[i].split('->')[4]
            y = rc[i].split('->')[5]
            print(rc[i].split('->'))
            fsize = rc[i].split('->')[6].split('\n')[0]
            new_write('{} = ttk.Label(text="{}", font=("Arial", {}))\n'.format(typkase, text, fsize))
            new_write('{}.place(width={}, height={}, x={}, y={})\n'.format(typkase, width, height, x, y))
        
       
    new_write("root.mainloop()\n")            


# genPy('./t.ggp')