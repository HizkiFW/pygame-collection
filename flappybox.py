import os
import sys
import random
import pygame as pg

SCREEN_SIZE = (640, 360)

TRANSPARENT = (0, 0, 0, 0)
TRIGGER = pg.K_SPACE
GRAVITY = -1
TERMINAL_VELOCITY = -10

class Box(object):
	"""
	This class defines the main player box.
	"""
	SIZE = (50, 50)
	COLOR = pg.Color("yellow")

	def __init__(self, pos):
		self.rect = pg.Rect((0, 0), Box.SIZE)
		self.rect.center = pos
		self.image = self.make_image()
		self.vel = 0

	def make_image(self):
		image = pg.Surface(self.rect.size).convert_alpha()
		image.fill(Box.COLOR)
		return image

	def update(self, trigger, screen_rect):
		if trigger:
			self.vel = 10

		self.rect.y -= self.vel
		self.vel += GRAVITY if self.vel > TERMINAL_VELOCITY else 0

		self.rect.clamp_ip(screen_rect)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Lava(object):
	"""
	This class defines the ground for the game.
	"""
	def __init__(self, size, ypos):
		self.rect = pg.Rect((0, 0), size)
		self.rect.x = 0
		self.rect.y = ypos - size[1]
		self.image = pg.Surface(self.rect.size).convert_alpha()
		self.image.fill(pg.Color("red"))

	def check_collision(self, rect):
		return self.rect.colliderect(rect)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Pipe(object):
	"""
	This class defines a single pipe object, not a pair of pipes.
	"""
	SIZE = (50, 300)
	COLOR = pg.Color("green")

	def __init__(self, pos, speed):
		self.rect = pg.Rect((0, 0), Pipe.SIZE)
		self.rect.center = pos
		self.speed = speed
		self.image = self.make_image() #Could be optimized
		self.is_outside = False

	def make_image(self):
		image = pg.Surface(self.rect.size).convert_alpha()
		image.fill(Pipe.COLOR)
		return image

	def update(self):
		self.rect.x -= self.speed
		if self.rect.x < -10:
			self.is_outside = True

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class PipeObstacle(object):
	"""
	This class defines the pipe pair obstacle.
	"""
	def __init__(self, pos, speed):
		self.pipe_top = Pipe((pos[0], pos[1]+250), speed)
		self.pipe_bot = Pipe((pos[0], pos[1]-250), speed)
		self.x = pos[0]
		self.is_outside = False
		self.score_added = False
		self.has_collided = False

	def check_collision(self, rect):
		if rect.colliderect(self.pipe_top.rect) or rect.colliderect(self.pipe_bot.rect):
			self.has_collided = True
			return True

		return False

	def update(self):
		self.pipe_top.update()
		self.pipe_bot.update()
		self.x = self.pipe_top.rect.x
		self.is_outside = self.pipe_top.is_outside and self.pipe_bot.is_outside

	def draw(self, surface):
		self.pipe_top.draw(surface)
		self.pipe_bot.draw(surface)

class ScoreCounter(object):
	"""
	This class defines the score counter
	"""
	COLOR = pg.Color("black")
	def __init__(self, pos):
		self.pos = pos
		self.size = (50, 50)
		self.rect = pg.Rect((0, 0), self.size)
		self.rect.center = pos
		self.last_text = "0"
		self.image = self.make_image(self.last_text)

	def make_image(self, text):
		font = pg.font.SysFont("monospace", 15)
		#self.size = pg.font.size(text)
		#self.rect = pg.Rect((0, 0), self.size)
		#self.rect.center = self.pos

		image = font.render(text, 1, ScoreCounter.COLOR)
		return image

	def update(self, text):
		if text != self.last_text:
			self.image = self.make_image(text)
			self.last_text = text

	def draw(self, surface):
		surface.blit(self.image, self.rect)
		

class App(object):
	"""
	This class does the things
	"""
	PIPE_INTERVAL = 1
	PIPE_SPEED = 5
	def __init__(self):
		self.screen = pg.display.get_surface()
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.fps = 60
		self.done = False
		self.keys = pg.key.get_pressed()

		self.game_started = False

		self.player = Box(self.screen_rect.center)

		self.score = 0
		self.score_counter = ScoreCounter((self.screen_rect.center[0], 50))

		self.pipe_countdown = App.PIPE_INTERVAL * self.fps
		self.pipes = list()

		self.lava = Lava((self.screen_rect.width, 10), self.screen_rect.height)

	def event_loop(self):
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
				self.done = True
			elif event.type in (pg.KEYUP, pg.KEYDOWN):
				self.keys = pg.key.get_pressed()
				if self.keys[TRIGGER]:
					self.game_started = True

	def render(self):
		self.screen.fill(pg.Color("lightblue"))
		for p in self.pipes:
			p.draw(self.screen)
		self.player.draw(self.screen)
		self.lava.draw(self.screen)
		self.score_counter.draw(self.screen)
		pg.display.update()

	def game_over(self):
		print("Last score: " + str(self.score))
		self.score = 0
		self.game_started = False
		self.pipes = list()
		self.player.rect.center = self.screen_rect.center

	def main_loop(self):
		while not self.done:
			self.event_loop()

			if self.game_started:
				self.pipe_countdown -= 1
				if self.pipe_countdown < 0:
					op = (self.screen_rect.width, random.randrange(100, self.screen_rect.height-100))
					self.pipes.append(PipeObstacle(op, App.PIPE_SPEED))
					
					self.pipe_countdown = App.PIPE_INTERVAL * self.fps

				for p in self.pipes:
					p.update()
					if p.check_collision(self.player.rect):
						self.game_over()

					if p.x < self.player.rect.center[0]:
						if not p.score_added:
							p.score_added = True
							self.score += 1

					if p.is_outside:
						self.pipes.remove(p)

				self.player.update(self.keys[TRIGGER], self.screen_rect)
				self.score_counter.update(str(self.score))
				if self.lava.check_collision(self.player.rect):
					self.game_over()

			self.render()
			self.clock.tick(self.fps)

def main():
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption("Flappy Box")
	pg.display.set_mode(SCREEN_SIZE)
	App().main_loop()
	pg.quit()
	sys.exit()

if __name__ == "__main__":
	main()
