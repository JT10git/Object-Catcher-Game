from tkinter import *
from random import *
import tkinter.messagebox



class ScoreBoard():
    
    def __init__(self,parent):
        self.parent = parent       
        self.initGUI()        
        self.reset()
        
    def initGUI(self):
        # Lives
        self.livesVar = IntVar()
        Label(self.parent, text="Lives:", font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=35, pady=100, sticky=N+W)        
        Label(self.parent, textvariable=self.livesVar, font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=60, pady=150, sticky=N+W)        
        
        # Score
        self.scoreVar = IntVar()
        Label(self.parent, text="Score:", font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=35, pady=250, sticky=N+W)
        Label(self.parent, textvariable=self.scoreVar, font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=50, pady=300, sticky=N+W)        
        
        # High score
        self.highScoreVar = IntVar()
        Label(self.parent, text="Highest Score:", font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=0, pady=400, sticky=N+W)
        Label(self.parent, textvariable=self.highScoreVar, font=("Helvetica", 16, "bold")).grid(row=1, column=2, padx=50, pady=450, sticky=N+W)

    def reset(self):
        self.lives = 5
        self.score = 0
        self.highScore = self.loadScore()
        
        self.livesVar.set(self.lives)
        self.scoreVar.set(self.score)
        self.highScoreVar.set(self.highScore)

    def loadScore(self):
        with open("high-score.txt", "r") as data:
            return int(data.read())                
        
    def saveScore(self):
        if self.score >= self.highScore:
            with open("high-score.txt", "w") as data:
                data.write(str(self.score))
        
    def gameOver(self):
        self.saveScore()      
        if tkinter.messagebox.askyesno("Object Catcher Game", "Try again?"):
            self.reset()
        else:
            exit()
            
    def updateBoard(self, livesStatus, scoreStatus):
        self.lives += livesStatus; self.score += scoreStatus
        if self.lives < 0: self.gameOver()        
        self.livesVar.set(self.lives); self.scoreVar.set(self.score)
        if self.highScore < self.score: self.highScoreVar.set(self.score)



class ItemsFallingFromSky():
    
    def __init__(self,parent,canvas,player,board, playerSelected):
        self.parent = parent                    # root form
        self.canvas = canvas                    # canvas to display
        self.player = player                    # to check touching
        self.board = board                      # score board statistics
        
        self.fallSpeed = 50                     # falling speed        
        self.xPosition = randint(50, 750)       # random position
        self.isgood = randint(0, 100)           # random goodness
        
        if playerSelected == 0:
            self.goodItems = ["momo.png"]
            self.badItems = ["chicken.png","taco.png"]
            self.lifeItems = ["life.png"]
        elif playerSelected == 1:
            self.goodItems = ["chicken.png"]
            self.badItems = ["momo.png", "taco.png"]
            self.lifeItems = ["life.png"]
        else:
            self.goodItems = ["taco.png"]
            self.badItems = ["momo.png","chicken.png"]
            self.lifeItems = ["life.png"]

        # create falling items
        if (self.isgood > 50):   
            self.itemPhoto = tkinter.PhotoImage(file = "images/{}" .format( choice(self.goodItems) ) )
            self.fallItem = self.canvas.create_image( (self.xPosition, 50) , image=self.itemPhoto , tag="good" )
        elif (self.isgood > 1):
            self.itemPhoto = tkinter.PhotoImage(file = "images/{}" . format( choice(self.badItems) ) )
            self.fallItem = self.canvas.create_image( (self.xPosition, 50) , image=self.itemPhoto , tag="bad" )
        else:
            self.itemPhoto = tkinter.PhotoImage(file = "images/{}" . format( choice(self.lifeItems) ) )
            self.fallItem = self.canvas.create_image( (self.xPosition, 50) , image=self.itemPhoto , tag="life" )
            
        # trigger falling item movement
        self.move_object()
        
        
    def move_object(self):
        # dont move x, move y
        self.canvas.move(self.fallItem, 0, 15)
        
        if (self.check_touching()) or (self.canvas.coords(self.fallItem)[1] > 650):     # [ x0, y0, x1, y1 ]
            self.canvas.delete(self.fallItem)                                           # delete if out of canvas
        else:
            self.parent.after(self.fallSpeed, self.move_object)                         # after some time move object
            
        
    def check_touching(self):
        # find current coordinates
        x0, y0 = self.canvas.coords(self.fallItem)
        x1, y1 = x0 + 50, y0 + 50
        
        # get overlapps
        overlaps = self.canvas.find_overlapping(x0, y0, x1, y1)
        
        if (self.canvas.gettags(self.fallItem)[0] == "good") and (len(overlaps) > 1) and (self.board.lives >= 0):   # gettags : ("good",)
            self.board.updateBoard(0, 100)                                              # (lives, score)
            return True                                                                 # touching yes
        
        elif (self.canvas.gettags(self.fallItem)[0] == "life") and (len(overlaps) > 1) and (self.board.lives >= 0):   # gettags : ("good",)
            self.board.updateBoard(1, 0)                                              # (lives, score)
            return True                                                                 # touching yes
            
        elif (self.canvas.gettags(self.fallItem)[0] == "bad") and (len(overlaps) > 1) and (self.board.lives >= 0):  # gettags : ("bad",)
            self.board.updateBoard(-1, 0)                                               # (lives, score)
            return True                                                                 # touching yes
            
        return False                                                                    # touching not
    


class TheGame(ItemsFallingFromSky,ScoreBoard):
    
    def __init__(self,parent):
        self.parent = parent
        
        # windows form
        self.parent.geometry("1024x650")
        self.parent.title("Object Catcher")

        # canvas window
        self.canvas = Canvas(self.parent, width=800, height=600)
        self.canvas.config(background="#98D0E3")
        self.canvas.bind("<Key>", self.keyMoving)       # take keyboard input as movement
        self.canvas.focus_set()
        self.canvas.grid(row=1, column=1, padx=25, pady=25, sticky=W+N)

        # play selector (random/temporary)
        self.playerSelector = randint(0, 2)

        # player character
        self.playerPhoto = tkinter.PhotoImage(file = "images/{}" .format( "Bhakta_L.png" ) )
        self.playerChar = self.canvas.create_image( (475, 560) , image=self.playerPhoto , tag="player" )

        if self.playerSelector == 1:
            self.playerPhoto = tkinter.PhotoImage(file = "images/{}" .format( "jew.gif" ) )
            self.playerChar = self.canvas.create_image( (475, 560) , image=self.playerPhoto , tag="player" )
        elif self.playerSelector == 2:
            self.playerPhoto = tkinter.PhotoImage(file = "images/{}" .format( "Hritesh_L.png" ) )
            self.playerChar = self.canvas.create_image( (475, 560) , image=self.playerPhoto , tag="player" )


        # define score board
        self.personalboard = ScoreBoard(self.parent)

        # start poping falling items
        self.createEnemies()
        
        
    def keyMoving(self, event):        
        if ((event.char == "a") or (event.char == "A")) and (self.canvas.coords(self.playerChar)[0] > 50):
            self.canvas.move(self.playerChar, -50, 0)            
        if ((event.char == "d") or (event.char == "D")) and (self.canvas.coords(self.playerChar)[0] < 750):
            self.canvas.move(self.playerChar, 50, 0)


    def createEnemies(self):
        ItemsFallingFromSky(self.parent, self.canvas, self.playerChar, self.personalboard, self.playerSelector)
        self.parent.after(1100, self.createEnemies)
        

        
if __name__ == "__main__":
    root = Tk()
    TheGame(root)
    root.mainloop()