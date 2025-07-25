#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import random
import time

WIDTH = 400
HEIGHT = 300
HEAD_COLOR = (10, 169, 103)
SNAKE_COLOR = (60, 179, 113)  # MediumSeaGreen
FONT_COLOR = (205, 92, 92)  # IndianRed
FOOD_COLOR = (205, 92, 92)  # IndianRed
BG_COLOR = (70, 130, 180)     # SteelBlue
SNAKE_LENGTH = 1
SNAKE_SPEED = 5
SNAKE_SIZE = 20
ACCELERATION_FOOD = 5
GAME_OVER_ON_EDGE = False
ACCELERATION_ENABLED = True
ACCELERATION = 2

pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('SnakeGame')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont('Monaco', 25, bold=True)
score_font = pygame.font.SysFont('Monaco', 25, bold=True)
speed_font = pygame.font.SysFont('Monaco', 25, bold=True)
time_font = pygame.font.SysFont('Monaco', 25, bold=True)


class Snake:
    def __init__(self):
        self.length = SNAKE_LENGTH
        self.size = SNAKE_SIZE
        self.speed = SNAKE_SPEED
        self.x = WIDTH // 2 // SNAKE_SIZE * SNAKE_SIZE
        self.y = HEIGHT // 2 // SNAKE_SIZE * SNAKE_SIZE
        self.body = [[self.x, self.y]]
        self.way = None     # 'left', 'right', 'up', 'down'
        self.lock = False

    def get_head(self):
        return [self.x, self.y]

    def set_direction(self, direction):
        # Validate direction
        if direction not in ['left', 'right', 'up', 'down']:
            return False
        # Lock opposite direction
        if self.lock:
            return False
        if direction in ['left', 'right'] and self.way in ['left', 'right']:
            return False
        if direction in ['up', 'down'] and self.way in ['up', 'down']:
            return False
        self.way = direction
        self.lock = True
        return True

    def move(self):
        # Unlock opposite direction
        if self.lock:
            self.lock = False
        # Move head
        if self.way == 'left':
            self.x -= self.size
        elif self.way == 'right':
            self.x += self.size
        elif self.way == 'up':
            self.y -= self.size
        elif self.way == 'down':
            self.y += self.size
        # Game over if hit itself
        if [self.x, self.y] in self.body[:-1]:
            return False
        if GAME_OVER_ON_EDGE:
            # Game over if hit the edge
            if self.x >= WIDTH or self.x < 0 or self.y >= HEIGHT or self.y < 0:
                return False
        else:
            if self.x >= WIDTH:
                self.x = 0
            elif self.x < 0:
                self.x = WIDTH - self.size
            if self.y >= HEIGHT:
                self.y = 0
            elif self.y < 0:
                self.y = HEIGHT - self.size
        self.body.append([self.x, self.y])
        if len(self.body) > self.length:
            del self.body[0]
        return True

class Food:
    def __init__(self, snake):
        self.size = SNAKE_SIZE
        self.x, self.y = self.create(snake)

    def create(self, snake):
        # Create food at random position (not on snake body)
        while True:
            food_x = round(random.randrange(0, WIDTH - self.size) / self.size) * self.size
            food_y = round(random.randrange(0, HEIGHT - self.size) / self.size) * self.size
            if [food_x, food_y] not in snake.body:
                return food_x, food_y

