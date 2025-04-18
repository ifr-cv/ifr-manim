from manim import *

class Scene1_ProcessDifferentHeaders(Scene):
    def construct(self):
        # 定义元素
        buffer = Rectangle(width=6, height=0.5, color=WHITE).shift(UP*2)
        data_stream = Text("数据流: [0x01][AA][D1][D2][BB][D3][D4][D5][D6]").scale(0.6).next_to(buffer, DOWN)
        
        # 动画：显示初始状态
        self.play(Create(buffer), Write(data_stream))
        self.wait(1)

        # 步骤3a: 读取 min_pkg(假设min_pkg=4)
        self.play(Indicate(buffer), run_time=0.5)
        min_pkg_arrow = Arrow(start=LEFT, end=RIGHT).next_to(buffer, LEFT)
        min_pkg_label = Text("读取 min_pkg=4", font_size=24).next_to(min_pkg_arrow, LEFT)
        self.play(Create(min_pkg_arrow), Write(min_pkg_label))
        self.wait(1)

        # 步骤3a-i: 偏移量i=0时检测Header
        header_check = Text("检查偏移i=0: Header=0x01 (无效)", color=RED, font_size=24).next_to(buffer, DOWN)
        self.play(Write(header_check))
        self.wait(1)
        self.play(FadeOut(header_check))

        # 偏移量i=1时发现有效Header=0xAA
        header_found = Text("i=1: 发现Header=0xAA (Pkg1)", color=GREEN, font_size=24).next_to(buffer, DOWN)
        self.play(Write(header_found))
        self.wait(1)

        # 步骤3a-ii: 移动数据到buffer头部
        move_arrow = CurvedArrow(buffer.get_left()+LEFT, buffer.get_left(), color=YELLOW)
        self.play(Create(move_arrow))
        self.play(buffer.animate.shift(LEFT*1), run_time=0.5)
        self.wait(1)

        # 步骤3a-iv: 补充数据并校验通过
        new_data = Text("补充数据 [D3][D4]", color=GREEN, font_size=24).next_to(buffer, RIGHT)
        check_mark = Text("✓ CRC校验通过", color=GREEN).next_to(buffer, DOWN)
        self.play(Write(new_data), Write(check_mark))
        self.wait(2)

class Buffer(VGroup):
    """代表串口缓冲区"""
    def __init__(self,content:list[str]|str,desc:str=None, **kwargs):
        super().__init__(**kwargs)
        if isinstance(content, str):
            content = content.split(" ")
        for i,txt in enumerate(content):
            square = Square(side_length=0.5)
            text = Text(txt, font_size=24)
            text.move_to(square.get_center())
            grp = VGroup(square, text)
            grp.shift(RIGHT * (i * 0.5 + 0.25))
            self.add(grp)
        if desc:
            self.add(Text(desc, font_size=24).next_to(self, DOWN))
        self.content = content
    def enter_read(self,mask=True):
            self.read_head = Rectangle(height=0.7,width=0.5,color=YELLOW,fill_opacity=0.2)
            self.read_head.next_to(self[0][0],LEFT,buff=0.1)
            self.add(self.read_head)
            action = []
            if mask:
                for i in range(len(self.content)):
                    old = self[i][1] 
                    self[i][1] =Text("?", font_size=24,color=RED)
                    self[i][1].move_to(old.get_center())
                    action.append(Transform(old,self[i][1]))
            self.read_idx= -1
            action.append(FadeIn(self.read_head))
            return action
    def move_content(self,n:int=1):
        # 将buffer整体向前移动n个字节
        action = []
        for i in range(len(self.content)):
            curr_grp = self[i]
            tar_i = i-n
            if tar_i < 0:
                action.append(FadeOut(curr_grp[1],shift=LEFT*10,scale=0.1))
            else:
                tar_grp = self[tar_i]
                action.append(curr_grp[1].animate.move_to(tar_grp[0].get_center()))
                tar_grp[1] = curr_grp[1]
        for i in range(n):
            x=len(self.content)-i-1
            self[x][1] = Text("__", font_size=24)
            self[x][1].move_to(self[x][0].get_center())
            action.append(FadeIn(self[x][1],shift=RIGHT*10,scale=0.1))

        return action
                
    def edit_content(self,content:list[str]|str):
        if isinstance(content, str):
            content = content.split(" ")
        assert len(content) == len(self.content)
        for i,txt in enumerate(content):
            self[i][1].text = txt
    def read(self,n:int=1):
        action =[]
        n=min(n,len(self.content)-self.read_idx)
        for i in range(1,n+1):
            current_grp = self[self.read_idx+i]
            old_txt = current_grp[1]
            new_txt = Text(self.content[self.read_idx+i], font_size=24,color=GREEN)
            new_txt.move_to(current_grp[0].get_center())
            current_grp[1] = new_txt
            action.append(Transform(old_txt, new_txt))
        self.read_idx += n
        action.append(self.read_head.animate.move_to(self[self.read_idx][0].get_center()))
        return action

