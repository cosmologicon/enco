import enco

# The tests below demonstrate some of the edge cases and potentially surprising behavior of
# enco.Component.


# ENTITIES RECEIVE METHODS THAT ARE DEFINED IN THEIR COMPONENTS

class Component1(enco.Component):
	def f(self):
		print("Component1.f called")

@Component1()
class Entity1(object):
	pass

entity = Entity1()
entity.f()  # prints "Component1.f called"


# METHODS THAT ARE DEFINED IN MULTIPLE COMPONENTS WILL ALL BE CALLED

class Component2(enco.Component):
	def f(self):
		print("Component2.f called")

@Component1()
@Component2()
class Entity2(object):
	pass

entity = Entity2()
entity.f()  # prints "Component1.f called", followed by "Component2.f called"


# METHODS ARE INVOKED IN THE ORDER THE COMPONENTS APPEAR WHEN DEFINING THE ENTITY CLASS

@Component2()
@Component1()
class Entity3(object):
	pass

entity = Entity3()
entity.f()  # prints "Component2.f called", followed by "Component1.f called"


# IF THE METHOD IS DEFINED ON THE ENTITY, THE ENTITY VERSION IS CALLED LAST

@Component1()
class Entity4(object):
	def f(self):
		print("Entity4.f called")

entity = Entity4()
entity.f()  # prints "Component1.f called", followed by "Entity4.f called"


# THE RETURN VALUE IS THE VALUE RETURNED BY THE LAST METHOD INVOKED
# RETURN VALUES FROM ANY METHOD INVOKED BEFORE THE LAST ONE ARE IGNORED

class Component3(enco.Component):
	def g(self):
		return "Component3.g"

@Component3()
class Entity5(object):
	def g(self):
		return "Entity5.g"

entity = Entity5()
print(entity.g())  # prints "Entity5.g"


# METHODS THAT ARE DEFINED IN NO COMPONENTS ARE NOT DEFINED ON THE ENTITY

try:
	entity.h()
except AttributeError:
	print("entity.h not defined")


# WITHIN COMPONENT METHODS, self REFERS TO THE ENTITY, NOT THE COMPONENT

class Component4(enco.Component):
	def h(self):
		return self.x  # Component4 lacks an "x" member, but that's okay

@Component4()
class Entity6(object):
	def __init__(self):
		self.x = 100

entity = Entity6()
print(entity.h())  # prints 100


# NON-CALLABLE COMPONENT MEMBERS ARE COPIED TO THE ENTITY, BUT THEY ARE NOT CHAINED
# TOGETHER LIKE METHODS ARE. THE ENTITY MEMBER HAS THE SAME VALUE AS THE LAST
# COMPONENT THAT DEFINES THAT MEMBER.

class Component5(enco.Component):
	x = 200

class Component6(enco.Component):
	x = 300

@Component5()
@Component6()
class Entity6(object):
	pass

entity = Entity6()
print(entity.x)  # prints 300


# IF THE ENTITY DEFINES THE MEMBER, ITS VALUE IS NOT OVERWRITTEN BY THE COMPONENTS

@Component5()
@Component6()
class Entity7(object):
	x = 400

entity = Entity7()
print(entity.x)  # prints 400


# THESE ARE SHALLOW COPIES. BE AWARE WHEN DEFINING MUTABLE CLASS MEMBERS.

class Component7(enco.Component):
	a = []

@Component7()
class Entity7(object):
	pass

@Component7()
class Entity8(object):
	pass

assert(Entity7.a is Entity8.a)
Entity7.a.append(500)
print(Entity8.a)  # prints [500]


# THIS CAN BE AVOIDED BY DEFINING CLASS MEMBERS IN THE COMPONENT'S __init__ METHOD.
# MORE ON __init__ BELOW.

class Component7(enco.Component):
	def __init__(self):
		self.a = []

@Component7()
class Entity7(object):
	pass

@Component7()
class Entity8(object):
	pass

assert(Entity7.a is not Entity8.a)
Entity7.a.append(600)
print(Entity8.a)  # prints []


# COMPONENT METHODS AND MEMBERS THAT BEGIN WITH DOUBLE UNDERSCORE (__) ARE NOT
# ATTACHED TO THE ENTITY. THIS INCLUDES STANDARD METHODS LIKE __init__, __str__,
# and __nonzero__.

class Component8(enco.Component):
	def __fff(self):
		pass

@Component8()
class Entity9(object):
	pass

entity = Entity9()
try:
	entity.__fff()
except AttributeError:
	print("entity.__fff not defined")

# (As a note, these methods may end up in the entity in a mangled form, such as, in
# this case, entity._Component8__fff, so they may show up in dir(entity). However, you
# should be able to ignore them in general.)


# COMPONENT __init__ METHODS ARE INVOKED WHEN THE COMPONENT IS APPLIED TO THE
# ENTITY, *NOT* WHEN THE ENTITY IS INSTANTIATED. ENTITY __init__ METHODS ARE INVOKED
# WHEN THE ENTITY IS INSTANTIATED, LIKE NORMAL.

class Component9(enco.Component):
	def __init__(self):
		print("Component9.__init__ called")

@Component9()  # prints "Component9.__init__ called"
class Entity10(object):
	def __init__(self):
		print("Entity10.__init__ called")

print("About to instantiate Entity10....")
entity = Entity10()  # prints "Entity10.__init__ called"


# ANY MEMBERS DEFINED IN COMPONENT __init__ METHODS WILL WIND UP AS CLASS-LEVEL VARIABLES
# IN ENTITIES. THEREFORE THEY WILL BE SHARED BY ALL INSTANCES.

class Component10(enco.Component):
	def __init__(self):
		self.b = []

@Component10()
class Entity11(object):
	pass

entity_1 = Entity11()
entity_2 = Entity11()

entity_1.b.append(700)
print(entity_2.b)  # prints [700]


# IF THIS IS A PROBLEM, THE BEST WAY TO AVOID IT IS TO USE YOUR OWN COMPONENT INITIALIZER METHOD
# THAT DOES NOT START WITH A DOUBLE UNDERSCORE. MAKE IT THE SAME IN ALL YOUR COMPONENTS, AND THEN
# YOU ONLY NEED TO ADD ONE LINE TO YOUR ENTITY'S __init__ METHOD.

class Component11(enco.Component):
	def initialize(self):
		self.b = []

@Component11()
class Entity12(object):
	def __init__(self):
		self.initialize()

entity_1 = Entity12()
entity_2 = Entity12()

entity_1.b.append(700)
print(entity_2.b)  # prints []


# ENTITY CLASSES CAN ALSO BE SUBCLASSES OF OTHER CLASSES, AND OTHER CLASSES CAN INHERIT FROM
# ENTITY CLASSES. FOR THE PURPOSE OF DETERMINING METHOD INVOCATION ORDER, THE DERIVED CLASS TREATS
# THE BASE CLASS'S METHOD (ALONG WITH ANY COMPONENTS OF THE BASE CLASS) AS A REGULAR METHOD.

class Component12(enco.Component):
	def f(self):
		print("Component12.f called")
	
class Component13(enco.Component):
	def f(self):
		print("Component13.f called")
	
@Component12()
class EntityBase(object):
	def f(self):
		print("EntityBase.f called")

@Component13()
class EntityDerived(EntityBase):
	pass

entity = EntityDerived()
entity.f()  # prints "Component13.f", then "Component12.f", then "EntityBase.f"


