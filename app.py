import pygame,sys
import random
from random import choice, randrange

pygame.font.init() #oyunu başlat

#kare boyutu : 20x30 kare boyutu
block_size = 20 
block_width=20
block_height=30
#oyun alanı
GAME_RES = block_width * block_size, block_height * block_size  

#ekran
s_width=800
s_height=810

sc = pygame.display.set_mode((s_width,s_height)) #görüntüleme yüzeyi nesnesi
game_sc = pygame.Surface(GAME_RES) #oyun alanı

clock = pygame.time.Clock() #record
FPS =3

pygame.display.set_caption('Tetris')


# COLORS *********************************************************************
white = (255, 255, 255)
yellow=(255, 255, 0)
green = (0, 255, 0)
BLACK = (21, 24, 29)
BLUE = (31, 25, 76)
RED = (252, 91, 122)
#shape_colors =[green, (255, 0, 0), (0, 255, 255), yellow, (255, 165, 0), (0, 0, 255), (128, 0, 128)]

#Loading Sounds & Music **************************************************************
pygame.mixer.init()
music = pygame.mixer.music.load('Music/music.mp3')
#pygame.mixer.music.play(-1) # -1 will ensure the song keeps looping

# Images ********************************************************************* 
img1 = pygame.image.load('Assets/1.png')
img2 = pygame.image.load('Assets/2.png')
img3 = pygame.image.load('Assets/3.png')
img4 = pygame.image.load('Assets/4.png')

Assets = {
	1 : img1,
	2 : img2,
	3 : img3,
	4 : img4
}
imp = pygame.image.load('img/a.jpg').convert() #üzerine görüntünün çizildiği yüzey nesnesi
game_imp = pygame.image.load('img/b.jpg').convert()

# FONTS  **********************************************************************
#yazı tipi nesnesi: (dosya,yazı tipi boyutu)
font = pygame.font.Font('freesansbold.ttf', 60) 
font2 =pygame.font.Font('freesansbold.ttf', 40) 

title_tetris = font.render('TETRIS', True, pygame.Color('red'))
title_score = font2.render('Score:', True, pygame.Color('gray'))
title_level = font2.render('Level:', True, pygame.Color('gray'))
title_next_shape = font2.render('Next Shape:', True, pygame.Color('gray'))
title_record =font2.render('Record:', True, pygame.Color('gray'))