class A(Scene):
    def construct(self):
        sx,sy = 0, config.frame_y_radius
        imu_data = Buffer("5C XX XX XX XX XX XX XX cc", "IMU数据")
        imu_data = imu_data.move_to(np.array([sx,sy-imu_data.get_height(),0]))
        referee_data = Buffer("A5 XX XX XX cc", "裁判系统数据").next_to(imu_data, DOWN)
        pkg_desc = Text("XX代表任意一个字节, cc代表CRC校验码", font_size=24).next_to(referee_data, DOWN)

        # 展示pkg结构
        self.play(FadeIn(imu_data), FadeIn(referee_data), FadeIn(pkg_desc))
        self.wait(3)
        txt_setReader = Text("调用setMultiHeadReader()时计算:", font_size=24).next_to(pkg_desc, DOWN)
        txt_min_max_pkg_grp = VGroup()
        txt_setReader_min_pkg = Text("min_pkg=5", font_size=24)
        txt_setReader_max_pkg = Text("max_pkg=9", font_size=24).next_to(txt_setReader_min_pkg, DOWN)
        txt_min_max_pkg_grp.add(txt_setReader_min_pkg, txt_setReader_max_pkg).next_to(txt_setReader, DOWN)
        self.play(FadeIn(txt_setReader), FadeIn(txt_min_max_pkg_grp))
        self.wait(2)
        self.play(FadeOut(imu_data), FadeOut(referee_data), FadeOut(pkg_desc), FadeOut(txt_setReader))
        
        # 展示min_pkg和max_pkg
        txt_setReader_max_pkg.next_to(txt_setReader_min_pkg, RIGHT)
        self.play(txt_min_max_pkg_grp.animate.move_to(np.array([sx,sy-txt_min_max_pkg_grp.get_height(),0])))

        txt_serial = Text("serial = ", font_size=24)
        txt_serial.move_to(np.array([-config.frame_x_radius+txt_serial.get_width()/2,sy-txt_min_max_pkg_grp.get_height()*3,0]))
        serial = Buffer("XX XX XX XX 5C 00 00 00 00 00 00 00 EE").next_to(txt_serial, RIGHT)
        serial.enter_read()
        self.play(FadeIn(txt_serial), FadeIn(serial))
        self.wait(2)
        self.play(*serial.read(5))
        txt_read_min_pkg = Text("读取min_pkg个字节: [XX XX XX XX 5C]", font_size=24).next_to(serial, DOWN)
        txt_buffer = Text("buffer = ", font_size=24).next_to(txt_read_min_pkg, DOWN)
        # 移动到最左侧
        txt_buffer.move_to(np.array([-config.frame_x_radius+txt_buffer.get_width()/2,txt_buffer.get_center()[1],0]))
        buffer = Buffer("XX XX XX XX 5C __ __ __ __").next_to(txt_buffer, RIGHT)
        self.play(FadeIn(txt_read_min_pkg),FadeIn(txt_buffer),FadeIn(buffer))
        self.wait(2)
        txt_check_header = Text("查找HEADER(5C/A5)", font_size=24).next_to(serial, DOWN)

        self.play(FadeIn(txt_check_header),FadeOut(txt_read_min_pkg),*buffer.enter_read(mask=False))
        for i in range(5):
            self.play(*buffer.read())
        txt_fond_5C = Text("找到Header=0x5C", font_size=24, color=GREEN).next_to(buffer, DOWN)
        self.play(FadeIn(txt_fond_5C))
        self.wait(1)
        txt_mmove = Text("memmove", font_size=24).next_to(buffer, DOWN)
        self.play(FadeIn(txt_mmove),FadeOut(txt_fond_5C),*buffer.move_content(4))

        # for i in range(len(buffer.content)):
        #     buffer.read(self)
        #     self.wait(1)


        
class Scene2_CRCError(Scene):
    def construct(self):
        buffer = Rectangle(width=6, height=0.5, color=WHITE).shift(UP*2)
        data_stream = Text("数据流: [AA][D1][D2][CRC=ERROR][BB][D3][D4][D5]").scale(0.6).next_to(buffer, DOWN)
        
        self.play(Create(buffer), Write(data_stream))
        self.wait(1)

        # 检测到Header但CRC错误
        error_text = Text("Header=0xAA 校验失败!", color=RED).next_to(buffer, DOWN)
        self.play(Write(error_text))
        self.wait(1)

        # 显示错误处理：丢弃数据
        cross = Cross(buffer, color=RED)
        self.play(Create(cross))
        self.play(buffer.animate.set_color(RED), FadeOut(cross))
        self.wait(1)
class Scene3_ResidualData(Scene):
    def construct(self):
        buffer = Rectangle(width=6, height=0.5, color=WHITE).shift(UP*2)
        data_stream = Text("数据流: [FF][FF][AA][D1][D2][D3]").scale(0.6).next_to(buffer, DOWN)
        
        self.play(Create(buffer), Write(data_stream))
        self.wait(1)

        # 显示无效数据段[FF][FF]
        invalid_highlight = SurroundingRectangle(buffer, color=RED, buff=0)
        self.play(Create(invalid_highlight))
        self.wait(1)

        # 移动有效数据到buffer头部
        move_arrow = Arrow(buffer.get_corner(DR), buffer.get_corner(DL), color=YELLOW)
        self.play(Create(move_arrow))
        self.play(buffer.animate.shift(LEFT*2), run_time=0.5)
        self.wait(2)