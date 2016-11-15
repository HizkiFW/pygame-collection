"""
Python Pygame Test Game
Copyright HizkFW
"""

import os
import sys
import math
import random
import pygame as pg

SCREEN_SIZE = (1280, 720)
TRANSPARENT = (0, 0, 0, 0)
DIRECTION = {
	pg.K_LEFT: (-1, 0),
	pg.K_RIGHT: (1, 0)
}

class Obstacle(object):
	SIZE = (10, 10)
	def __init__(self, pos, direction, speed):
		self.rect = pg.Rect((0, 0), Obstacle.SIZE)
		self.rect.center = pos
		self.speed = speed
		self.image = self.make_image()
		self.direction = direction
		self.has_collided = True
		
	def make_image(self):
		image = pg.Surface(self.rect.size).convert_alpha()
		image.fill(TRANSPARENT)
		image_rect = image.get_rect()
		pg.draw.rect(image, pg.Color("red"), pg.Rect((0, 0), Obstacle.SIZE))
		return image

	def update(self):
		self.rect.y += self.direction * self.speed

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Player(object):
	SIZE = (50, 50)
	
	def __init__(self, pos, speed):
		self.rect = pg.Rect((0, 0), Player.SIZE)
		self.rect.center = pos
		self.speed = speed
		self.acceleration = 0
		self.max_health = 100
		self.health = self.max_health
		self.dead = False
		self.image = self.make_image()
		self.explosion = Explosion(pos, 36, 5, 5)

	def make_image(self):
		image = pg.Surface(self.rect.size).convert_alpha()
		image.fill(pg.Color("red"))
		image_rect = image.get_rect()
		pg.draw.rect(image, pg.Color("white"), pg.Rect((0, Player.SIZE[1] - ((float(self.health)/float(self.max_health))*Player.SIZE[1])), Player.SIZE))
		return image

	def setHealth(self, amount):
		self.health = amount
		if self.health <= 0:
			self.dead = True
		elif self.health > self.max_health:
			self.health = self.max_health
		self.image = self.make_image()		

	def update(self, keys, screen_rect):
		for key in DIRECTION:
			if keys[key]:
				self.acceleration += DIRECTION[key][0]*self.speed
		if self.acceleration > 0:
			self.acceleration -= 1
		elif self.acceleration < 0:
			self.acceleration += 1

		if not self.dead:
			self.rect.x += self.acceleration

		self.rect.clamp_ip(screen_rect)

		if self.dead:
			self.explosion.update()
		
	def draw(self, surface):
		surface.blit(self.image, self.rect)
		self.explosion.draw(surface)

class Particle(object):
	def __init__(self, pos, size, velocity, deceleration, decay):
		self.pos = pos
		self.size = size
		self.opacity = 255
		self.vel = velocity
		self.dec = deceleration
		self.dcy = decay

		self.rect = pg.Rect((0, 0), (int(self.size), int(self.size)))
		self.rect.center = pos

	def make_image(self):
		image = pg.Surface(self.rect.size).convert_alpha()
		image.fill((255, 0, 0, int(self.opacity)))
		return image

	def update(self):
		#self.size -= self.dcy
		self.opacity -= self.dcy
		#self.rect = pg.Rect((0, 0), (int(self.size), int(self.size)))
		#self.rect.center = self.pos
		
		vx = self.vel[0] - self.dec if self.vel[0] > 0 else (self.vel[0] + self.dec if self.vel[0] < 0 else self.vel[0])
		vy = self.vel[1] - self.dec if self.vel[1] > 0 else (self.vel[1] + self.dec if self.vel[1] < 0 else self.vel[1])
		
		self.vel = (vx, vy)
		self.rect.x += self.vel[0]
		self.rect.y += self.vel[1]

	def draw(self, surface):
		surface.blit(self.make_image(), self.rect)

class Explosion(object):
	def __init__(self, pos, particles, power, psize):
		self.rect = pg.Rect((0, 0), (power, power))
		self.rect.center = pos
		self.particles = list()
		for i in range(particles):
			angle = (float(i) / float(particles)) * math.pi * 2

			vx = power * math.cos(angle)
			vy = power * math.sin(angle)
			self.particles.append(Particle(pos, psize, (vx, vy), (1.0/power), 0.1))

	def update(self):
		for p in self.particles:
			p.update()

	def draw(self, surface):
		for p in self.particles:
			p.draw(surface)

class App(object):
	def __init__(self):
		self.screen = pg.display.get_surface()
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.fps = 60
		self.done = False
		self.keys = pg.key.get_pressed()
		self.player = Player(self.screen_rect.center, 2)
		self.obstacles = list()
		self.spawn_interval = 0.1
		self.regen_interval = 1
		self.spawn_counter = self.spawn_interval * self.fps
		self.regen_counter = self.regen_interval * self.fps

	def spawn_obstacle(self, speed):
		pos = random.randrange(0, SCREEN_SIZE[0])
		dir = 1 if random.random() > 0.5 else -1
		y = 0 if dir > 0 else SCREEN_SIZE[1]
		obs = Obstacle((pos, y), dir, speed)
		self.obstacles.append(obs)

	def check_collision(self):
		for o in self.obstacles:
			if o.rect.colliderect(self.player.rect):
				o.has_collided = True
				self.obstacles.remove(o)
				self.player.setHealth(self.player.health - 10)

	def event_loop(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.done = True
			elif event.type in (pg.KEYUP, pg.KEYDOWN):
				self.keys = pg.key.get_pressed()

	def render(self):
		self.screen.fill(pg.Color("black"))
		self.player.draw(self.screen)
		for o in self.obstacles:
			o.draw(self.screen)
		pg.display.update()

	def main_loop(self):
		while not self.done:
			self.event_loop()
			self.player.update(self.keys, self.screen_rect)
			for o in self.obstacles:
				o.update()
				self.check_collision()
				if o.rect.y < -10 or o.rect.y > SCREEN_SIZE[1] + 10:
					self.obstacles.remove(o)

			self.spawn_counter -= 1
			self.regen_counter -= 1
			if self.spawn_counter < 1:
				self.spawn_obstacle(10)
				self.spawn_counter = self.spawn_interval * self.fps
			if self.regen_counter < 1:
				self.player.setHealth(self.player.health + 1)
				self.regen_counter = self.regen_interval * self.fps
			
			self.render()
			self.clock.tick(self.fps)

def main():
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption("Test Game")
	pg.display.set_mode(SCREEN_SIZE)
	App().main_loop()
	pg.quit()
	sys.exit()

if __name__ == "__main__":
	main()
