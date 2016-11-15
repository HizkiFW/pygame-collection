import os
import sys
import random
import pygame as pg

SCREEN_SIZE = (1280, 720)
PADMARGIN = 50
PADSIZE = (10, 100)
PADSPEED = 5

BALL_SPEED = 5

PL = "PLAYER_LEFT"
PR = "PLAYER_RIGHT"
UP = 1
DN = -1

CONTROLS = {
	PL: {
		UP: pg.K_w,
		DN: pg.K_s
	},
	PR: {
		UP: pg.K_UP,
		DN: pg.K_DOWN
	}
}
DIRS = (
	(-1, -1),
	(-1,  1),
	( 1, -1),
	( 1,  1)
)

WHITE = pg.Color("white")
BLACK = pg.Color("black")

class Paddle(object):
	def __init__(self, pos, size):
		self.rect = pg.Rect((0, 0), size)
		self.rect.center = pos
		self.image = pg.Surface(self.rect.size).convert_alpha()
		self.image.fill(WHITE)
		self.acc = 0

	def update(self, dy, rect):
#		self.acc += dy
#		self.rect.centery += self.acc
#		if self.acc > 0:
#			self.acc -= 1
#		elif self.acc < 0:
#			self.acc += 1
#		else:
#			self.acc = 0

		self.rect.centery += dy

		self.rect.clamp_ip(rect)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Ball(object):
	def __init__(self, pos, size, vel, speed):
		self.rect = pg.Rect((0, 0), (size, size))
		self.rect.center = pos
		self.image = pg.Surface(self.rect.size).convert_alpha()
		self.image.fill(WHITE)
		self.vel = vel
		self.speed = speed

		self.o_pos = pos
		self.o_vel = vel
		self.o_speed = speed

	def update(self, screen_rect, plrect, prrect):
		self.rect.x += self.vel[0] * self.speed
		self.rect.y += self.vel[1] * self.speed

		if self.rect.colliderect(plrect) or self.rect.colliderect(prrect):
			self.vel = (self.vel[0] * -1, self.vel[1])

		if self.rect.y < 0 or self.rect.y > screen_rect.height:
			self.vel = (self.vel[0], self.vel[1] * -1)

	def set(self, pos, vel, speed):
		self.rect.center = pos
		self.vel = vel
		self.speed = speed

	def reset(self):
		self.rect.center = self.o_pos
		self.vel = self.o_vel
		self.speed = self.o_speed

	def reset_rnd(self):
		self.reset()
		self.vel = DIRS[random.randrange(0, 3)]

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class ScoreCounter(object):
	SIZE = (50, 50)

	def __init__(self, pos):
		self.rect = pg.Rect((0, 0), ScoreCounter.SIZE)
		self.rect.center = pos
		self.score = 0
		self.image = self.make_image()

	def set_score(self, score):
		if self.score != score:
			self.score = score
			self.image = self.make_image()

	def add_score(self, score):
		if score != 0:
			self.score += score
			self.image = self.make_image()

	def make_image(self):
		font = pg.font.SysFont("monospace", 36)
		return font.render(str(self.score), 1, WHITE)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class App(object):
	def __init__(self):
		self.screen = pg.display.get_surface()
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.fps = 60
		self.done = False
		self.keys = pg.key.get_pressed()

		self.pl = Paddle((PADMARGIN, self.screen_rect.center[1]), PADSIZE)
		self.pr = Paddle((self.screen_rect.width - PADMARGIN, self.screen_rect.center[1]), PADSIZE)

		self.sl = ScoreCounter((50, 50))
		self.sr = ScoreCounter((self.screen_rect.width - 50, 50))

		self.ball = Ball(self.screen_rect.center, 5, (1, 1), BALL_SPEED)
		#self.ball2 = Ball(self.screen_rect.center, 5, (-1, 1), 7)
		#self.ball3 = Ball(self.screen_rect.center, 5, (1, -1), 10)


	def event_loop(self):
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
				self.done = True
			elif event.type in (pg.KEYUP, pg.KEYDOWN):
				self.keys = pg.key.get_pressed()

	def render(self):
		self.screen.fill(BLACK)

		self.pl.draw(self.screen)
		self.pr.draw(self.screen)

		self.sl.draw(self.screen)
		self.sr.draw(self.screen)

		self.ball.draw(self.screen)
		#self.ball2.draw(self.screen)
		#self.ball3.draw(self.screen)

		pg.display.update()

	def check_collision(self, ball):
		if ball.rect.x < 0:
			self.sr.add_score(1)
			ball.reset_rnd()
		elif ball.rect.x > self.screen_rect.width:
			self.sl.add_score(1)
			ball.reset_rnd()

	def main_loop(self):
		while not self.done:
			self.event_loop()

			if self.keys[CONTROLS[PL][UP]]: self.pl.update(-PADSPEED, self.screen_rect)
			if self.keys[CONTROLS[PL][DN]]: self.pl.update(PADSPEED, self.screen_rect)

			if self.keys[CONTROLS[PR][UP]]: self.pr.update(-PADSPEED, self.screen_rect)
			if self.keys[CONTROLS[PR][DN]]: self.pr.update(PADSPEED, self.screen_rect)

			self.ball.update(self.screen_rect, self.pl.rect, self.pr.rect)
			#self.ball2.update(self.screen_rect, self.pl.rect, self.pr.rect)
			#self.ball3.update(self.screen_rect, self.pl.rect, self.pr.rect)

			self.check_collision(self.ball)
			#self.check_collision(self.ball2)
			#self.check_collision(self.ball3)

			self.render()
			self.clock.tick(self.fps)

def main():
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption("PONG")
	pg.display.set_mode(SCREEN_SIZE)
	App().main_loop()
	pg.quit()
	sys.exit()

if __name__ == "__main__":
	main()
