from manim import *

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
    def exit_read(self):
        self.remove(self.read_head)
    def move_content(self,n:int=1,mask=False,fill:list[str]|str|None = None):
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
        if fill is None:
            fill = ["__"]*n
        elif isinstance(fill, str):
            fill = fill.split(" ")
        assert len(fill) == n
        for i,txt in enumerate(reversed(fill)):
            x=len(self.content)-i-1
            self[x][1] = Text('?' if mask else txt, font_size=24)
            self[x][1].move_to(self[x][0].get_center())
            action.append(FadeIn(self[x][1],shift=RIGHT*10))

        self.content = self.content[n:] + fill
        return action
                
    def edit_content(self,content:list[str]|str):
        if isinstance(content, str):
            content = content.split(" ")
        assert len(content) == len(self.content)
        action = []
        for i,txt in enumerate(content):
            # self[i][1].text = txt
            text = Text(txt, font_size=24).move_to(self[i][0].get_center())
            action.append(Transform(self[i][1],text))
        self.content = content
        return action
    def read(self,n:int=1):
        action =[]
        n=min(n,len(self.content)-self.read_idx)
        for i in range(1,n+1):
            current_grp = self[self.read_idx+i]
            old_txt = current_grp[1]
            new_txt = Text(self.content[self.read_idx+i], font_size=24,color=GREEN)
            new_txt.move_to(current_grp[0].get_center())
            # current_grp[1] = new_txt
            action.append(Transform(old_txt, new_txt))
        self.read_idx += n
        action.append(self.read_head.animate.move_to(self[self.read_idx][0].get_center()))
        return action
    def move_read_head(self,n:int):
        pos = self.read_idx + n
        assert 0 <= pos < len(self.content)
        self.read_idx = pos
        return [
            self.read_head.animate.move_to(self[self.read_idx][0].get_center())
        ]
