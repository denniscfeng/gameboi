import discord
from PIL import Image

gameboi = discord.Client()

#############################################################################
############################################################################# Dennis Feng
#############################################################################

class GameboiException(Exception):
    pass

class Lobby:
    idsInLobby = {}
    def __init__(self, people):
        self.people = people
        self.initMessage = []
    def close(self):
        for person in self.people:
            Lobby.idsInLobby.pop(person.id)

class WaitingLobby(Lobby):
    def __init__(self, game, people):
        super().__init__(people)
        self.game = game
        for person in people:
            Lobby.idsInLobby[person.id] = self
        self.checklist = set(people[1:])
        peoplestr = ""
        for person in people[1:]:
            peoplestr += person.mention + " "
        self.initMessage.append("" + people[0].mention + " has challenged " + peoplestr + "to a game of " + game.name + "!\n You must all type 'yes' to begin the game. Anyone may type 'no' to decline or cancel.")
    def eval(self, message):
        content = message.content.lower()
        if content == 'no':
            self.close()
            return ["Someone has declined the challenge. Cancelling game."]
        elif content == 'yes' and message.author in self.checklist:
            self.checklist.remove(message.author)
            if len(self.checklist) == 0:
                ## TODO start the game already proabably have to return the game's own initMessage
                return []
            else:
                return [message.author.name + " has confirmed. " + str(len(self.checklist)) + " more people needed."]

class GameLobby(Lobby):
    gamesList = {}
    name = ""
    numPlayers = 0

class countToThree(GameLobby):
    name = "countToThree"
    numPlayers = 3
    def __init__(self, people):
        super().__init__(people)
        self.count = 0
    def eval(self, message):
        if message.content.lower == ("yee"):
            self.count += 1
        if self.count >= 3:
            self.close()
            return ["Yay yall counted to three!"]
        return ["Current count at: " + str(self.count)]

GameLobby.gamesList[countToThree.name] = countToThree

@gameboi.event
async def on_ready():
    print('Gameboi successfully booted!')
    print('Account: "'+gameboi.user.name+'", ID: '+gameboi.user.id)

@gameboi.event
async def on_message(message):
    if message.author.id in Lobby.idsInLobby:
        await sendOutputs(message.channel, Lobby.idsInLobby[message.author.id].eval(message))
    elif message.content.startswith(gameboi.user.mention):
        msgIter = iter(message.content.split())
        next(msgIter)
        try:
            command = next(msgIter).lower()
            if command == 'help':
                await gameboi.send_message(message.channel, "Mention me with these commands: \n"
                                                            "- '"+gameboi.user.mention+" help' : see commands \n"
                                                            "- '"+gameboi.user.mention+" games' : see list of game names \n"
                                                            "- '"+gameboi.user.mention+" play <game name> with <username or mention> <username or mention> ...' : invite people to play a game\n")
            elif command == 'games':
                gamesstr = "Games you can play: "
                for game in GameLobby.gamesList:
                    gamesstr = gamesstr + "\n-" + game
                await gameboi.send_message(message.channel, gamesstr)
            elif command == 'play':
                gameName = next(msgIter)
                if not (gameName in GameLobby.gamesList):
                    raise GameboiException("Game name not found. Type '" + gameboi.user.mention + " games' : see list of game names.")
                else:
                    game = GameLobby.gamesList[gameName]
                    people = [message.author]
                    for name in msgIter:
                        if name.lower() == 'with':  # TODO using "with" to parse game names with spaces
                            continue
                        person = findUser(name, message.channel)
                        if person in people:
                            raise GameboiException("Duplicate players found.")
                        people.append(person)
                    if len(people) != game.numPlayers:
                        raise GameboiException("Wrong number of players for " + gameName + ". Need " + str(game.numPlayers) + " more players to confirm.")
                    else:
                        newLobby = WaitingLobby(game, people)
                        await sendOutputs(message.channel, newLobby.initMessage)
            else:
                raise GameboiException ("Command not found. \nType '"+gameboi.user.mention+" help' to see usage of commands.")
        except GameboiException as ge:
            await gameboi.send_message(message.channel, "Error: " + str(ge))
        except StopIteration:
            await gameboi.send_message(message.channel, "Type '"+gameboi.user.mention+" help' to see usage of commands.")

def findUser(theName, theChannel):
    for theUser in theChannel.server.members:
        if theUser.nick==theName or theUser.name==theName or theUser.mention==theName:
            if theUser.status != discord.Status.online:
                raise GameboiException("User not online or active: " + theName)
            else:
                return theUser
            break
    else:
        raise GameboiException("User not found: " + theName)

async def sendOutputs(thechannel, thelist):
    # A way to send the list of outputs spit out by a game object, and can upload .png's
    if thelist:
        for item in thelist:
            if ".png" in item:
                await gameboi.send_file(thechannel, fp=item)
            else:
                await gameboi.send_message(thechannel, item)

# gameboi.run("MjYyODE4Mzg4MDk3NzYxMjgw.DBY6Rw.ugTBLNQMhX7ImQ0sgrS4CPAI-Mg") #runs on account "gameboi"
gameboi.run("MjUzMzA3ODIwNjk3NDUyNTQ1.DBY7VQ.ABcabZxrv0JDU722RO2YuWn07L0")  # runs on account "testboi"
