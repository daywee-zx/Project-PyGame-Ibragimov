import os
import sys

import pygame
import thorpy


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


def load_level(filename):
    filename = "data/" + filename

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global key, door
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                walls_group.add(Tile('wall', x, y))
            elif level[y][x] == '$':
                walls_group.add(Tile('grass', x, y))
            elif level[y][x] == '[':
                Tile('empty', x, y)
                door = Door('door', x, y)
            elif level[y][x] == 'k':
                Tile('empty', x, y)
                key = Key('key', x, y)
            elif level[y][x] == '^':
                Tile('empty', x, y)
                Trap('spikes', x, y)
            elif level[y][x] == '>':
                Tile('empty', x, y)
                hidden_traps_group.add(HiddenTrap('spikes', x, y))
            elif level[y][x] == '!':
                Tile('empty', x, y)
                flag_group.add(Flag('flag', x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def win_screen(screen, w, h, level):
    if level != '8':
        intro_text = ["Отличная работа!",
                      "Нажми Enter, чтобы перейти на следующий уровень",
                      "Нажми Escape, чтобы выйти из игры"]
    else:
        intro_text = ["Поздравляю! Вы закончили этот шедевр геймдева",
                      "Нажми Escape, чтобы выйти и больше не возвращаться"]
    fon = pygame.transform.scale(load_image('nothing.png'), (w, h))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def terminate():
    pygame.quit()
    sys.exit()


# Класс ловушки
class Trap(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, traps_group)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 25))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y + 25)


class HiddenTrap(Trap):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 25))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y + 25)

        self.hidden_flag = False
        self.hide_count = 1

    def hide(self):
        self.hide_count += 1
        if self.hide_count == FPS * 2:
            self.rect.y += 1000
        elif self.hide_count == FPS * 3:
            self.rect.y -= 1000
            self.hide_count = 1


