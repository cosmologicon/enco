# Asteroids example game, demonstrating several entity/component design choices.
# Requires Python 3.8+ and the pygame library. Arrow keys and space to control. Esc to quit.
# I suggest playing the game for a minute before looking at the code.

import pygame, math, random, enco
from pygame.locals import *

screensize = 500

# Polar to rectangular coordinate transform. theta = 0 is upward on screen (y is negative)
def vector(r, theta):
	return r * math.sin(theta), -r * math.cos(theta)

# POSITION AND MOVEMENT COMPONENTS

# Used by all entities
class PositionVelocity(enco.Component):
	"""Entity has a position and velocity."""
	def __init__(self):
		self.x, self.y = 0, 0
		self.vx, self.vy = 0, 0
	def think(self, dt):
		self.x += dt * self.vx
		self.y += dt * self.vy
	def screenpos(self):
		return int(self.x), int(self.y)

# Used by player
class HasMaxSpeed(enco.Component):
	"""Maximum speed is imposed on the entity."""
	def __init__(self, maxspeed):
		self.maxspeed = maxspeed
	def think(self, dt):
		v = math.hypot(self.vx, self.vy)
		if v > self.maxspeed:
			self.vx *= self.maxspeed / v
			self.vy *= self.maxspeed / v

# Used by the player, asteroids, and bullets
class WrapScreen(enco.Component):
	"""Entity comes on the opposite side of the screen when it goes off."""
	def think(self, dt):
		self.x %= screensize
		self.y %= screensize

# Used by ufos
class CrossesScreen(enco.Component):
	"""Entity spawns at a random point on the left or right edge, travels across the screen with a
	constant horizontal velocity, periodically changing vertical velocity, and disappearing after
	reaching the opposite edge. Wraps around when going off the top or bottom."""
	def __init__(self, v0, steerperiod):
		self.v0 = v0
		self.steerperiod = steerperiod
		self.steertime = 0
	def spawn(self):
		if random.random() < 0.5:
			self.x, self.vx = 0, self.v0  # Start at left and move right.
		else:
			self.x, self.vx = screensize, -self.v0  # Start at right and move left.
		self.y = random.uniform(0, screensize)
		self.vy = 0
	def think(self,  dt):
		if self.x < 0 and self.vx < 0 or self.x > screensize and self.vx > 0:
			self.alive = False
		self.y %= screensize
		self.steertime += dt
		if self.steertime > self.steerperiod:
			self.steertime = 0
			self.vy = random.uniform(-self.v0, self.v0)

# Used by player
class SpawnsAtCenter(enco.Component):
	"""Entity spawns at the center of the screen with 0 velocity."""
	def spawn(self):
		self.x, self.y = screensize / 2, screensize / 2
		self.vx, self.vy = 0, 0

# Used by asteroids
class SpawnsAtEdge(enco.Component):
	"""Entity spawns at a random point along the edge of the screen, moving in a random direction
	with the given speed."""
	def __init__(self, v0):
		self.v0 = v0
	def spawn(self):
		if random.random() < 0.5:
			self.x, self.y = 0, random.uniform(0, screensize)  # Spawn on left/right edge.
		else:
			self.x, self.y = random.uniform(0, screensize), 0  # Spawn on top/bottom edge.
		self.vx, self.vy = vector(self.v0, random.uniform(0, math.tau))
	
# Used by player
class RotatesWithArrows(enco.Component):
	"""Entity rotates to the right or left when an arrow key is pressed, with the given rotation
	rate."""
	def __init__(self, turnspeed):
		self.turnspeed = turnspeed
		self.angle = 0
		self.turning = 0
	def control(self, keys):
		self.turning = (1 if keys[K_RIGHT] else 0) - (1 if keys[K_LEFT] else 0)
	def think(self, dt):
		self.angle += self.turning * self.turnspeed * dt

# Used by player
class ThrustsWithUp(enco.Component):
	"""Entity accelerates forward when the up key is pressed, with the given acceleration."""
	def __init__(self, acceleration):
		self.acceleration = acceleration
		self.thrusting = False
	def control(self, keys):
		self.thrusting = keys[K_UP]
	def think(self, dt):
		if self.thrusting:
			dvx, dvy = vector(self.acceleration * dt, self.angle)
			self.vx += dvx
			self.vy += dvy

# WEAPON AND COLLISION COMPONENTS

