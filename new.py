import pygame as pg
pg.init()
size=20
FPS=60
acc_gravity=9.8/FPS*2
clock=pg.time.Clock()
ms=pg.mixer
resolution=(1280,720)
window=pg.display.set_mode(resolution,pg.RESIZABLE)
font = pg.font.Font('freesansbold.ttf', 50)
pg.display.set_caption("game")
box=pg.Rect(100,100,size,size)
motion={"spx":0,"spy":0,"acx":0,"acy":0,"friction":0.05,"strength":0.1,"elasticity":0.8}
listlenlim=10
mouseposlist=[(0,0) for i in range(listlenlim)]
ms.init()
ms.music.set_volume(0.1)
ms.music.load("bounce.wav")
pg.mouse.heldobj=None
pg.display.isfullscreen=False
safedist=5

def distance(point_A,point_B):
    dist=((point_A[0]-point_B[0])**2 + (point_A[1]-point_B[1])**2)**(1/2)
    return dist

class scene():
    def __init__(self,list,function):
        self.name="ll"

class obsticle():
    oblist=[]
    def __init__(self,size,center,color,isrigid):
        self.rect=pg.Rect(center[0]-size[0]/2,center[1]-size[1]/2,size[0],size[1])
        self.color=color
        obsticle.oblist.append(self)
        self.isrigid=isrigid
        self.speed=(0,0)
        self.isbrick=False
        
    
    def display(self):
        pg.draw.rect(window,self.color,self.rect)

class moving_obsticle(obsticle):
    def __init__(self, size, center, color,rigidity,elasticity,r=(False,False)):
        super().__init__(size, center, color,rigidity)
        self.r=r
        self.restricted_x=r[0]
        self.restricted_y=r[1]
        self.collidedobst=None
        self.speed=(0,0)
        self.elasticity=elasticity
        self.mouseplaced=(0,0)
        
    def work(self,mousepos,mousespeed,pressed_mb,eventlist):

        if self.collidedobst==None:
            self.restricted_x=self.r[0]
            self.restricted_y=self.r[1]

        for event in eventlist:
            if event.type==pg.MOUSEBUTTONUP:
                if pg.mouse.heldobj==self:
                    pg.mouse.heldobj=None
            if self.rect.collidepoint(mousepos) and event.type==pg.MOUSEBUTTONDOWN:
                self.mouseplaced=(self.rect.centerx-mousepos[0],self.rect.centery-mousepos[1])

        if pressed_mb[0] and self.rect.collidepoint(mousepos):
            if pg.mouse.heldobj==None or pg.mouse.heldobj==self:
                pg.mouse.heldobj=self
                    
        if pg.mouse.heldobj==self:

            if (not self.collidedobst==None) and self.collidedobst.isrigid:
                movementallowed_x=(self.rect.centerx>self.collidedobst.rect.centerx and mousespeed[0]>0) or (self.rect.centerx<self.collidedobst.rect.centerx and mousespeed[0]<0)
                movementallowed_y=(self.rect.centery>self.collidedobst.rect.centery and mousespeed[1]>0) or (self.rect.centery<self.collidedobst.rect.centery and mousespeed[1]<0)
                
                if (not movementallowed_x) and movementallowed_y:
                    self.rect.y=mousepos[1]-self.rect.height/2+self.mouseplaced[1]
                if (not movementallowed_y) and movementallowed_x:
                    self.rect.x=mousepos[0]-self.rect.width/2+self.mouseplaced[0]
                if not (movementallowed_x and movementallowed_y):
                    pass

            else:
                if not self.restricted_y:
                    self.rect.y=mousepos[1]-self.rect.height/2+self.mouseplaced[1]
                if not self.restricted_x:
                    self.rect.x=mousepos[0]-self.rect.width/2+self.mouseplaced[0]
                self.speed=mousespeed
        if pg.mouse.heldobj!=self:
            self.speed=(0,0)

        for obst in obsticle.oblist:
            if self.rect.colliderect(obst.rect) and not obst==self:
                self.collidedobst=obst
                collide_x=abs(self.rect.centerx-obst.rect.centerx)<(self.rect.width+obst.rect.width)/2
                collide_y=abs(self.rect.centery-obst.rect.centery)<(self.rect.height+obst.rect.height)/2
                if collide_x:
                    self.restricted_x=True
                elif collide_y:
                    self.restricted_y=True
            elif not self.rect.colliderect(obst.rect):
                self.collidedobst=None