class MutiHeadReader(Scene):
    def construct(self):
        watermark = Text("元路 · IFR-CV · 2025", font_size=20, color=YELLOW)
        watermark.to_corner(DOWN + RIGHT)
        watermark.shift(0.2 * LEFT + 0.2 * UP)
        self.add(watermark)

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
        serial = Buffer("XX XX XX XX 5C 00 00 00 00 00 00 00 EE A5 00 00 00 CC").next_to(txt_serial, RIGHT)
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
        txt_mmove = Text("将帧头置于buffer头", font_size=24).next_to(buffer, DOWN)
        buffer.exit_read()
        self.play(FadeIn(txt_mmove),FadeOut(txt_fond_5C),*buffer.move_content(4))
        self.wait(1)
        txt_append = Text("读取补充对应pkg长度(9-1=8)的内容", font_size=24).next_to(buffer, DOWN)
        self.play(FadeIn(txt_append),FadeOut(txt_mmove),*serial.read(8))
        self.play( *buffer.edit_content("5C 00 00 00 00 00 00 00 EE"))
        self.wait(1)

        txt_check = Text("校验CRC: ✓", font_size=24, color=GREEN).next_to(txt_append, DOWN)
        self.play(FadeIn(txt_check))
        txt_use = Text("使用数据", font_size=24).next_to(txt_check, DOWN)
        self.play(FadeIn(txt_use))
        txt_next = Text("执行下一次读取循环", font_size=24).next_to(txt_use, DOWN)
        self.play(FadeIn(txt_next))
        self.wait(1)
        self.play(FadeOut(txt_next), FadeOut(txt_use), FadeOut(txt_check),FadeOut(txt_append), *buffer.edit_content(['--']*len(buffer.content)))
        self.wait(1)
        txt_read_min_pkg = Text("读取min_pkg个字节: [A5 00 00 00 CC]", font_size=24).next_to(serial, DOWN)
        self.play(FadeIn(txt_read_min_pkg),FadeOut(txt_check_header),*serial.read(5))
        self.play( *buffer.edit_content("A5 00 00 00 CC __ __ __ __"))
        self.wait(1)
        txt_check_header = Text("查找HEADER(5C/A5)", font_size=24).next_to(serial, DOWN)
        self.play(FadeIn(txt_check_header),FadeOut(txt_read_min_pkg),*buffer.enter_read(mask=False))
        self.play(*buffer.read())
        txt_fond_A5 = Text("找到Header=0xA5", font_size=24, color=GREEN).next_to(buffer, DOWN)
        self.play(FadeIn(txt_fond_A5))
        self.wait(1)
        txt_mmove = Text("将帧头置于buffer头 (无需操作)", font_size=24).next_to(buffer, DOWN)
        buffer.exit_read()
        self.play(FadeIn(txt_mmove),FadeOut(txt_fond_A5))
        self.wait(1)
        txt_append = Text("读取补充对应pkg长度(5-5=0)的内容 (无需操作)", font_size=24).next_to(buffer, DOWN)
        self.play(FadeIn(txt_append),FadeOut(txt_mmove))
        self.wait(1)
        
        txt_check = Text("校验CRC: ✓", font_size=24, color=GREEN).next_to(txt_append, DOWN)
        self.play(FadeIn(txt_check))
        txt_use = Text("使用数据", font_size=24).next_to(txt_check, DOWN)
        self.play(FadeIn(txt_use))
        txt_next = Text("执行下一次读取循环", font_size=24).next_to(txt_use, DOWN)
        self.play(FadeIn(txt_next))
        self.wait(1)
        self.play(FadeOut(txt_next), FadeOut(txt_use), FadeOut(txt_check),FadeOut(txt_append), 
                  *buffer.edit_content(['--']*len(buffer.content)),*serial.move_read_head(-13),
                  *serial.move_content(13,True,"A5 A5 00 00 00 CC XX XX A5 00 00 00 CC")
                  )
        self.wait(1)
        txt_read_min_pkg = Text("读取min_pkg个字节: [A5 A5 00 00 00]", font_size=24).next_to(serial, DOWN)
        self.play(FadeIn(txt_read_min_pkg),FadeOut(txt_check_header),*serial.read(5))
        self.play( *buffer.edit_content("A5 A5 00 00 00 __ __ __ __"))
        self.wait(1)
        txt_check_header = Text("查找HEADER(5C/A5)", font_size=24).next_to(serial, DOWN)
        self.play(FadeIn(txt_check_header),FadeOut(txt_read_min_pkg),*buffer.enter_read(mask=False))
        self.play(*buffer.read())
        txt_fond_A5 = Text("找到Header=0xA5", font_size=24, color=GREEN).next_to(buffer, DOWN)
        self.play(FadeIn(txt_fond_A5))
        self.wait(1)
        txt_mmove = Text("将帧头置于buffer头 (无需操作)", font_size=24).next_to(buffer, DOWN)
        buffer.exit_read()
        self.play(FadeIn(txt_mmove),FadeOut(txt_fond_A5))
        self.wait(1)
        txt_append = Text("读取补充对应pkg长度(5-5=0)的内容 (无需操作)", font_size=24).next_to(buffer, DOWN)
        self.play(FadeIn(txt_append),FadeOut(txt_mmove))
        self.wait(1)
        
        txt_check = Text("校验CRC: ×", font_size=24, color=RED).next_to(txt_append, DOWN)
        self.play(FadeIn(txt_check))
        txt_use = Text("继续", font_size=24).next_to(txt_check, DOWN)
        self.play(FadeIn(txt_use))
        self.wait(1)
        self.play(FadeOut(txt_use), FadeOut(txt_check),FadeOut(txt_append),*buffer.enter_read(mask=False),*buffer.read(),*buffer.read())
        txt_fond_A5 = Text("找到Header=0xA5", font_size=24, color=GREEN).next_to(buffer, DOWN)
        self.play(FadeIn(txt_fond_A5))
        self.wait(1)
        txt_mmove = Text("将帧头置于buffer头", font_size=24).next_to(buffer, DOWN)
        buffer.exit_read()
        self.play(FadeIn(txt_mmove),FadeOut(txt_fond_A5),*buffer.move_content(1))
        self.wait(1)
        txt_append = Text("读取补充对应pkg长度(5-4=1)的内容", font_size=24).next_to(buffer, DOWN)
        self.play(FadeIn(txt_append),FadeOut(txt_mmove),*serial.read(1))
        self.play( *buffer.edit_content("A5 00 00 00 CC __ __ __ __"))
        self.wait(1)
        txt_check = Text("校验CRC: ✓", font_size=24, color=GREEN).next_to(txt_append, DOWN)
        self.play(FadeIn(txt_check))
        txt_use = Text("使用数据", font_size=24).next_to(txt_check, DOWN)
        self.play(FadeIn(txt_use))
        txt_next = Text("执行下一次读取循环", font_size=24).next_to(txt_use, DOWN)
        self.play(FadeIn(txt_next))
        txt_more1 = Text("...", font_size=24).next_to(txt_next, DOWN)
        self.play(FadeIn(txt_more1))
        txt_more2 = Text("...", font_size=24).next_to(txt_more1, DOWN)
        self.play(FadeIn(txt_more2))
        txt_more3 = Text("...", font_size=24).next_to(txt_more2, DOWN)
        self.play(FadeIn(txt_more3))
        self.wait(1)
        # self.play(FadeOut(txt_more3), FadeOut(txt_more2), FadeOut(txt_more1), FadeOut(txt_next), FadeOut(txt_use), FadeOut(txt_check),FadeOut(txt_append)
        #           )




        # for i in range(len(buffer.content)):
        #     buffer.read(self)
        #     self.wait(1)


        