# Used by ufos and player
class WeaponCooldown(enco.Component):
	"""Entity can fire weapon after the specified cooldown time."""
	def __init__(self, cooldowntime):
		self.cooldowntime = cooldowntime
		self.cooldownremaining = 0
	def fire(self):
		self.cooldownremaining = self.cooldowntime
	def trytofire(self):
		if self.cooldownremaining == 0:
			self.fire()
	def think(self, dt):
		self.cooldownremaining = max(self.cooldownremaining - dt, 0)

# Used by ufos and player
class FiresBullets(enco.Component):
	"""Entity has the capability of firing bullets."""
	def __init__(self, bulletspeed):
		self.bulletspeed = bulletspeed
	def fireindirection(self, angle):
		dx, dy = vector(self.size * 1.3, angle)
		pos = self.x + dx, self.y + dy
		vel = vector(self.bulletspeed, angle)
		state.objects.append(Bullet(pos, vel))

# Used by ufos
class FiresRandomDirectionsConstantly(enco.Component):
	"""Entity fires in a random direction whenever it's allowed to do so."""
	def fire(self):
		self.fireindirection(random.uniform(0, math.tau))
	def think(self, dt):
		self.trytofire()

# Used by player
class FiresForwardWithSpace(enco.Component):
	"""Entity fires in the direction it's facing when space bar is pressed."""
	def fire(self):
		self.fireindirection(self.angle)
	def control(self, keys):
		if keys[K_SPACE]:
			self.trytofire()

# Used by asteroids
class SplitsOnCollision(enco.Component):
	"""Entity creates two smaller asteroids (one level smaller) at its position when it collides.
	The smaller asteroids have additional velocity of the given magnitude, added to the original
	asteroid's velocity."""
	def __init__(self, dvsplit):
		self.dvsplit = dvsplit
	def collide(self):
		if self.level <= 1:  # Level 1 asteroids don't split.
			return
		dvx, dvy = vector(self.dvsplit, random.uniform(0, math.tau))
		state.objects.extend([
			Asteroid(self.level - 1, (self.x, self.y), (self.vx + dvx, self.vy + dvy)),
			Asteroid(self.level - 1, (self.x, self.y), (self.vx - dvx, self.vy - dvy)),
		])

# Used by ships and asteroids
class ExplodesOnCollision(enco.Component):
	"""Entity leaves behind an explosion when it collides."""
	def collide(self):
		state.effects.append(Explosion((self.x, self.y)))

# OTHER LOGICAL COMPONENTS

# Used by bullets and explosions
class Lifetime(enco.Component):
	"""Entity automatically disappears after a set period of time."""
	def __init__(self, lifetime):
		self.lifetime = lifetime
		self.timelived = 0
	def think(self, dt):
		self.timelived += dt
		if self.timelived > self.lifetime:
			self.alive = False

# Used by explosions
class Grows(enco.Component):
	"""Entity steadily increases in size at the given rate."""
	def __init__(self, growthrate):
		self.growthrate = growthrate
		self.size = 0
	def think(self, dt):
		self.size += self.growthrate * dt

# GRAPHICS COMPONENTS

# Used by bullets, asteroids, and explosions
class Circular(enco.Component):
	"""Entity is drawn as a circle."""
	def draw(self, surf):
		if self.size < 1:
			return
		pygame.draw.circle(surf, self.color, self.screenpos(), int(self.size), 1)
		
# Used by ufos
class Rectangular(enco.Component):
	"""Entity is drawn as a rectangle."""
	def draw(self, surf):
		rect = pygame.Rect((0, 0, int(3 * self.size), int(2 * self.size)))
		rect.center = self.screenpos()
		pygame.draw.rect(surf, self.color, rect, 1)

# Used by player
class Triangular(enco.Component):
	"""Entity is a triangle, oriented in the direction it's facing."""
	def makeimg(self):
		s = int(self.size)
		self.img = pygame.Surface((4 * s, 4 * s)).convert_alpha()
		points = (s, 3 * s), (2 * s, 0), (3 * s, 3 * s)
		pygame.draw.lines(self.img, self.color, True, points)
	def draw(self, surf):
		rotimg = pygame.transform.rotate(self.img, -math.degrees(self.angle))
		surf.blit(rotimg, rotimg.get_rect(center = self.screenpos()))

# ENTITIES

@PositionVelocity()
class Entity:
	alive = True
	def collide(self):
		self.alive = False