class brick(obsticle):
    bricks=[]
    def __init__(self,size,center,color,life_int):
        super().__init__(size,center,color,True)
        self.touches=life_int
        self.isbrick=True
        self.elasticity=1
        brick.bricks.append(self)

    @classmethod
    def getlist(cls):
        return cls.bricks

    

class ball():
    blist=[]
    def __init__(self,position,diameter,color,motion_variables_dict):
        self.rect=pg.Rect(position[0],position[1],diameter,diameter)
        self.motion=motion_variables_dict
        self.size=diameter
        self.color=color
        self.elasticity=self.motion["elasticity"]
        ball.blist.append(self)

    def physics(self,coordinate,keylist,keypositive,keynegetive,res):
        acceleration="ac"+coordinate
        speed="sp"+coordinate

        if coordinate=="x":
            self.rect.x+=round(self.motion["spx"])
        if coordinate=="y":
            self.rect.y+=round(self.motion["spy"])

        self.motion[speed]+=self.motion[acceleration]

        if keylist[keypositive]:
            self.motion[acceleration]=self.motion["strength"]
        elif keylist[keynegetive]:
            self.motion[acceleration]=-self.motion["strength"]
        
        if not (keylist[keypositive] or keylist[keynegetive]):
            self.motion[acceleration]=0

        if not round(self.motion[speed])==0:
            if self.motion[speed]>0:
                self.motion[speed]=(self.motion[speed]-self.motion["friction"])
            if self.motion[speed]<0:
                self.motion[speed]=(self.motion[speed]+self.motion["friction"])

    def work(self,mouse_speed,mousepos,pressed_mb,pressed_keys,resolution,eventlist):      
        self.physics("x",pressed_keys,pg.K_d,pg.K_a,resolution)
        self.physics("y",pressed_keys,pg.K_s,pg.K_w,resolution)
        for event in eventlist:
            if event.type==pg.MOUSEBUTTONUP:
                if pg.mouse.heldobj==self:
                    self.motion["spx"]=mouse_speed[0]
                    self.motion["spy"]=mouse_speed[1]
                    pg.mouse.heldobj=None

        if pressed_mb[0] and distance(mousepos,self.rect.center)<size:
            if pg.mouse.heldobj==None or pg.mouse.heldobj==self:
                pg.mouse.heldobj=self

        if pg.mouse.heldobj==self:
            self.rect.x=mousepos[0]-self.rect.width/2
            self.rect.y=mousepos[1]-self.rect.height/2

        if self.rect.x>=resolution[0]-(self.rect.width) or self.rect.x<=0:
            self.motion["spx"]=self.motion["spx"]*-1*self.elasticity
            if resolution[0]-self.rect.center[0] < self.rect.center[0]:
                self.rect.x-=safedist
            else:
                self.rect.x+=safedist
            ms.music.play()

        elif  self.rect.y<=0: #self.rect.y>=resolution[1]-(self.rect.height) or
            self.motion["spy"]=self.motion["spy"]*-1*self.elasticity
            if resolution[1]-self.rect.center[1] < self.rect.center[1]:
                self.rect.y-=safedist
            else:
                self.rect.y+=safedist
            ms.music.play()

        for obst in obsticle.oblist:
            if self.rect.colliderect(obst.rect):
                ms.music.play()
                if obst.isbrick:
                    obst.touches-=1
                if abs(self.rect.centerx-obst.rect.centerx)-obst.rect.width/2 > abs(self.rect.centery-obst.rect.centery)-obst.rect.height/2:
                    self.motion["spx"]=self.motion["spx"]*-1*self.elasticity + obst.speed[0]*self.elasticity*obst.elasticity
                    if self.rect.centerx<obst.rect.centerx:
                        self.rect.x-=safedist
                    else:
                        self.rect.x+=safedist
                elif abs(self.rect.centerx-obst.rect.centerx)-obst.rect.width/2 < abs(self.rect.centery-obst.rect.centery)-obst.rect.height/2:
                    self.motion["spy"]=self.motion["spy"]*-1*self.elasticity + obst.speed[1]*self.elasticity*obst.elasticity
                    if self.rect.centery<obst.rect.centery:
                        self.rect.y-=safedist
                    else:
                        self.rect.y+=safedist
                else:
                    self.motion["spy"]=self.motion["spy"]*-1*self.elasticity
                    self.motion["spx"]=self.motion["spx"]*-1*self.elasticity

    def display(self):
        pg.draw.circle(window,self.color,self.rect.center,self.size/2)