# Класс клетки
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Door(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, walls_group, doors_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def check_open(self):
        if player.key:
            self.kill()
            return True
        return False


class Key(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, key_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def check_if_player_has_the_key(self):
        if pygame.sprite.spritecollideany(player, key_group):
            player.key = True
            self.kill()


# Класс флага
class Flag(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.start_x = tile_width * pos_x
        self.start_y = tile_height * pos_y
        self.idle_count_flag = True
        self.idle_flag = False
        self.flag_looking_left = True
        self.key = False
        self.idle_count = 1
        self.running_count = 1

    def check_death_collide(self):
        if pygame.sprite.spritecollideany(self, traps_group):
            return True
        return False

    def check_win_collide(self):
        if pygame.sprite.spritecollideany(self, flag_group):
            return True
        return False

    def no_anim(self):
        self.image = load_image('hero.png', colorkey=-1)

    # Анимация бездействия
    def idle_animation(self):
        self.running_count = 1

        if not self.idle_count_flag:
            self.idle_count = 1
        self.idle_count += 1
        if not self.idle_flag and self.idle_count == FPS * 2:
            self.idle_count = 1
            self.idle_flag = True
        if self.idle_flag:
            if self.idle_count == FPS * 1:
                if self.flag_looking_left:
                    self.image = load_image(
                        'hero_looking_left.png', colorkey=-1)
                    self.flag_looking_left = False
                else:
                    self.image = load_image(
                        'hero_looking_right.png', colorkey=-1)
                    self.flag_looking_left = True
                self.idle_count = 1

    # Конец анимации бездействия
    def end_idle_animation(self):
        self.idle_flag = False
        self.idle_count_flag = False
        self.flag_looking_left = True

    # Анимация бега
    def running(self, direct):
        self.running_count += 1
        if self.running_count == 2:
            if direct == 'left':
                self.image = load_image('hero_running_left1.png', colorkey=-1)
            elif direct == 'right':
                self.image = load_image('hero_running_right1.png', colorkey=-1)
        if self.running_count == 15:
            if direct == 'left':
                self.image = load_image('hero_running_left2.png', colorkey=-1)
            elif direct == 'right':
                self.image = load_image('hero_running_right2.png', colorkey=-1)
        if self.running_count == 30:
            if direct == 'left':
                self.image = load_image('hero_running_left3.png', colorkey=-1)
            elif direct == 'right':
                self.image = load_image('hero_running_right3.png', colorkey=-1)
        if self.running_count == 45:
            if direct == 'left':
                self.image = load_image('hero_running_left4.png', colorkey=-1)
            elif direct == 'right':
                self.image = load_image('hero_running_right4.png', colorkey=-1)
        if self.running_count == 60:
            self.running_count = 1
            if direct == 'left':
                self.image = load_image('hero_running_left1.png', colorkey=-1)
            elif direct == 'right':
                self.image = load_image('hero_running_right1.png', colorkey=-1)


# Функция для работы меню в начале
def launch_menu(choices):
    title = thorpy.make_text("Выбери уровень", 14, (0, 0, 0))

    def at_press(what):
        global picked_level
        picked_level = what
        thorpy.functions.quit_menu_func()

    elements = []
    for text in choices:
        element1 = thorpy.make_button(text, func=at_press)
        element1.user_params = {"what": text}
        elements.append(element1)
    box1 = thorpy.Box([title] + elements)
    box1.set_main_color((200, 200, 200, 150))
    box1.center()
    m = thorpy.Menu(box1)
    m.play()


if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Not Meat Boy')
    screen.fill('blue')

    # Флаги, связанные с запуском уровня
    picked_level = None
    level_has_started = False
    level_has_just_ended = False
    start_next_level = False

    # Интерфейс с thorpy
    exit_button = thorpy.make_button('Выход', thorpy.functions.quit_func)
    choices = [str(i + 1) for i in range(8)]
    button = thorpy.make_button("Начать игру", launch_menu,
                                {"choices": choices})
    box = thorpy.Box(elements=[button, exit_button])
    box.center()
    menu = thorpy.Menu(box)

    for element in menu.get_population():
        element.surface = screen

    box.set_topleft((197, 208))
    box.blit()
    box.update()

    clock = pygame.time.Clock()
    FPS = 60

    tile_images = {
        'wall': load_image('ground.png'),
        'empty': load_image('nothing.png'),
        'door': load_image('door.png', colorkey=-1),
        'key': load_image('key.png', colorkey=-1),
        'spikes': load_image('spikes.png', colorkey=-1),
        'flag': load_image('flag.png', colorkey=-1),
        'grass': load_image('grass.png')
    }
    player_image = load_image('hero.png', colorkey=-1)

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    key_group = pygame.sprite.Group()
    doors_group = pygame.sprite.Group()
    traps_group = pygame.sprite.Group()
    flag_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    hidden_traps_group = pygame.sprite.Group()

    tile_width = tile_height = 50

    # Флаги движения
    moving_up = False
    moving_right = False
    moving_left = False
    direction = None
    # Флаги прыжка и нахождения в падении
    jump = False
    falling = False
    # Флаги запущенной инерции в ту или иную сторону
    right_inertia = False
    left_inertia = False
    # Флаг стартового экрана
    start_screen_flag = True
    jump_count = 1
    left_count = 1
    right_count = 1

    running = True
    running_menu = True
    stop_flag = False

    # door и key, не попадающие в кадр. Сделано, чтобы не было ошибки pycharm
    door = Door('door', 100000, 100000)
    key = Key('key', 100000, 10000000)

    player = Player(100000, 100000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.KEYDOWN:
                start_screen_flag = False
                if event.key == pygame.K_LEFT:
                    moving_left = True
                    direction = 'left'
                if event.key == pygame.K_RIGHT:
                    moving_right = True
                    direction = 'right'
                if event.key == pygame.K_UP:
                    moving_up = True
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if level_has_just_ended:
                    if event.key == pygame.K_RETURN:
                        start_next_level = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    moving_left = False
                    left_inertia = True
                    player.no_anim()
                if event.key == pygame.K_RIGHT:
                    moving_right = False
                    right_inertia = True
                    player.no_anim()
                if event.key == pygame.K_UP:
                    moving_up = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_screen_flag = False

            menu.react(event)

        # Начало СЛЕДУЮЩЕГО уровня
        if start_next_level:
            picked_level = str(int(picked_level) + 1)
            if picked_level != '8':
                all_sprites = pygame.sprite.Group()
                tiles_group = pygame.sprite.Group()
                walls_group = pygame.sprite.Group()
                key_group = pygame.sprite.Group()
                doors_group = pygame.sprite.Group()
                traps_group = pygame.sprite.Group()
                flag_group = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                hidden_traps_group = pygame.sprite.Group()

                player, level_x, level_y = generate_level(load_level(
                    f'{picked_level} level.txt'))
                size = width, height = (level_x + 1) * 50, (level_y + 1) * 50
                pygame.display.set_mode(size)
                all_sprites.draw(screen)

                start_next_level = False
                level_has_started = True
                level_has_just_ended = False

        # Начало уровня
        if picked_level is not None and not level_has_started:
            player, level_x, level_y = generate_level(load_level(
                f'{picked_level} level.txt'))
            size = width, height = (level_x + 1) * 50, (level_y + 1) * 50
            pygame.display.set_mode(size)
            all_sprites.draw(screen)
            level_has_started = True

        if level_has_started:
            # Инициализация прыжка
            if moving_up and not jump and not falling:
                jump = True
                jump_count = 1
                moving_up = False

            # Движение
            if not pygame.sprite.spritecollideany(player, walls_group):
                if moving_right:
                    player.rect.x += 5
                if moving_left:
                    player.rect.x -= 5
                if moving_left or moving_right:
                    player.running(direction)

            # Инерция при остановке
            if right_inertia:
                if right_count <= 5:
                    right_count += 1
                    player.rect.x += 5
                    if pygame.sprite.spritecollideany(player, walls_group):
                        player.rect.x -= 5

                if right_count == 5:
                    right_count = 1
                    right_inertia = False

            if left_inertia:
                if left_count <= 5:
                    left_count += 1
                    player.rect.x -= 5
                    if pygame.sprite.spritecollideany(player, walls_group):
                        player.rect.x += 5

                if left_count == 5:
                    left_count = 1
                    left_inertia = False

            # Проверка коллизии - сначала по бокам, потом коллизия снизу
            if pygame.sprite.spritecollideany(player, walls_group):
                if pygame.sprite.spritecollideany(player, doors_group):
                    if door.check_open():
                        door.kill()
                    else:
                        player.rect.x += 5
                        if pygame.sprite.spritecollideany(player, walls_group):
                            player.rect.x -= 10
                else:
                    player.rect.x += 5
                    if pygame.sprite.spritecollideany(player, walls_group):
                        player.rect.x -= 10
                    if jump and pygame.sprite.spritecollideany(player,
                                                               walls_group):
                        player.rect.y += 5
                        player.rect.x += 5
                        jump = False
                        jumped = False
                    elif pygame.sprite.spritecollideany(player, walls_group):
                        player.rect.y -= 5

            # Имитация гравитации
            player.rect.y += 5
            if pygame.sprite.spritecollideany(player, walls_group):
                falling = False
                player.rect.y -= 5
            else:
                falling = True

            # Прыжок
            if jump:
                staying_in_air = False
                if jump_count <= 17:
                    if not staying_in_air:
                        player.rect.y -= 10
                    jump_count += 1
                    if 14 <= jump_count < 17:
                        staying_in_air = True
                    if jump_count == 17:
                        jump = False

            # Запуск и остановка анимации бездействия
            if moving_right or moving_left or moving_up or jump:
                player.end_idle_animation()
            if not moving_left and not moving_right and \
                    not moving_up and not jump:
                player.idle_count_flag = True
                player.idle_animation()

            # "Анимация" двигающихся шипов
            for i in hidden_traps_group.sprites():
                i.hide()

            if key is not None:
                key.check_if_player_has_the_key()

            # Проверка на смерть, если игрок погиб - сброс всего уровня
            if player.check_death_collide():
                all_sprites = pygame.sprite.Group()
                tiles_group = pygame.sprite.Group()
                walls_group = pygame.sprite.Group()
                key_group = pygame.sprite.Group()
                doors_group = pygame.sprite.Group()
                traps_group = pygame.sprite.Group()
                flag_group = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                hidden_traps_group = pygame.sprite.Group()

                player, level_x, level_y = generate_level(load_level(
                    f'{picked_level} level.txt'))
                all_sprites.draw(screen)

            # Проверка конца уровня
            if player.check_win_collide() or level_has_just_ended:
                all_sprites = pygame.sprite.Group()
                tiles_group = pygame.sprite.Group()
                walls_group = pygame.sprite.Group()
                key_group = pygame.sprite.Group()
                doors_group = pygame.sprite.Group()
                traps_group = pygame.sprite.Group()
                flag_group = pygame.sprite.Group()
                player_group = pygame.sprite.Group()

                win_screen(screen, width, height, picked_level)

                level_has_just_ended = True
                level_has_started = False

            tiles_group.draw(screen)
            player_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
