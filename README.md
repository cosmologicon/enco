enco
====

python entity/component tool

Entity Component System (ECS) is a software pattern (found especially in games) that represents entities as collections of components. This tool is a limited version of an ECS, designed to be easy to use, appropriate for small to medium games. This tool is recommended for beginners to ECS, and people writing quick or small games (e.g. game jams).

Differences from a typical ECS
------------------------------

ECS typically involves an extra layer of indirection compared with regular python objects. Entities created with this tool behave like regular objects, without this layer of indirection. The fact that they're implemented as collections of components is "behind the scenes".

ECS typically involves a "system" or "world" object that acts a collection of all entities in existence. This tool does not work that way. Entities can be accessed either individually or as part of any collection you add them to, just like regular python objects.

ECS typically separates the definition of data (which lives in components) from the behavior of that data (which lives in the system). This tool puts both the definition of the data and its behavior into the components.

ECS typically encapsulates the data between components. This tool allows components free access to other components' data. This is a powerful feature, and it comes at the expense of some safety. Thus this tool is not recommended for very large games.

To install
----------

Download `enco.py` and put it in your source directory.

To install from command line
----------------------------

    curl https://raw.githubusercontent.com/cosmologicon/enco/master/enco.py > my-source-directory/enco.py