class button():
    def __init__(self,size,position):
        self.size=size
        self.position=position
        self.rect=pg.Rect(position[0],position[1],size[0],size[1])
        self.surface=pg.Surface(size)
    def is_clicked(self):
        bool1= pg.mouse.get_pressed()[0] and self.rect.collidepoint(pg.mouse.get_pos())
        return bool1

ballpos=(600,600)
b1=ball(ballpos,20,(0,0,200),{"spx":0,"spy":0,"acx":0,"acy":0,"friction":0.0,"strength":acc_gravity,"elasticity":1})   
beam=moving_obsticle((100,10),(100,window.get_height()-5),(255,100,100),True,1,(False,True))
positive=button((10,10),(600,50))
negetive=button((100,100),(650,50))
brickwidth=50
brickheight=20

def createbricks():
    for i in range(14):
        x=(i+1.5)*(brickwidth+30)
        for j in range(12):
            y=(j+1)*(brickheight+20)
            b=brick((brickwidth,brickheight),(x,y),(200,200,200),5)

createbricks()
gamerunning=True


def get_mouse_speed():
    cursor_position=pg.mouse.get_pos()
    mouseposlist.append(cursor_position)

    if len(mouseposlist)>10:
        mouseposlist.pop(0)

    avg_mousespeed_x=average([mouseposlist[l+1][0]-mouseposlist[l][0] for l in range(listlenlim-1)])
    avg_mousespeed_y=average([mouseposlist[l+1][1]-mouseposlist[l][1] for l in range(listlenlim-1)])
    return (avg_mousespeed_x,avg_mousespeed_y)

def reset():
    for i in brick.bricks:
        if i in obsticle.oblist:
            obsticle.oblist.remove(i)

    brick.bricks=[]
    b1.rect.center=ballpos
    b1.motion["spx"]=0;b1.motion["spy"]=0
    createbricks()
    global gamerunning
    gamerunning=True

def gameoverscreen():
    if len(brick.bricks)<=0:
        s="You win"
    else:
        s="Game Over"

    pressed_keys=pg.key.get_pressed()
    window.fill((0,0,0))
    text=font.render(s,True,(255,255,255))
    text1=font.render("press ESC to retry",True,(255,255,255))
    window.blit(text,(window.get_width()/2-text.get_width()/2,window.get_height()/2-text.get_height()/2))
    window.blit(text1,(window.get_width()/2-text1.get_width()/2,window.get_height()/2+text1.get_height()/2))
    if pressed_keys[pg.K_ESCAPE]:
        reset()   

def maingamerun(eventlist):
    newres=(window.get_width(),window.get_height())
    mousepos=pg.mouse.get_pos()
    pressed_keys=pg.key.get_pressed()
    pressed_mb=pg.mouse.get_pressed()
    mouse_speed=get_mouse_speed()
    window.fill((0,0,0))
    if b1.rect.y>window.get_height():
        global gamerunning
        gamerunning=False
    b1.display()
    for i in obsticle.oblist:
        i.display()
    b1.work(mouse_speed,mousepos,pressed_mb,pressed_keys,newres,eventlist)
    beam.work(mousepos,mouse_speed,pressed_mb,eventlist)
    for b in brick.bricks:
        if b.touches<=0 and b in obsticle.oblist:
            obsticle.oblist.pop(obsticle.oblist.index(b))

def average(numbers):
    num=0
    for i in numbers:
        num+=i
    avg=num/len(numbers)
    return avg

currentfunc=maingamerun
def main():
    counter=0
    run=True
    while run:
        pg.mouse.heldobj=beam
        eventlist=pg.event.get()
        pressed_keys=pg.key.get_pressed()
        clock.tick(FPS)
        if pressed_keys[pg.K_f]:
            if not pg.display.isfullscreen:
                pg.display.set_mode(resolution,pg.RESIZABLE)
                pg.display.isfullscreen=True
            else:
                pg.display.isfullscreen=False
            pg.display.toggle_fullscreen()
        if gamerunning:
            maingamerun(eventlist)
        else:
            gameoverscreen()
        pg.display.update()
        for event in eventlist:
            if event.type==pg.QUIT:
                run=False
    pg.quit()



if __name__=="__main__":
    main()