# OBJECTS ********************************************************************
class Tetramino: 
    #matrix
    #0   1   2   3
    #4   5   6   7
    #8   9   10  11
    #12  13  14  15
    FIGURES = { #dictionary list:key ile erişilir.
	'I' : [[1, 5, 9, 13], [4, 5, 6, 7]], #key:value
    'Z' : [[4, 5, 9, 10], [2, 6, 5, 9]],
    'S' : [[6, 7, 9, 10], [1, 5, 6, 10]],
    'L' : [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
    'J' : [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
    'T' : [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
    'O' : [[1, 2, 5, 6]]
    }
    TYPES = ['I', 'Z', 'S', 'L', 'J', 'T', 'O'] #liste

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.type=random.choice(self.TYPES) #I
        self.shape=self.FIGURES[self.type]
        self.color=random.randint(1,4)
        self.rotation=0
        self.record = self.get_record()
        
    def image(self):
        return self.shape[self.rotation]
    def rotate(self):
        self.rotation=(self.rotation+1)%len(self.shape)

    @classmethod
    def get_record(cls):
        try:
            with open('record') as file:
                return int(file.readline().strip())
        except FileNotFoundError:
            return 0

    @classmethod
    def set_record(cls, score):
        with open('record', 'w') as file:
            file.write(str(score))

# t=Tetramino(5,0)
# image=t.image() #şekil ekrana gelir

class Shape():
    def __init__(self): #constructor
        self.next=None
        self.level = 1
        self.gameover=False
        self.board = [[0 for j in range(block_width)] for i in range(block_height)]
        self.score=0
        #self.shape=self.FIGURES[random.choice[self.TYPES]]
        #self.color= shape_colors[TYPES.index(self.TYPES)] #gelen şeklin indexine göre renk atanır
        self.figure=[]
        self.get_shape()
        self.update_record()  # Update record from file

    def get_shape(self): #şekilleri random getirir.
        if not self.next:
            self.next=Tetramino(5,0)
        self.figure.append(self.next) #gelen şekil suan figure uzerinden erişicez.x,y,rotation değişkenleri mevcut.
        self.next=Tetramino(5,0)
        
    def rotateShapes(self,event):
        if event.type == pygame.KEYDOWN: #1024 ,32783,768,769 eventtype
            if not self.gameover:
                if event.key == pygame.K_LEFT:
                    self.figure[-1].x -= 1
                    if self.check_borders(): #eger kesişim varsa
                        self.figure[-1].x += 1
                if event.key == pygame.K_RIGHT:
                    self.figure[-1].x += 1
                    if self.check_borders(): #eger kesişim varsa
                        self.figure[-1].x -= 1
                if event.key == pygame.K_UP: #dönme   
                    rotation =self.figure[-1].rotation #0
                    self.figure[-1].rotate()
                    if self.check_borders(): #eger kesişim varsa
                        self.figure[-1].rotation = rotation
                        
                if event.key == pygame.K_DOWN:
                    self.figure[-1].y += 1
                    if self.check_borders(): #eger kesişim varsa
                        self.figure[-1].y -=1
                if event.key == pygame.K_SPACE: #direkt aşagı inme
                    while not self.check_borders():
                        self.figure[-1].y += 1
                    self.figure[-1].y -= 1
                    self.isteOZaman()

            if event.key == pygame.K_r:
                self.__init__()
			
    def check_borders(self): #sınırları kontrol eder
        intersection = False #şekil başta oyun alanı içinde
        for i in range(4): #şekil 4 kareden oluştuğu için
            for j in range(4):
                    if i * 4 + j in self.figure[-1].image():
                        if i + self.figure[-1].y > block_height - 1 or \
                        j + self.figure[-1].x > block_width - 1 or \
                        j + self.figure[-1].x < 0 or \
                        self.board[i + self.figure[-1].y][j + self.figure[-1].x] > 0:
                         intersection = True
        return intersection

    def update_record(self):
        self.record = Tetramino.get_record()  # Use the static method to get the record

    def delete_line(self): #satırı sıl
        rerun = False
        for y in range(block_height-1, 0, -1):
            is_full = True
            for x in range(0,block_width):
                if self.board[y][x] == 0:
                    is_full = False
            if is_full:
                del self.board[y]
                self.board.insert(0, [0 for i in range(block_width)])
                self.score += 1
                if self.score % 20 == 0: #genislik 20 
                    self.level += 1
                rerun = True

        if rerun:
            self.delete_line()

        if self.score > self.record:
            self.record = self.score
            Tetramino.set_record(self.record)  # Use the static method to set the record

    def isteOZaman(self):
        #parça yere geldiği zaman 
        for i in range(4):
            for j in range(4):
                if i*4 +j in self.figure[-1].image():
                    self.board[i + self.figure[-1].y][j + self.figure[-1].x] = self.figure[-1].color
        self.delete_line()
        self.get_shape() #2. şekil gelir
        if self.check_borders():
            self.gameover=True

    def go_down(self): #şeklin otomatık olarak aşagı inmesi
        self.figure[-1].y += 1
        if self.check_borders(): #şekil dolu kareye denk geliyorsa hareketi kısıtla.
            self.figure[-1].y -= 1
            self.isteOZaman()
          
class Control(Shape): 
    def __init__(self,shape):
        Shape.__init__(self)
        self.shape=shape  

    def game_over(self): #oyun bittiğinde ekrana verilecekler
        rect = pygame.Rect((50, 100, 350, 350))
        pygame.draw.rect(game_sc, white, rect)
        pygame.draw.rect(game_sc, RED, rect, 2)

        over = font2.render('Game Over', True, RED)
        msg1 = font2.render('Press r to restart', True, BLACK)
        msg2 = font2.render('Press esc to quit', True, BLACK)

        game_sc.blit(over, (rect.centerx-over.get_width()/2, rect.y + 20))
        game_sc.blit(msg1, (rect.centerx-msg1.get_width()/2, rect.y + 100))
        game_sc.blit(msg2, (rect.centerx-msg2.get_width()/2, rect.y + 150))

def create_grid():
    #pygame.Rect nesnesi
    grid = [pygame.Rect(x * block_size, y * block_size, block_size, block_size) #x,y,genişlik,yükseklik
    for x in range(block_width) 
    for y in range(block_height)]

    [pygame.draw.rect(game_sc, white, i_rect,1) for i_rect in grid] #oyun yüzeyine-beyaz-pygame Rect nesnesini çizer.

#*****************************************************************************************************************
tetris = Shape()
control=Control(tetris)

def main():
    run=True
    global change_piece 
    
#While*********************************************************************************************
    while run:
        if not tetris.gameover:
            tetris.go_down() #control.go_down() #şeklin aşagı inmesi
        
#EVENT HANDLING ************************************************************************************
        for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.QUIT:
                        run=False  #oyunu bitir
                    if event.key  == pygame.K_ESCAPE:
                        run=False #oyunu bitir
                    else:
                        tetris.rotateShapes(event)

#draw grid ***************************************************************************************
        create_grid()

#draw shape ***************************************************************************************
        if tetris.figure:
            for i in range(4):
                for j in range(4):
                    for a in tetris.figure:
                        if i*4 +j in a.image():
                            x=block_size *(a.x+j)
                            y=block_size *(a.y+i)
                            img=Assets[a.color]
                            game_sc.blit(img,(x,y))
                            #pygame.draw.rect(game_sc,yellow,(x,y,block_size,block_size))
           
# GAMEOVER ***************************************************************************************
        if tetris.gameover:
            control.game_over()

#draw screen*************************************************************************************
        sc.blit(imp, (0, 0))
        sc.blit(game_sc, (20, 80)) #ne kadar boşluk bırakacagı ustten ve soldan
        game_sc.blit(game_imp, (0, 0)) #görüntü yüzeyi nesnesini görüntüleme yüzeyi nesnesine kopyalama

#draw titles****************************************************************************************
    
        sc.blit(title_tetris, (325, 20))
        sc.blit(title_score, (500, 300))
        sc.blit(font.render(str(tetris.score), True, pygame.Color('white')), (550, 840))
        sc.blit(title_level, (500, 120)) #solda 600 ustten 220
        #sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))
        sc.blit(title_next_shape, (500, 500))
        sc.blit(title_record, (500, 100))
        #sc.blit(font.render(str(tetris.record), True, pygame.Color('gold')), (550, 710))

        #level ve score bilgilerinin ekrana yazılması
        scoreimg = font2.render(f'{tetris.score}', True, white)
        levelimg = font2.render(f'{tetris.level}', True, white)
        sc.blit(levelimg,(650,120))
        sc.blit(scoreimg,(650,300))
	    
#draw next shape ************************************************************************************
        if tetris.next:
            for i in range(4):
                for j in range(4):
                    if i*4 +j in tetris.next.image():
                        x=block_size *(tetris.next.x+j+23)
                        y= s_height -250 + block_size *(tetris.next.y+i)
                        img=Assets[tetris.next.color]
                        sc.blit(img, (x, y))
                        
        pygame.display.flip() #paint screen one time.pygame.display.update() farkı nedir?
        clock.tick(FPS)
    pygame.quit() #Pygame kitaplığını devre dışı bırakır

#TEST
main()