@WrapScreen()
@SpawnsAtEdge(v0 = 50)
@ExplodesOnCollision()
@SplitsOnCollision(dvsplit = 40)
@Circular()
class Asteroid(Entity):
	color = 144, 144, 144
	def __init__(self, level, pos = None, vel = None):
		self.level = level
		self.size = 10 + 10 * level
		if pos is None:  # Created at random position at stage startup.
			self.spawn()
		else:  # Created by larger asteroid splitting into two.
			self.x, self.y = pos
			self.vx, self.vy = vel

@WrapScreen()
@HasMaxSpeed(100)
@SpawnsAtCenter()
@RotatesWithArrows(turnspeed = 2.5)
@ThrustsWithUp(acceleration = 100)
@WeaponCooldown(0.5)
@FiresBullets(bulletspeed = 200)
@FiresForwardWithSpace()
@ExplodesOnCollision()
@Triangular()
class Player(Entity):
	color = 255, 255, 255
	size = 10
	def __init__(self):
		self.spawn()
		self.makeimg()

@CrossesScreen(v0 = 30, steerperiod = 3)
@WeaponCooldown(0.5)
@FiresBullets(bulletspeed = 200)
@FiresRandomDirectionsConstantly()
@ExplodesOnCollision()
@Rectangular()
class Ufo(Entity):
	color = 127, 255, 127
	size = 15
	def __init__(self):
		self.spawn()

@WrapScreen()
@Circular()
@Lifetime(1.5)
class Bullet(Entity):
	color = 255, 127, 127
	size = 2
	def __init__(self, pos, vel):
		self.x, self.y = pos
		self.vx, self.vy = vel
	
@Lifetime(0.5)
@Grows(growthrate = 80)
@Circular()
class Explosion(Entity):
	color = 0, 0, 127
	def __init__(self, pos):
		self.x, self.y = pos


class Gamestate:
	def __init__(self):
		self.stage = 0
		self.deaths = 0
		self.hudfont = pygame.font.Font(None, 30)
		self.restart()
	def restart(self):
		self.player = Player()
		# Entities that interact with each other
		self.objects = [self.player] + [Asteroid(3) for _ in range(self.stage + 2)]
		# Non-interacting entities, i.e. graphical effects (explosions)
		self.effects = []
		self.ufospawntime = 0
		self.ufospawnperiod = 30.0 * 0.9 ** self.stage
		self.restarting = False
		self.restarttime = 0
	def control(self, keys):
		if self.player.alive:
			self.player.control(keys)
	def think(self, dt):
		self.ufospawntime += dt
		if not self.restarting and self.ufospawntime > self.ufospawnperiod:
			self.ufospawntime = 0
			self.objects.append(Ufo())

		for entity in self.objects + self.effects:
			entity.think(dt)

		# The collision logic is: any two objects will collide if they're of different types. So
		# bullets don't collide with other bullets, asteroids don't collide with other asteroids.
		for i in range(len(self.objects)):
			for j in range(i):
				obj0, obj1 = self.objects[i], self.objects[j]
				if type(obj0) is type(obj1):
					continue
				# Treat all objects as circular for the purpose of collision detection.
				# Miss the case where the objects are near opposite edges, close enough to collide
				# if you count screen wrap. It's not very noticeable so don't worry about it.
				if math.dist((obj0.x, obj0.y), (obj1.x, obj1.y)) < obj0.size + obj1.size:
					obj0.collide()
					obj1.collide()

		self.objects = [obj for obj in self.objects if obj.alive]
		self.effects = [effect for effect in self.effects if effect.alive]
		
		if self.restarting:
			self.restarttime += dt
			if self.restarttime > 2:
				self.restart()
		elif not any(isinstance(obj, Asteroid) for obj in self.objects):  # Win condition
			self.stage += 1
			self.restarting = True
		elif not self.player.alive:  # Lose condition
			self.deaths += 1
			self.restarting = True
	def draw(self, surf):
		surf.fill((0, 0, 0))
		for entity in self.objects + self.effects:
			entity.draw(surf)
		hudcolor = 255, 255, 0
		surf.blit(self.hudfont.render("Stage: %d" % self.stage, True, hudcolor), (5, 5))
		surf.blit(self.hudfont.render("Deaths: %d" % self.deaths, True, hudcolor), (5, 30))


pygame.font.init()
screen = pygame.display.set_mode((screensize, screensize))
pygame.display.set_caption("enco Asteroids")
state = Gamestate()
clock = pygame.time.Clock()
def isquit(event):
	return event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)
while not any(isquit(event) for event in pygame.event.get()):
	dt = clock.tick(60) * 0.001
	state.control(pygame.key.get_pressed())
	state.think(dt)
	state.draw(screen)
	pygame.display.flip()

