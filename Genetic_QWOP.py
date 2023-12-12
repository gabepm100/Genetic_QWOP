import pyautogui
import time
import os
from selenium import webdriver
from PIL import Image
import pytesseract
import _thread as thread
import random
import keyboard

class Game:
    def __init__(self):
        self.gameover=False
        self.evolution=13
        self.score=0.0
        self.populationSize=10
        self.population=[]
        self.best_1=Player()
        self.best_2=Player()
        self.mutatescore=10
        self.start_time=0
        self.read=True
        self.write=False
        self.restart=False
    
    def run(self,driver):
        if self.read:
            self.getpopulation()
        else:
            self.generatePopulation()
        driver.startGame()
        best1=(Player(),0,0)
        best2=(Player(),0,0)
        while True:
            for player in self.population:
                is_done = self.isDone(driver)
                thread.start_new_thread(player.Algorithm, (driver,))                 
                self.start_time = time.time()
                while not is_done:
                    dist=self.getDistance(driver)
                    if is_float(dist):
                        dist=float(dist)
                        if player.score+10>=dist:
                            player.score=dist
                    is_done = self.isDone(driver)
                    if keyboard.is_pressed('r'):
                        driver.quit()
                        return False

                delta = time.time() - self.start_time            
                if best1[0].score<player.score:
                    best1 = (player, player.score, delta)
                elif best2[0].score<player.score:
                    best2 = (player, player.score, delta)
                elif best1[1] >= 100 and player.score >= 100:
                    if best1[2] > delta and delta >= 60:
                        best2 = best1
                        best1 = (player, player.score, delta)
                elif best2[1] >= 100 and player.score >= 100:
                    if best2[2] > delta and delta  >= 60:
                        best2 = (player, player.score, delta)
                elif player.score > 0 and best1[1] < player.score:
                    best2 = best1
                    newmom=Player()
                    best1 = (newmom, newmom.score, delta)                    
                elif player.score > 0 and best2[1] < player.score:
                    newdad=Player()
                    best2 = (newdad, newdad.score, delta)
                player.alive = False                
                driver.restart_game()
                player.alive = True
            self.reproduce(best1[0], best2[0])
            if self.write:
                self.writepopulation()

    def evolve(self):
        for player in self.population:
            for j in range(self.evolution):
                k=random.randrange(player.dnalength-1)
                player.dna[k]=(random.choice(player.optionalInputs),player.generateTime())



    def writePopulation(self):
        s=[]
        for i in range(self.populationSize):
            print(i)
            strr = "("+self.population[i].dna[0][0]+","+str(self.population[i].dna[0][1])+")"
            for item in self.population[i].dna[1:]:
                strr = strr + ","+ "("+item[0]+","+str(item[1])+")"
            strr="["+strr+"]"
            s.append(strr)
        print(s)
        file = open('train.txt','w')
        for item in s:
            print(item)
            file.write(item+"\n")
        file.close()
        print("Written To File")
        
    def getpopulation(self):
        self.population=[]
        # Using readlines()
        file1 = open('train.txt', 'r')
        Lines = file1.readlines()
        for line in Lines:
            line=line[:-1]
            l=0
            dn=[]
            while l<len(line)-1:
                move=""
                tim=""
                while line[l]!=")":
                    if len(line)-1<l:
                        break
                    if line[l].isalpha():
                        move=move+line[l]
                    elif line[l].isdigit() or line[l]==".":
                        tim=tim+line[l]
                    l+=1
                l+=1
                dn.append((move,float(tim.strip())))
            play=Player()
            play.dna=dn
            self.population.append(play)

    def generatePopulation(self):
        self.population = []
        for i in range(self.populationSize):
            player=Player()
            player.createSetup(self)
            self.population.append(player)

    def getDistance(self, driver):
        driver.driver.save_screenshot('my_screenshot.png')
        file_path = "\path\to\filemy_screenshot.png"
        im = Image.open(file_path)
        left = 230
        top = 40
        right = 310
        bottom = 78
        im1 = im.crop((left, top, right, bottom))
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(im1)
        if os.path.exists(file_path):
            os.remove(file_path)
        return text

    
    def isDone(self,driver):
        driver.driver.save_screenshot('endScreenshot.png')
        filePath="\path\to\file\endScreenshot.png"
        image=Image.open(filePath)
        left = 220
        top = 122
        right = 440
        bottom = 165
        im1 = image.crop((left, top, right, bottom))
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(im1).lower()
        text=text.strip()
        if os.path.exists(filePath):
           os.remove(filePath)
        if text == "participant":
            return True
        return False
    
    def reproduce(self, setup1, setup2):
        already={}
        population=[]
        for i in range(self.populationSize):
            player=Player()
            position = random.randint(0, len(setup1.dna))
            if not already.get(position) or position>=2:
                already[position] = True
                if random.randint(0, 100) > 50:
                    player.dna = setup1.dna[0:position] + setup2.dna[position:]        
                    if random.randint(0, 100) <= self.mutatescore:
                        index = random.randint(0, len(player.dna) - 1)
                        player.dna[index] = setup1.createSetup(self)[0]
                    population.append(player)
                else:
                    player.dna = setup2.dna[0:position] + setup1.dna[position:]
                    if random.randint(0, 100) < self.mutatescore:
                        index = random.randint(0, len(player.dna) - 1)
                        player.dna[index] = setup2.createSetup(self)[0]
                    population.append(player)
            else:
                player.createSetup(self)
                population.append(player)     
        self.population = population
        self.evolve()


class Player:
    def __init__(self):
        self.bestscore=0
        self.optionalInputs=["","q","w","","o","p","qw","qo","qp","wo","wp","op","qwo","qwp","qop","wop","qwop"]
        self.dnalength=300
        self.alive = True
        self.dna=[]
        self.score=0.0
        
    def createSetup(self,Game):
        moves=[]
        Game.startTime = time.time()
        for i in range(self.dnalength):
            moves.append((random.choice(self.optionalInputs),self.generateTime()))
        self.dna=moves
        return moves 

    def generateTime(self):
        return round(((random.randint(100, 3000) / 1000)+1),2)
    
    def Algorithm(self,driver):
        for action in self.dna:
            if not self.alive:
                print("you dead")
                break
            driver.pressKeys(action)


class Driver:
    def __init__(self):      
        self.driver=None
    def create_Driver(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--window-size=700,600")
        option.add_argument('--ignore-certificate-errors-spki-list')
        driver = webdriver.Chrome(options=option)
        driver.get('https://www.foddy.net/Athletics.html')
        self.driver=driver
        return driver

    
    def pressKeys(self, action):
        for key in action[0]:
            pyautogui.keyDown(key)
        time.sleep(action[1])
        for key in action[0]:
            pyautogui.keyUp(key)
    
    def startGame(self):
        time.sleep(2)
        pyautogui.scroll(-100)
        pyautogui.click(x=200,y=200)

    def restart_game(self):
        self.score = 0.0
        pyautogui.press(" ")


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def main():
    newDriver=Driver()
    newDriver.create_Driver()
    newGame=Game()
    newGame.run(newDriver)
        
    

if __name__ == '__main__':
    main()