class Game:
    def __init__(self):
        self.started = False
        self.pause = False
        self.over = False
        self.quit = False
        self.repeat = False
        # Acceleration
        self.acceleration = 0
        # Timers
        self.start_time = None
        self.pause_time = 0
        self.paused_sum = 0

    def snake_move(self, snake, foot):
        x, y = snake.move()

    def draw_snake(self, snake):
        for b in snake.body[:-1]:
            pygame.draw.rect(display, SNAKE_COLOR, [b[0], b[1], snake.size, snake.size])
        pygame.draw.rect(display, HEAD_COLOR, [snake.body[-1][0], snake.body[-1][1], snake.size, snake.size])

    def draw_food(self, food):
        pygame.draw.rect(display, FOOD_COLOR, [food.x, food.y, food.size, food.size])

    def draw_message(self, text, color):
        lines = text.split('\n')
        y_offset = 0
        for line in lines:
            msg = font_style.render(line, False, color)
            text_rect = msg.get_rect(center=(WIDTH / 2, HEIGHT / 3 + y_offset))
            display.blit(msg, text_rect)
            y_offset += font_style.get_height()

    def draw_speed(self, speed):
        txt = f'{speed:.2f}' if speed % 1 else str(int(speed))
        value = speed_font.render(txt, False, FONT_COLOR)
        text_rect = value.get_rect()
        text_rect.topleft = (10, 10)
        display.blit(value, text_rect)

    def draw_score(self, snake):
        score = snake.length - 1
        value = score_font.render(str(score), False, SNAKE_COLOR) 
        text_rect = value.get_rect()
        text_rect.topright = (WIDTH - 10, 10)
        display.blit(value, text_rect)

    def draw_time(self):
        seconds = int(time.monotonic() - self.start_time - self.paused_sum)
        if seconds < 0:
            seconds = 0
        minutes = seconds // 60
        seconds = seconds % 60
        time_str = f'{minutes}:{seconds:02d}'
        value = time_font.render(time_str, False, FONT_COLOR)
        text_rect = value.get_rect(center=(WIDTH // 2, 10))
        display.blit(value, text_rect)

    def draw_overlay(self, color, alpha):
        overlay_width, overlay_height = WIDTH // 2, HEIGHT // 4
        overlay_x, overlay_y = (WIDTH - overlay_width) // 2, (HEIGHT - overlay_height) // 2
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        display.blit(overlay, (overlay_x, overlay_y))

def main():
    game = Game()
    snake = Snake()
    food = Food(snake)
    while not game.quit:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                change_direction = False
                if event.key == pygame.K_a:
                    change_direction = snake.set_direction('left')
                elif event.key == pygame.K_d:
                    change_direction = snake.set_direction('right')
                elif event.key == pygame.K_w:
                    change_direction = snake.set_direction('up')
                elif event.key == pygame.K_s:
                    change_direction = snake.set_direction('down')
                # On start
                if change_direction and not game.started:
                    game.start_time = time.monotonic()
                    game.started = True
                # Pause
                if event.key == pygame.K_SPACE:
                    game.pause = not game.pause
                    if game.pause:
                        game.pause_time = time.monotonic()
                    else:
                        game.paused_sum += time.monotonic() - game.pause_time
            # Quit
            if event.type == pygame.QUIT:
                game.quit = True
                break
        # Acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and snake.way == 'left':
            game.acceleration += 1
        elif keys[pygame.K_d] and snake.way == 'right':
            game.acceleration += 1
        elif keys[pygame.K_w] and snake.way == 'up':
            game.acceleration += 1
        elif keys[pygame.K_s] and snake.way == 'down':
            game.acceleration += 1
        else:
            game.acceleration = 0
        if ACCELERATION_ENABLED and game.acceleration > 2:
            acceleration = ACCELERATION
        else:
            acceleration = 1
        if not game.pause and not game.over:
            # Move
            if not snake.move():
                game.over = True
            # Get score
            if snake.x == food.x and snake.y == food.y:
                food = Food(snake)
                snake.length += 1
                if ACCELERATION_FOOD > 0 and (snake.length - 1) % ACCELERATION_FOOD == 0:
                    snake.speed += 1
            display.fill(BG_COLOR)
            game.draw_food(food)
            game.draw_snake(snake)
            game.draw_score(snake)
            game.draw_speed(snake.speed * acceleration)
            if game.started:
                game.draw_time()
            pygame.display.update()
            clock.tick(snake.speed * acceleration)

        if game.pause:
            game.draw_overlay(BG_COLOR, 128)
            game.draw_message("Pause\nPress Space to Continue", FONT_COLOR)
            pygame.display.update()

        if game.over:
            total_seconds = int(time.monotonic() - game.start_time - game.paused_sum)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            print(f"Game over! Time: {minutes}:{seconds:02d}, Score: {snake.length - 1}")
            game.draw_overlay(BG_COLOR, 128)
            game.draw_message("GAME OVER\n\nPress Q to Quit\nor R to Retry", FONT_COLOR)
            pygame.display.update()
            game.repeat = None
            while game.repeat is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game.repeat = False
                        game.quit = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            game.repeat = False
                            game.quit = True
                        if event.key == pygame.K_r:
                            game.repeat = True
                            game.quit = True
    if game.repeat:
        main()
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
