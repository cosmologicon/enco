import enco

class PlaysSoundEffects(enco.Component):
    def jump(self):
        print("Playing jump sound")
    def takedamage(self, damage):
        print("Playng hurt sound")

class HasHealthPoints(enco.Component):
    def __init__(self, maxhp):
        self.hp = self.maxhp = maxhp
    def heal(self):
        self.hp = self.maxhp
    def takedamage(self, damage):
        self.hp -= damage

@PlaysSoundEffects()
@HasHealthPoints(10)
class Player(object):
    pass

player = Player()
player.takedamage(4)  # prints "Playing hurt sound"
print(player.hp)  # prints 6

