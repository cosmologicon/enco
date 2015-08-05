enco: a python entity/component tool
====================================

Entity Component System (ECS) is a software pattern (found especially in games) that represents entities as collections of components. This tool is an easy-to-use, limited version of an ECS, appropriate for small to medium games. This tool is recommended for beginners to ECS, and people writing quick or small games (e.g. game jams).

Quick example
-------------

To use the API, create a subclass of enco.Component. This will be a component class. Use one or more component classes to create an entity class (which doesn't need to be a subclass of anything). Do this by using @ to decorate the entity class with instances of the component classes.

The entity class receives all the methods defined on any of its component classes. When an entity's method is called, the corresponding method of every component that defines that method will be called.

    import enco

    class PlaysSoundEffects(enco.Component):  # PlaysSoundEffects is a component class
        def jump(self):
            print("Playing jump sound")
        def takedamage(self, damage):
            print("Playng hurt sound")

    class HasHealthPoints(enco.Component):  # HasHealthPoints is a second component class
        def __init__(self, maxhp):
            self.hp = self.maxhp = maxhp
        def heal(self):
            self.hp = self.maxhp
        def takedamage(self, damage):
            self.hp -= damage

    @PlaysSoundEffects()  # Decorate the entity class with instances of the component classes
    @HasHealthPoints(10)
    class Player(object):  # Player is now an entity class
        pass

    # Player now has all the methods that are defined in at least one of its component claseses:
    #   in this case: jump, takedamage, and heal
    player = Player()  # Instantiate the entity class to create an entity, player
    # Calling player.takedamage calls both PlaysSoundEffects.takedamage and
    #   HasHealthPoints.takedamage on player
    player.takedamage(4)  # prints "Playing hurt sound"
    print(player.hp)  # prints 6

For most simple cases, this should just work. For details and edge cases, 


Differences from a typical ECS
------------------------------

(If you've never used another ECS, you don't need to worry about this part.) Compared with a typical ECS implementation, enco:

* removes the extra layer of indirection for accessing an entity's methods and data. Instead you access an entity's data and methods directly, just like with any other python object.
* lacks a "system" or "world" object that acts as a collection of all entities in existence. Instead you use entities individually, or part of any collections you create yourself, just like any other python object.
* keeps together the definition of data and the behavior of that data. These are typically separated, with data in the components, and behavior in the system. But enco places both of them in the component.
* does not allow for dynamically adding or removing components at run time.
* allows easy access to data across components, rather than encapsulating each component's data.
* is not optimized for speed.

Because of these design choices, valuing ease of use and conceptual simplicity over speed and safety checks, enco is recommended for small to medium games, rather than very large games.

To install
----------

Download [https://raw.githubusercontent.com/cosmologicon/enco/master/enco.py](`enco.py`) and put it in your source directory.

To install from command line
----------------------------

    curl https://raw.githubusercontent.com/cosmologicon/enco/master/enco.py > my-source-directory/enco.py
